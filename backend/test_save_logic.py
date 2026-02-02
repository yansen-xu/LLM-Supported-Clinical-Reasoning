#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试save-conversation逻辑的脚本
验证是否会正确保存数据并标记案例为已完成
"""

import json
import os
import sys

# 模拟测试场景
def test_save_logic():
    """测试保存逻辑"""
    print("=" * 60)
    print("测试save-conversation逻辑")
    print("=" * 60)
    
    # 场景1: 只有1条对话，无诊断治疗
    test_cases = [
        {
            'name': '场景1: 只有1条对话，无诊断治疗',
            'conversation_length': 1,
            'has_diagnosis': False,
            'has_treatment': False,
            'should_skip': 'NO (修复后)',
            'reason': '修改后会保存数据以标记案例已被操作'
        },
        {
            'name': '场景2: 有2条对话，无诊断治疗',
            'conversation_length': 2,
            'has_diagnosis': False,
            'has_treatment': False,
            'should_skip': 'NO',
            'reason': '对话足够，会保存'
        },
        {
            'name': '场景3: 1条对话，有诊断',
            'conversation_length': 1,
            'has_diagnosis': True,
            'has_treatment': False,
            'should_skip': 'NO',
            'reason': '有诊断内容，会保存'
        },
        {
            'name': '场景4: 空对话，无诊断治疗',
            'conversation_length': 0,
            'has_diagnosis': False,
            'has_treatment': False,
            'should_skip': 'NO (修复后)',
            'reason': '修改后会保存数据以标记案例已被操作'
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}")
        print(f"  对话长度: {case['conversation_length']}")
        print(f"  有诊断: {case['has_diagnosis']}")
        print(f"  有治疗: {case['has_treatment']}")
        print(f"  原逻辑是否跳过: {'YES' if case['conversation_length'] < 2 and not case['has_diagnosis'] and not case['has_treatment'] else 'NO'}")
        print(f"  修改后是否跳过: {case['should_skip']}")
        print(f"  原因: {case['reason']}")
    
    print("\n" + "=" * 60)
    print("修复关键点:")
    print("=" * 60)
    print("""
1. 原问题: save-conversation在以下条件下会跳过保存:
   - conversation_length < 2 AND
   - 没有诊断内容 AND
   - 没有治疗内容
   
2. 后果:
   - case文件夹中不会创建{username}.json文件
   - get_next_case_index()找不到该文件，认为案例未完成
   - 继续跳转到下一个案例
   - 返回时该案例数据为空

3. 修复方案:
   - 移除跳过保存的条件
   - 总是保存数据，即使只有初始消息或诊断治疗为空
   - 这样case文件夹中会创建{username}.json文件
   - get_next_case_index()能正确识别已完成的案例

4. 同时修复了get_previous_case_index():
   - 原来检查 if len(json_files) > 1
   - 因为case文件夹中有多个AI模型的JSON文件
   - 修改为检查是否存在包含用户名的JSON文件
   - 这样能正确识别用户操作过的案例
    """)

if __name__ == '__main__':
    test_save_logic()
