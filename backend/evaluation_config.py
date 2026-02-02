import os


class EvaluationConfig:
    """评估系统配置类"""
    # Flask配置
    DEBUG = False

    # 评估系统文件路径配置
    EVALUATORS_DIR = os.environ.get('EVALUATORS_DIR') or "./evaluators"
    CONVERSATIONS_DIR = os.environ.get(
        'CONVERSATIONS_DIR') or "./conversations"

    # 安全配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or ['*']

    @property
    def OPENAI_API_KEY(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_API_KEY')

    @property
    def OPENAI_BASE_URL(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_BASE_URL')

    @property
    def OPENAI_MODEL(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_MODEL')

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保必要的目录存在
        for dir_path in [EvaluationConfig.EVALUATORS_DIR, EvaluationConfig.CONVERSATIONS_DIR]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)


class EvaluationDevelopmentConfig(EvaluationConfig):
    """评估系统开发环境配置"""
    DEBUG = True


class EvaluationProductionConfig(EvaluationConfig):
    """评估系统生产环境配置"""
    DEBUG = False


class EvaluationDockerConfig(EvaluationConfig):
    """评估系统Docker环境配置"""
    DEBUG = False

    # Docker环境中的路径配置
    EVALUATORS_DIR = "/app/evaluators"
    CONVERSATIONS_DIR = "/app/conversations"


# 配置映射
evaluation_config = {
    'development': EvaluationDevelopmentConfig,
    'production': EvaluationProductionConfig,
    'docker': EvaluationDockerConfig,
    'default': EvaluationDevelopmentConfig
}


def get_evaluation_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV', 'default')
    config_class = evaluation_config.get(env, evaluation_config['default'])
    return config_class()  # Return an instance of the config class
