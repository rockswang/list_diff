#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单字典列表非深度对比演示
生成50万测试数据，克隆产生第二个列表，并随机修改主键和数据字段，然后计算差分并测速
"""

import time
import random
from listdiff2 import list_diff

def generate_test_data(n=500000):
    """生成测试数据"""
    print(f'生成 {n} 条测试数据...')
    data = []
    for i in range(n):
        item = {
            'id': i,
            'name': f'用户_{i}',
            'age': random.randint(18, 80),
            'score': random.randint(0, 100),
            'active': random.choice([True, False])
        }
        data.append(item)
    return data

def modify_data(data, modify_rate=0.1):
    """修改数据，模拟数据变化"""
    print(f'修改数据，修改率: {modify_rate:.1%}')
    modified = data.copy()
    
    # 随机修改一些记录
    n_modify = int(len(data) * modify_rate)
    indices_to_modify = random.sample(range(len(data)), n_modify)
    
    for idx in indices_to_modify:
        # 随机修改字段值
        field = random.choice(['name', 'age', 'score', 'active'])
        if field == 'name':
            modified[idx][field] = f'用户_修改_{idx}'
        elif field == 'age':
            modified[idx][field] = random.randint(18, 80)
        elif field == 'score':
            modified[idx][field] = random.randint(0, 100)
        else:  # active
            modified[idx][field] = not modified[idx][field]
    
    # 随机删除一些记录
    n_delete = int(len(data) * 0.05)
    indices_to_delete = random.sample(range(len(data)), n_delete)
    for idx in sorted(indices_to_delete, reverse=True):
        modified.pop(idx)
    
    # 随机添加一些新记录
    n_add = int(len(data) * 0.05)
    max_id = max(item['id'] for item in modified)
    for i in range(n_add):
        new_id = max_id + i + 1
        new_item = {
            'id': new_id,
            'name': f'用户_新增_{new_id}',
            'age': random.randint(18, 80),
            'score': random.randint(0, 100),
            'active': random.choice([True, False])
        }
        modified.append(new_item)
    
    return modified

def demo_simple_diff():
    """演示简单字典列表非深度对比"""
    print('=' * 60)
    print('简单字典列表非深度对比演示')
    print('=' * 60)
    
    # 生成测试数据
    start_time = time.time()
    data1 = generate_test_data(500000)
    gen_time = time.time() - start_time
    print(f'数据生成完成，耗时: {gen_time:.2f}秒')
    
    # 修改数据
    start_time = time.time()
    data2 = modify_data(data1, 0.1)
    modify_time = time.time() - start_time
    print(f'数据修改完成，耗时: {modify_time:.2f}秒')
    
    print(f'列表1长度: {len(data1)}')
    print(f'列表2长度: {len(data2)}')
    
    # 计算差分
    print('开始计算差分...')
    start_time = time.time()
    removed, added, updated = list_diff(data1, data2, 'id', ['name', 'age', 'score', 'active'])
    diff_time = time.time() - start_time
    
    print(f'差分计算完成，耗时: {diff_time:.2f}秒')
    print(f'删除记录数: {len(removed)}')
    print(f'新增记录数: {len(added)}')
    print(f'更新记录数: {len(updated)}')
    
    # 显示一些示例结果
    if removed:
        print(f'删除记录示例: {list(removed)[:5]}')
    if added:
        print(f'新增记录示例: {list(added)[:5]}')
    if updated:
        print(f'更新记录示例: {list(updated)[:5]}')
    
    print('=' * 60)
    print('性能统计:')
    print(f'数据生成: {gen_time:.2f}秒')
    print(f'数据修改: {modify_time:.2f}秒')
    print(f'差分计算: {diff_time:.2f}秒')
    print(f'总耗时: {gen_time + modify_time + diff_time:.2f}秒')
    print('=' * 60)

if __name__ == '__main__':
    demo_simple_diff()