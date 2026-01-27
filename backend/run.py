import logging
import uuid
import threading
from datetime import datetime
import openai
import json
from flask_cors import CORS
from flask import Flask, request, jsonify, session
from config import get_config
import sys
import io
import os
from pathlib import Path

# Configure stdout and stderr to use UTF-8 encoding for Chinese characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ⚠️ IMPORTANT: Load .env file BEFORE importing config
# config.py reads os.environ at module load time, so we must populate it first
print(f"[Startup] Loading .env file...")
possible_paths = [
    Path(__file__).parent.parent / '.env',  # 从backend上一级目录
    Path(__file__).parent / '.env',  # backend目录下
    Path.cwd() / '.env',  # 当前工作目录
]

env_loaded = False
for env_path in possible_paths:
    print(f"[Startup] Checking for .env at: {env_path}")
    if env_path.exists():
        print(f"[Startup] ✓ .env file found, loading...")
        try:
            with open(env_path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key:
                                os.environ[key] = value
                                print(f"[Startup]   → {key}")
            env_loaded = True
            break
        except Exception as e:
            print(f"[Startup] Error reading .env: {e}")
            continue

if not env_loaded:
    print(f"[Startup] ✗ WARNING: .env file not found in any expected location!")

# NOW import config after .env is loaded


# 获取配置
config = get_config()

# 验证关键配置
print(f"\n[Startup] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"[Startup] Configuration Summary:")
print(f"[Startup] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
openai_model = os.environ.get('OPENAI_MODEL')
openai_base_url = os.environ.get('OPENAI_BASE_URL')
openai_api_key = os.environ.get('OPENAI_API_KEY')
print(f"[Startup]   OPENAI_MODEL: {openai_model or '❌ NOT SET'}")
print(f"[Startup]   OPENAI_BASE_URL: {openai_base_url or '❌ NOT SET'}")
print(
    f"[Startup]   OPENAI_API_KEY: {'✓ SET' if openai_api_key else '❌ NOT SET'}")
print(f"[Startup]   CONVERSATIONS_DIR: {config.CONVERSATIONS_DIR}")
print(f"[Startup] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# 验证必要的配置是否存在
config_errors = []
if not openai_model:
    config_errors.append("OPENAI_MODEL is not set")
if not openai_api_key:
    config_errors.append("OPENAI_API_KEY is not set")
if not openai_base_url:
    config_errors.append("OPENAI_BASE_URL is not set")

if config_errors:
    print(f"[Startup] ❌ CONFIGURATION ERRORS:")
    for error in config_errors:
        print(f"[Startup]    - {error}")
    print(f"[Startup] Please check your .env file at the project root directory.")

# Disable verbose logging for polling requests
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
config.init_app(app)

CORS(app, origins=config.CORS_ORIGINS)

# User state management - store each user's state using username as key
user_states = {}
user_states_lock = threading.Lock()

# Global variable to store case file list for each user
user_case_files = {}


def get_user_state(username):
    """获取或创建用户状态，使用username作为键"""
    with user_states_lock:
        if username not in user_states:
            user_states[username] = {
                'message_history': [],
                'current_case_index': 0,
                'user_dir': None,
                'case_data': None,
                'initialized': False,
                'user_id': None  # 保留user_id用于其他用途
            }
        return user_states[username]


def get_user_case_files(username):
    """获取conversations文件夹下的所有case文件夹"""
    global user_case_files

    if username not in user_case_files:
        # 从conversations文件夹下获取所有case文件夹
        conversations_dir = config.CONVERSATIONS_DIR

        # 获取conversations文件夹下的所有第一层目录（case文件夹）
        if os.path.exists(conversations_dir):
            all_items = os.listdir(conversations_dir)
            # 过滤出是目录且名称为caseX的文件夹
            case_folders = [item for item in all_items
                            if os.path.isdir(os.path.join(conversations_dir, item))
                            and item.startswith('case')]

            # 按数字顺序排序 (case10, case11, etc.)
            case_folders = sorted(case_folders, key=lambda x: int(
                x.replace('case', '')))

            # 构建对应的json文件名列表 (case10.json, case11.json, etc.)
            case_files = [f"{folder}/{folder}.json" for folder in case_folders]

            user_case_files[username] = case_files
            print(f"从conversations文件夹获取的案例文件: {user_case_files[username]}")
        else:
            user_case_files[username] = []
            print(f"警告：conversations文件夹不存在: {conversations_dir}")

    return user_case_files[username]


def load_medical_case(username, case_index):
    """加载指定用户的指定索引的病例文件"""
    case_files = get_user_case_files(username)

    if case_index >= len(case_files):
        print(
            f"错误：案例索引 {case_index} 超出范围，用户 {username} 只有 {len(case_files)} 个案例")
        return None

    # 从conversations文件夹下加载case文件
    conversations_dir = config.CONVERSATIONS_DIR
    case_file_path = os.path.join(conversations_dir, case_files[case_index])

    print(f"尝试加载病例文件: {case_file_path}")

    if not os.path.exists(case_file_path):
        print(f"错误：病例文件不存在: {case_file_path}")
        return None

    try:
        with open(case_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"成功加载病例文件: {case_file_path}")
            return data
    except Exception as e:
        print(f"加载病例文件失败: {case_file_path}, 错误: {str(e)}")
        return None


def get_response(messages):
    """Get AI response from LLM"""
    try:
        # Verify configuration
        if not config.OPENAI_MODEL:
            raise ValueError(
                "OPENAI_MODEL is not configured. Please check your .env file.")
        if not config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not configured. Please check your .env file.")
        if not config.OPENAI_BASE_URL:
            raise ValueError(
                "OPENAI_BASE_URL is not configured. Please check your .env file.")

        # Set API configuration
        openai.api_key = config.OPENAI_API_KEY
        openai.api_base = config.OPENAI_BASE_URL

        print(f"[AI] Calling OpenAI API with model: {config.OPENAI_MODEL}")

        # Create chat completion request
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )

        return response.choices[0].message.content
    except ValueError as ve:
        print(f"[AI] Configuration Error: {str(ve)}")
        return f"Configuration Error: {str(ve)}"
    except Exception as e:
        import traceback
        error_msg = str(e)
        tb = traceback.format_exc()
        print(f"[AI] Error calling LLM API:")
        print(f"[AI]   Error: {error_msg}")
        print(f"[AI]   Traceback:\n{tb}")
        return "AI service is currently unavailable. Please try again later."


def initialize_case(username):
    """Initialize system messages for current case"""
    user_state = get_user_state(username)

    if user_state['case_data'] is None:
        user_state['case_data'] = load_medical_case(
            username, user_state['current_case_index'])

    user_state['message_history'] = []

    exam_content = json.dumps(
        user_state['case_data']["prompt3"], ensure_ascii=False)

    user_state['message_history'].extend([
        {"role": "system", "content": user_state['case_data']["prompt1"]},
        {"role": "system", "content": user_state['case_data']["prompt2"]},
        {"role": "system", "content": exam_content},
        {"role": "system", "content": "IMPORTANT: You MUST respond ONLY in English. Never use Chinese or any other language. All responses must be in English only."}
    ])

    user_state['initialized'] = True


def get_user_dir(username):
    """获取conversations目录（不再为用户创建单独的文件夹）"""
    base_dir = config.CONVERSATIONS_DIR
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 直接返回conversations目录，不再为用户创建子目录
    return base_dir


def get_next_case_index(username):
    """获取用户下一个未完成case的索引

    逻辑：
    1. 遍历所有案例文件夹，检查用户是否有保存的对话记录（文件名为{username}.json）
    2. 返回第一个没有作答过的案例索引（从0开始）
    3. 如果都作答过，返回最后一个案例索引
    """
    # 获取案例文件列表
    case_files = get_user_case_files(username)
    total_cases = len(case_files)

    if total_cases == 0:
        print(f"未找到任何案例文件")
        return 0

    # 统计每个case文件夹中是否有该用户的JSON文件
    conversations_dir = config.CONVERSATIONS_DIR
    completed_case_indices = set()

    # 期望的用户保存文件名
    expected_filename = f"{username}.json"

    for idx, case_file_path in enumerate(case_files):
        # case_files 中的文件名格式为 "case10/case10.json"
        case_folder = case_file_path.split('/')[0]
        case_dir = os.path.join(conversations_dir, case_folder)

        if os.path.exists(case_dir):
            # 精确查找该用户的json文件 (filename == "{username}.json")
            user_file_path = os.path.join(case_dir, expected_filename)
            if os.path.exists(user_file_path):
                completed_case_indices.add(idx)

    # 从索引0开始，找到第一个未完成的案例
    for idx in range(total_cases):
        if idx not in completed_case_indices:
            return idx

    # 如果所有案例都完成了，返回最后一个案例索引
    last_idx = total_cases - 1
    return last_idx


def get_previous_case_index(username):
    """获取用户上一个案例的索引（允许返回任何前面的案例，不仅仅是已完成的）"""
    # 获取案例文件列表
    case_files = get_user_case_files(username)
    total_cases = len(case_files)

    if total_cases == 0:
        print(f"未找到任何案例文件")
        return None

    # 获取当前案例索引
    user_state = get_user_state(username)
    current_index = user_state['current_case_index']

    # 如果当前索引大于0，则返回前一个案例索引
    if current_index > 0:
        previous_index = current_index - 1
        return previous_index
    else:
        return None


@app.route('/get-ai-response', methods=['POST'])
def get_ai_response():
    """获取AI对用户消息的响应"""
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'default_user')
    username = data.get('username', '')  # 添加username参数

    # 如果没有提供username，尝试从user_id中提取
    if not username:
        # 这里可以根据实际情况调整，暂时使用user_id作为username
        username = user_id

    user_state = get_user_state(username)

    if not user_state['initialized']:
        initialize_case(username)

    # 添加用户消息到历史
    user_state['message_history'].append({
        "role": "user",
        "content": user_message
    })

    try:
        assistant_output = get_response(user_state['message_history'])

        # 添加到对话历史
        user_state['message_history'].append({
            "role": "assistant",
            "content": assistant_output
        })

        return jsonify({
            'status': 'success',
            'reply': assistant_output
        })

    except Exception as e:
        import traceback
        error_info = f"处理请求时出错: {str(e)}"
        print(f"Error: {error_info}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': error_info
        }), 500


@app.route('/api/next-step', methods=['POST'])
def handle_next_step():
    """处理下一个病例的请求"""
    try:
        data = request.json
        next_action = data.get('action', False)
        username = data.get('username', '')
        user_id = data.get('user_id', 'default_user')

        if not username:
            return jsonify({
                'status': 'error',
                'message': '缺少用户名信息'
            }), 400

        user_state = get_user_state(username)

        # 获取下一个未完成的案例索引
        next_case_index = get_next_case_index(username)
        case_files = get_user_case_files(username)
        total_cases = len(case_files)

        # 先清空当前的消息历史，然后更新案例索引
        user_state['message_history'] = []
        user_state['current_case_index'] = next_case_index
        user_state['case_data'] = load_medical_case(username, next_case_index)
        initialize_case(username)

        return jsonify({
            'status': 'success',
            'action': next_action,
            'message': 'Next step processed successfully',
        })

    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': 'Failed to process next step'
        }), 500


