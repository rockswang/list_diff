#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有演示例程的主程序
"""

import sys
import os

# 添加父目录到路径，以便导入 list_diff 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """运行所有演示例程"""
    print('listdiff2 模块演示程序')
    print('=' * 50)
    
    try:
        # 导入演示模块
        from simple_diff_demo import demo_simple_diff
        from shallow_diff_demo import demo_shallow_diff
        from deep_diff_demo import demo_deep_diff
        
        # 运行简单对比演示
        demo_simple_diff()
        
        print('\n' + '=' * 50)
        input('按 Enter 键继续运行首层展开对比演示...')
        print()
        
        # 运行首层展开对比演示
        demo_shallow_diff()
        
        print('\n' + '=' * 50)
        input('按 Enter 键继续运行全展开对比演示...')
        print()
        
        # 运行全展开对比演示
        demo_deep_diff()
        
        print('\n' + '=' * 50)
        print('所有演示例程运行完成！')
        
    except ImportError as e:
        print(f'导入错误: {e}')
        print('请确保 list_diff 模块已正确安装')
    except Exception as e:
        print(f'运行错误: {e}')

if __name__ == '__main__':
    main()