#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列表首层展开比对演示
生成10万测试数据，每个元素含列表、字典类字段各一个，进行首层展开比对并测速
"""

import time
import random
from listdiff2 import list_diff, as_hashable

def generate_complex_data(n=100000):
    """生成包含列表和字典字段的复杂测试数据"""
    print(f'生成 {n} 条复杂测试数据...')
    data = []
    for i in range(n):
        # 生成列表字段
        scores = [random.randint(60, 100) for _ in range(random.randint(3, 8))]
        
        # 生成字典字段
        profile = {
            'height': random.randint(160, 190),
            'weight': random.randint(50, 90),
            'hobbies': random.sample(['阅读', '运动', '音乐', '旅行', '烹饪'],
                                   random.randint(1, 3))
        }
        
        item = {
            'id': i,
            'name': f'用户_{i}',
            'scores': scores,  # 列表字段
            'profile': profile,  # 字典字段
            'department': random.choice(['技术部', '人事部', '财务部', '市场部', '运营部'])
        }
        data.append(item)
    return data

def modify_complex_data(data, modify_rate=0.1):
    """修改复杂数据"""
    print(f'修改复杂数据，修改率: {modify_rate:.1%}')
    modified = data.copy()
    
    n_modify = int(len(data) * modify_rate)
    indices_to_modify = random.sample(range(len(data)), n_modify)
    
    for idx in indices_to_modify:
        # 随机修改不同类型的字段
        field_type = random.choice(['simple', 'list', 'dict'])
        
        if field_type == 'simple':
            # 修改简单字段
            field = random.choice(['name', 'department'])
            if field == 'name':
                modified[idx][field] = f'用户_修改_{idx}'
            else:
                modified[idx][field] = random.choice(['技术部', '人事部', '财务部', '市场部', '运营部'])
        
        elif field_type == 'list':
            # 修改列表字段 - 添加或删除元素
            if random.random() < 0.5:
                # 添加元素
                modified[idx]['scores'].append(random.randint(60, 100))
            else:
                # 删除元素（如果有多个元素）
                if len(modified[idx]['scores']) > 1:
                    modified[idx]['scores'].pop()
        
        else:  # dict
            # 修改字典字段
            if random.random() < 0.5:
                # 修改现有字段
                if 'height' in modified[idx]['profile']:
                    modified[idx]['profile']['height'] = random.randint(160, 190)
            else:
                # 添加新字段
                modified[idx]['profile']['new_field'] = f'值_{random.randint(1, 100)}'
    
    # 随机删除一些记录
    n_delete = int(len(data) * 0.03)
    indices_to_delete = random.sample(range(len(data)), n_delete)
    for idx in sorted(indices_to_delete, reverse=True):
        modified.pop(idx)
    
    # 随机添加一些新记录
    n_add = int(len(data) * 0.03)
    max_id = max(item['id'] for item in modified)
    for i in range(n_add):
        new_id = max_id + i + 1
        scores = [random.randint(60, 100) for _ in range(random.randint(3, 8))]
        profile = {
            'height': random.randint(160, 190),
            'weight': random.randint(50, 90),
            'hobbies': random.sample(['阅读', '运动', '音乐', '旅行', '烹饪'],
                                   random.randint(1, 3))
        }
        new_item = {
            'id': new_id,
            'name': f'用户_新增_{new_id}',
            'scores': scores,
            'profile': profile,
            'department': random.choice(['技术部', '人事部', '财务部', '市场部', '运营部'])
        }
        modified.append(new_item)
    
    return modified

def demo_shallow_diff():
    """演示列表首层展开比对"""
    print('=' * 60)
    print('列表首层展开比对演示')
    print('=' * 60)
    
    # 生成测试数据
    start_time = time.time()
    data1 = generate_complex_data(100000)
    gen_time = time.time() - start_time
    print(f'复杂数据生成完成，耗时: {gen_time:.2f}秒')
    
    # 修改数据
    start_time = time.time()
    data2 = modify_complex_data(data1, 0.1)
    modify_time = time.time() - start_time
    print(f'复杂数据修改完成，耗时: {modify_time:.2f}秒')
    
    print(f'列表1长度: {len(data1)}')
    print(f'列表2长度: {len(data2)}')
    
    # 计算差分 - 首层展开 (diff_obj=1)
    print('开始计算首层展开差分...')
    start_time = time.time()
    # 在调用list_diff前将整个列表转换为可哈希对象
    hashable_data1 = [as_hashable(item) for item in data1]
    hashable_data2 = [as_hashable(item) for item in data2]
    removed, added, updated = list_diff(hashable_data1, hashable_data2, 'id',
                                      ['name', 'scores', 'profile', 'department'],
                                      diff_obj=1)
    diff_time = time.time() - start_time
    
    print(f'首层展开差分计算完成，耗时: {diff_time:.2f}秒')
    print(f'删除记录数: {len(removed)}')
    print(f'新增记录数: {len(added)}')
    print(f'更新记录数: {len(updated)}')
    
    # 显示更新详情（首层展开的结果）
    if updated:
        sample_key = list(updated.keys())[0]
        sample_value = updated[sample_key]
        print(f'更新详情示例 - 主键 {sample_key}:')
        print(f'  新增字段: {sample_value[0]}')
        print(f'  删除字段: {sample_value[1]}')
        print(f'  更新字段: {sample_value[2]}')
    
    print('=' * 60)
    print('性能统计:')
    print(f'数据生成: {gen_time:.2f}秒')
    print(f'数据修改: {modify_time:.2f}秒')
    print(f'差分计算: {diff_time:.2f}秒')
    print(f'总耗时: {gen_time + modify_time + diff_time:.2f}秒')
    print('=' * 60)

if __name__ == '__main__':
    demo_shallow_diff()