@app.route('/api/previous-step', methods=['POST'])
def handle_previous_step():
    """处理上一个病例的请求"""
    try:
        data = request.json
        username = data.get('username', '')
        user_id = data.get('user_id', 'default_user')

        if not username:
            return jsonify({
                'status': 'error',
                'message': '缺少用户名信息'
            }), 400

        user_state = get_user_state(username)

        # 获取上一个案例索引
        previous_case_index = get_previous_case_index(username)

        if previous_case_index is None:
            return jsonify({
                'status': 'error',
                'message': 'Already at the first case'
            }), 400

        print(
            f"用户 {username} 从索引 {user_state['current_case_index']} 跳转到 {previous_case_index}")

        # 清空当前的消息历史，然后更新案例索引
        user_state['message_history'] = []
        user_state['current_case_index'] = previous_case_index
        user_state['case_data'] = load_medical_case(
            username, previous_case_index)
        initialize_case(username)

        return jsonify({
            'status': 'success',
            'message': 'Previous step processed successfully'
        })

    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': 'Failed to process previous step'
        }), 500


def save_message_history(username):
    """保存当前对话历史到JSON文件（过滤掉system消息）"""
    user_state = get_user_state(username)

    if not user_state['message_history']:
        return

    # 过滤掉系统消息
    filtered_history = [
        msg for msg in user_state['message_history'] if msg.get('role') != 'system']

    if not filtered_history:
        return

    # 使用用户名作为文件名，不使用时间戳
    file_name = f"{username}.json"

    # 获取案例文件列表和当前案例索引
    case_files = get_user_case_files(username)
    save_case_index = user_state['current_case_index']

    if save_case_index < len(case_files):
        # case_files 中的文件名格式为 "case10/case10.json"
        case_file_path = case_files[save_case_index]
        # 提取case文件夹名称 (case10)
        case_folder = case_file_path.split('/')[0]
    else:
        case_folder = f"case{save_case_index + 1}"

    # 构建保存路径：直接保存到 conversations/{caseFolder}/ 中
    conversations_dir = config.CONVERSATIONS_DIR
    case_dir = os.path.join(conversations_dir, case_folder)

    # 确保目录存在
    if not os.path.exists(case_dir):
        os.makedirs(case_dir, exist_ok=True)

    file_path = os.path.join(case_dir, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_history, f, ensure_ascii=False, indent=2)
        print(f"已保存过滤后的对话历史到: {file_path}")
    except Exception as e:
        print(f"保存对话历史失败: {str(e)}")


