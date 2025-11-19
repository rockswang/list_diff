#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复合主键功能
"""

import random
from listdiff2 import list_diff, as_hashable

def test_composite_key():
    """测试复合主键功能"""
    print('测试复合主键功能...')
    
    # 创建简单的测试数据
    data1 = [
        {'company': '公司A', 'employee_id': 'E001', 'name': '张三', 'salary': 50000},
        {'company': '公司A', 'employee_id': 'E002', 'name': '李四', 'salary': 60000},
        {'company': '公司B', 'employee_id': 'E001', 'name': '王五', 'salary': 70000},
    ]
    
    data2 = [
        {'company': '公司A', 'employee_id': 'E001', 'name': '张三', 'salary': 55000},  # 更新
        {'company': '公司A', 'employee_id': 'E002', 'name': '李四', 'salary': 60000},    # 不变
        {'company': '公司B', 'employee_id': 'E001', 'name': '王五', 'salary': 70000}, # 不变
        {'company': '公司A', 'employee_id': 'E003', 'name': '赵六', 'salary': 65000},  # 新增
    ]
    
    print('数据1:')
    for item in data1:
        print(f"  {item}")
    
    print('数据2:')
    for item in data2:
        print(f"  {item}")
    
    # 使用复合主键进行差分计算
    hashable_data1 = [as_hashable(item) for item in data1]
    hashable_data2 = [as_hashable(item) for item in data2]
    
    removed, added, updated = list_diff(hashable_data1, hashable_data2,
                                      ['company', 'employee_id'], ['name', 'salary'],
                                      diff_obj=-1)
    
    print(f'删除记录: {removed}')
    print(f'新增记录: {added}')
    print(f'更新记录: {updated}')
    
    if updated:
        for pk, diff_info in updated.items():
            print(f'主键 {pk} 的差异: {diff_info}')

if __name__ == '__main__':
    test_composite_key()