@app.route('/current-case', methods=['GET'])
def get_current_case():
    """获取当前加载的病例信息"""
    user_id = request.args.get('user_id', 'default_user')
    username = request.args.get('username', '')  # 添加username参数

    # 如果没有提供username，尝试从user_id中提取
    if not username:
        username = user_id

    user_state = get_user_state(username)

    try:
        # 获取该用户的案例文件列表
        case_files = get_user_case_files(username)
        case_filename = case_files[user_state['current_case_index']
                                   ] if case_files and user_state['current_case_index'] < len(case_files) else "未找到病例"

        # 创建过滤后的病例数据副本
        filtered_data = {}
        formatted_data = ""  # 初始化formatted_data变量

        if user_state['case_data']:
            for key, value in user_state['case_data'].items():
                if key == "personal_message":
                    filtered_data[key] = value

            # 格式化为可读字符串
            for key, value in filtered_data.items():
                if key == "personal_message":
                    key_display = "Patient Informaition: "
                else:
                    key_display = key.replace("_", " ").title()

                value_display = str(value).replace("\\n", "\n")
                formatted_data += f"{key_display}: {value_display}\n"

        # 获取该用户的案例文件列表
        case_files = get_user_case_files(username)
        total_cases = len(case_files)

        print(
            f"用户 {username} 当前病例索引: {user_state['current_case_index']}, 总案例数: {total_cases}")
        return jsonify({
            'status': 'success',
            'case_index': user_state['current_case_index'],
            'formatted_data': formatted_data,
            'debug_info': {
                'total_cases': total_cases,
                'case_files': case_files,
                'current_case_file': case_files[user_state['current_case_index']] if case_files and user_state['current_case_index'] < len(case_files) else 'N/A'
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取病例信息失败: {str(e)}'
        }), 500


@app.route('/api/get-main-suit', methods=['GET'])
def get_main_suit():
    """获取当前病例的主诉"""
    user_id = request.args.get('user_id', 'default_user')
    username = request.args.get('username', '')  # 添加username参数

    # 如果没有提供username，尝试从user_id中提取
    if not username:
        username = user_id

    user_state = get_user_state(username)

    try:
        # 如果case_data还没有加载，尝试加载
        if user_state['case_data'] is None:
            user_state['case_data'] = load_medical_case(
                username, user_state['current_case_index'])
            if user_state['case_data'] is None:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to load case data for user {username}'
                }), 404

        # 检查是否有main_suit字段
        if 'main_suit' in user_state['case_data']:
            main_suit = user_state['case_data']['main_suit']
            result = {
                'status': 'success',
                'main_suit': main_suit
            }
            return jsonify(result)
        else:
            # 如果没有main_suit字段，返回默认值而不是404错误
            print(f"警告：用户 {username} 的案例数据中没有main_suit字段")
            return jsonify({
                'status': 'success',
                'main_suit': '有一些不舒服'
            })

    except Exception as e:
        print(f"获取主诉失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取主诉失败: {str(e)}'
        }), 500


@app.route('/api/init-user', methods=['POST'])
def init_user():
    """根据用户名初始化用户状态"""
    try:
        data = request.json
        username = data.get('username', '')
        user_id = data.get('user_id', str(uuid.uuid4()))

        if not username:
            return jsonify({'status': 'error', 'message': '用户名不能为空'}), 400

        user_state = get_user_state(username)
        # 不再需要创建用户文件夹，直接保存到case文件夹
        user_state['user_dir'] = None
        user_state['user_id'] = user_id  # 保存user_id
        next_case_index = get_next_case_index(username)

        # 设置用户状态
        user_state['current_case_index'] = next_case_index
        user_state['case_data'] = load_medical_case(username, next_case_index)
        initialize_case(username)

        # 获取该用户的案例文件列表
        case_files = get_user_case_files(username)

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'user_dir': user_state['user_dir'],
            'username': username,
            'next_case_index': next_case_index,
            'total_cases': len(case_files),
            'debug_info': {
                'case_files': case_files,
                'current_case_file': case_files[next_case_index] if next_case_index < len(case_files) else 'N/A',
                'loaded_case_index': user_state['current_case_index'],
                'main_suit': user_state['case_data'].get('main_suit', 'N/A') if user_state['case_data'] else 'N/A'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get-saved-conversation', methods=['GET'])
def get_saved_conversation():
    """获取指定案例的已保存对话内容"""
    try:
        username = request.args.get('username', '')
        case_index = int(request.args.get('case_index', '-1'))

        if not username or case_index < 0:
            return jsonify({
                'status': 'error',
                'message': '缺少用户名或案例索引'
            }), 400

        # 获取案例文件列表
        case_files = get_user_case_files(username)
        if case_index >= len(case_files):
            return jsonify({
                'status': 'error',
                'message': '案例索引超出范围'
            }), 400

        # 获取案例文件夹
        case_file_path = case_files[case_index]
        case_folder = case_file_path.split('/')[0]

        # 构建case文件夹路径
        conversations_dir = config.CONVERSATIONS_DIR
        case_dir = os.path.join(conversations_dir, case_folder)

        if not os.path.exists(case_dir):
            return jsonify({
                'status': 'error',
                'message': '案例文件夹不存在'
            }), 404

        # 查找该用户在该case下的保存文件
        # 使用精确的文件名匹配 (filename == "{username}.json")
        expected_filename = f"{username}.json"
        user_file_path = os.path.join(case_dir, expected_filename)

        if not os.path.exists(user_file_path):
            return jsonify({
                'status': 'error',
                'message': '该案例还没有保存过对话'
            }), 404

        with open(user_file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        return jsonify({
            'status': 'success',
            'conversation': saved_data.get('conversation', []),
            'Diagnosis': saved_data.get('Diagnosis', ''),
            'Treatment': saved_data.get('Treatment', ''),
            'file': expected_filename
        })

    except Exception as e:
        print(f"获取已保存对话失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取已保存对话失败: {str(e)}'
        }), 500


@app.route('/api/save-conversation', methods=['POST'])
def save_conversation():
    """保存对话记录"""
    try:
        data = request.json
        # 使用前端传递的conversation数据
        conversation = data.get('conversation', [])
        username = data.get('username', '')
        user_id = data.get('user_id', 'default_user')
        conversation_length = len(conversation)
        # 从前端接收要保存的案例索引，如果没有则使用当前索引
        target_case_index = data.get('case_index', None)

        if not username:
            return jsonify({
                'status': 'error',
                'message': '缺少用户名信息',
                'debug_info': {
                    'username': username,
                    'user_id': user_id,
                    'conversation_length': conversation_length,
                    'conversation_content': str(conversation)[:200] + '...' if len(str(conversation)) > 200 else str(conversation),
                    'frontend_conversation_length': len(conversation),
                    'backend_history_length': len(user_state['message_history']) if 'user_state' in locals() else 0
                }
            }), 400

        user_state = get_user_state(username)

        # 检查是否有诊断或治疗方案，如果有则保存，即使对话为空
        has_diagnosis = data.get('Diagnosis', '').strip() != ''
        has_treatment = data.get('Treatment', '').strip() != ''

        # 收集调试信息
        debug_info = {
            'username': username,
            'user_id': user_id,
            'conversation_length': conversation_length,
            'conversation_content': str(conversation)[:200] + '...' if len(str(conversation)) > 200 else str(conversation),
            'frontend_conversation_length': len(conversation),
            'backend_history_length': len(user_state['message_history']),
            'has_diagnosis': has_diagnosis,
            'has_treatment': has_treatment,
            'diagnosis_length': len(data.get('Diagnosis', '')),
            'treatment_length': len(data.get('Treatment', '')),
            'target_case_index': target_case_index
        }

        # 修改逻辑：总是保存数据以标记该案例已被操作
        # 原来的逻辑会导致：
        # 1. 只有1条对话且无诊断治疗时会跳过保存
        # 2. get_next_case_index()找不到该用户的JSON文件，会继续跳到下一个案例
        # 3. 返回该案例时数据为空
        # 新逻辑：只要用户提交了数据，就保存以标记该案例已完成

        # 获取该用户的案例文件列表
        case_files = get_user_case_files(username)

        # 确定要保存的案例索引
        if target_case_index is not None:
            save_case_index = target_case_index
        else:
            save_case_index = user_state['current_case_index']

        # 使用指定的case索引对应的实际文件名，确保与加载的文件名一致
        if save_case_index < len(case_files):
            # case_files 中的文件名格式为 "case10/case10.json"
            case_file_path = case_files[save_case_index]
            # 提取case文件夹名称 (case10)
            case_folder = case_file_path.split('/')[0]
            file_number = save_case_index + 1
        else:
            # 如果索引超出范围，使用默认命名
            file_number = save_case_index + 1
            case_folder = f"case{file_number}"

        # 构建保存路径：直接保存到 conversations/{caseFolder}/ 中
        conversations_dir = config.CONVERSATIONS_DIR
        case_dir = os.path.join(conversations_dir, case_folder)

        # 确保目录存在
        if not os.path.exists(case_dir):
            os.makedirs(case_dir, exist_ok=True)

        # 使用用户名作为文件名，不使用时间戳，这样会覆盖之前的文件
        file_name = f"{username}.json"
        file_path = os.path.join(case_dir, file_name)

        debug_info['file_path'] = file_path
        debug_info['file_name'] = file_name
        debug_info['file_number'] = file_number
        debug_info['save_case_index'] = save_case_index
        debug_info['current_case_index'] = user_state['current_case_index']

        # 验证对话内容是否与当前案例匹配
        # 检查对话中的第一条消息是否包含当前案例的主诉
        if conversation and len(conversation) > 0:
            first_message = conversation[0].get('content', '')
            current_case_data = load_medical_case(username, save_case_index)
            if current_case_data and 'main_suit' in current_case_data:
                expected_main_suit = current_case_data['main_suit']
                if expected_main_suit not in first_message:
                    print(f"警告：对话内容与案例不匹配！")
                    print(f"期望的主诉：{expected_main_suit}")
                    print(f"实际对话：{first_message[:100]}...")
                    debug_info['content_mismatch'] = True
                    debug_info['expected_main_suit'] = expected_main_suit
                    debug_info['actual_first_message'] = first_message[:100]

        # 添加用户名到保存的数据中
        save_data = {
            'conversation': conversation,
            'Diagnosis': data.get('Diagnosis', ''),
            'Treatment': data.get('Treatment', '')
        }

        # 尝试保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            debug_info['file_saved'] = True
            debug_info['file_size'] = len(
                json.dumps(save_data, ensure_ascii=False))
        except Exception as file_error:
            debug_info['file_saved'] = False
            debug_info['file_error'] = str(file_error)
            raise file_error

        # 保存成功后，不清空消息历史，让next-step函数来处理
        # 这样可以确保保存和跳转的顺序正确

        return jsonify({
            'status': 'success',
            'file': file_name,
            'case_dir': case_dir,
            'debug_info': debug_info
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'debug_info': debug_info if 'debug_info' in locals() else {'error': str(e)}
        }), 500


@app.route('/classify-message', methods=['POST'])
def classify_message():
    """对AI回复进行分类的API端点"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        username = data.get('username', '')

        if not message:
            return jsonify({
                'status': 'error',
                'message': '消息内容不能为空'
            }), 400

        # 使用LLM进行分类
        classification_prompt = f"""
请对以下医疗对话内容进行分类，只返回分类结果（不要其他解释）：

分类类别：
- symptom: 症状（患者的主观感受，如疼痛、不适、发烧、胸闷、胸痛、心悸、气短、呼吸困难、晕厥等）
- sign: 体征（医生检查发现的客观表现，如体温、血压、心率、心脏听诊、瓣膜杂音、心界、肺部听诊等）
- examination: 辅助检查（实验室检查、影像学检查等，如血常规、心电图、超声心动图、心肌标志物、甲状腺功能、理化指标等）
- history: 个人史（病史、家族史、生活习惯、手术史、用药史、家族遗传史等）
- other: 其他（不属于上述类别的内容）

对话内容：{message}

请只返回分类结果（symptom/sign/examination/history/other）：
"""

        try:
            # 使用现有的AI模型进行分类
            classification_messages = [
                {"role": "user", "content": classification_prompt}
            ]

            # 调用AI进行分类
            classification_response = get_response(classification_messages)
            category = classification_response.strip().lower()

            # 验证分类结果
            valid_categories = ['symptom', 'sign',
                                'examination', 'history', 'other']
            if category not in valid_categories:
                print(f"LLM返回无效分类结果: '{category}'，使用默认分类: 'other'")
                category = 'other'
            else:
                print(f"LLM分类成功: {category}")

        except Exception as llm_error:
            print(f"LLM分类失败: {str(llm_error)}，使用默认分类: 'other'")
            category = 'other'

        return jsonify({
            'status': 'success',
            'category': category,
            'message': f'Message classified as: {category}'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Classification failed: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Analysis service"""
    return jsonify({
        'status': 'healthy',
        'service': 'analysis'
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.DEBUG, port=5000)
