#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂字典列表全展开对比演示
生成测试数据，包含嵌套字典，进行全展开比对并演示 deep_get 使用
"""

import time
import random
from listdiff2 import list_diff, as_hashable, deep_get

def generate_single_nested_data(idx, company='Company_A'):
    """生成单条嵌套测试数据"""
    item = {
        'company': company,
        'employee_id': f'E{str(idx).zfill(3)}',
        'basic_info': {
            'name': f'Employee_{idx}',
            'age': random.randint(20, 60),
            'department': random.choice(['Engineering', 'Product', 'Design'])
        },
        'contact': {
            'email': f'employee_{idx}@company.com',
            'phone': f'+1-555-{random.randint(1000, 9999)}',
            'address': {
                'city': random.choice(['New York', 'San Francisco', 'London']),
                'zipcode': str(random.randint(10000, 99999))
            }
        },
        'work_info': {
            'salary': random.randint(50000, 150000),
            'level': random.choice(['Junior', 'Mid', 'Senior']),
            'projects': [
                {
                    'name': f'Project_{j}',
                    'status': random.choice(['active', 'completed']),
                    'progress': random.randint(0, 100)
                }
                for j in range(random.randint(1, 3))
            ]
        }
    }
    return item

def generate_simple_nested_data(n=100):
    """生成简化的嵌套测试数据"""
    print(f'生成 {n} 条嵌套测试数据...')
    return [generate_single_nested_data(i) for i in range(n)]

def modify_nested_data(data, modify_rate=0.3):
    """修改嵌套数据，确保有更新记录"""
    print(f'修改嵌套数据，修改率: {modify_rate:.1%}')
    modified = []
    
    # 深度复制所有数据
    for item in data:
        import copy
        modified.append(copy.deepcopy(item))
    
    n_modify = int(len(data) * modify_rate)
    indices_to_modify = random.sample(range(len(data)), n_modify)
    
    for idx in indices_to_modify:
        # 确保进行真正的修改，避免随机到相同的值
        mod_type = random.choice(['basic', 'contact', 'work'])
        
        if mod_type == 'basic':
            # 修改基本信息
            if random.random() < 0.5:
                old_age = modified[idx]['basic_info']['age']
                new_age = random.randint(20, 60)
                while new_age == old_age:
                    new_age = random.randint(20, 60)
                modified[idx]['basic_info']['age'] = new_age
            else:
                old_dept = modified[idx]['basic_info']['department']
                new_dept = random.choice(['Engineering', 'Product', 'Design'])
                while new_dept == old_dept:
                    new_dept = random.choice(['Engineering', 'Product', 'Design'])
                modified[idx]['basic_info']['department'] = new_dept
        
        elif mod_type == 'contact':
            # 修改联系信息
            if random.random() < 0.5:
                old_phone = modified[idx]['contact']['phone']
                new_phone = f'+1-555-{random.randint(1000, 9999)}'
                while new_phone == old_phone:
                    new_phone = f'+1-555-{random.randint(1000, 9999)}'
                modified[idx]['contact']['phone'] = new_phone
            else:
                old_city = modified[idx]['contact']['address']['city']
                new_city = random.choice(['New York', 'San Francisco', 'London'])
                while new_city == old_city:
                    new_city = random.choice(['New York', 'San Francisco', 'London'])
                modified[idx]['contact']['address']['city'] = new_city
        
        else:  # work
            # 修改工作信息
            if random.random() < 0.5:
                old_salary = modified[idx]['work_info']['salary']
                new_salary = random.randint(50000, 150000)
                while new_salary == old_salary:
                    new_salary = random.randint(50000, 150000)
                modified[idx]['work_info']['salary'] = new_salary
            elif modified[idx]['work_info']['projects']:
                project_idx = random.randint(0, len(modified[idx]['work_info']['projects']) - 1)
                old_progress = modified[idx]['work_info']['projects'][project_idx]['progress']
                new_progress = random.randint(0, 100)
                while new_progress == old_progress:
                    new_progress = random.randint(0, 100)
                modified[idx]['work_info']['projects'][project_idx]['progress'] = new_progress
    
    # 删除一些记录
    n_delete = int(len(data) * 0.1)
    indices_to_delete = random.sample(range(len(data)), n_delete)
    for idx in sorted(indices_to_delete, reverse=True):
        modified.pop(idx)
    
    # 添加一些新记录
    n_add = int(len(data) * 0.1)
    for i in range(n_add):
        new_item = generate_single_nested_data(len(data) + i)
        new_item['employee_id'] = f'E{str(len(data) + i).zfill(3)}'
        new_item['basic_info']['name'] = f'New_Employee_{len(data) + i}'
        modified.append(new_item)
    
    return modified

def demo_deep_diff():
    """演示复杂字典列表全展开比对"""
    print('=' * 60)
    print('复杂字典列表全展开比对演示')
    print('=' * 60)
    
    # 生成测试数据
    start_time = time.time()
    data1 = generate_simple_nested_data(10000)
    gen_time = time.time() - start_time
    print(f'嵌套数据生成完成，耗时: {gen_time:.2f}秒')
    
    # 修改数据
    start_time = time.time()
    data2 = modify_nested_data(data1, 0.5)  # 增加修改率
    modify_time = time.time() - start_time
    print(f'嵌套数据修改完成，耗时: {modify_time:.2f}秒')
    
    print(f'列表1长度: {len(data1)}')
    print(f'列表2长度: {len(data2)}')
    
    # 计算差分 - 全展开 (diff_obj=-1)
    print('开始计算全展开差分...')
    start_time = time.time()
    # 在调用list_diff前将整个列表转换为可哈希对象
    hashable_data1 = [as_hashable(item) for item in data1]
    hashable_data2 = [as_hashable(item) for item in data2]
    removed, added, updated = list_diff(hashable_data1, hashable_data2, ['company', 'employee_id'],
                                      ['basic_info', 'contact', 'work_info'],
                                      diff_obj=-1)
    diff_time = time.time() - start_time
    
    print(f'全展开差分计算完成，耗时: {diff_time:.2f}秒')
    print(f'删除记录数: {len(removed)}')
    print(f'新增记录数: {len(added)}')
    print(f'更新记录数: {len(updated)}')
    
    # 显示前几条差异数据
    print('\n差异数据预览:')
    if removed:
        print(f'删除记录 (前{min(3, len(removed))}条):')
        for i, pk in enumerate(list(removed)[:3]):
            print(f'  {i+1}. 主键: {pk}')
    
    if added:
        print(f'新增记录 (前{min(3, len(added))}条):')
        for i, pk in enumerate(list(added)[:3]):
            print(f'  {i+1}. 主键: {pk}')
    
    # 显示更新详情
    if updated:
        print(f'更新记录详情 (前{min(3, len(updated))}条):')
        for i, (pk, diff_info) in enumerate(list(updated.items())[:3]):
            added_paths, removed_paths, updated_paths = diff_info
            print(f'  {i+1}. 主键 {pk}:')
            print(f'    新增路径: {list(added_paths)[:2]}...')  # 显示前2个
            print(f'    删除路径: {list(removed_paths)[:2]}...')  # 显示前2个
            print(f'    更新路径: {list(updated_paths)[:2]}...')  # 显示前2个
    
    # 演示如何使用 deep_get 获取差异项
    print('\n使用 deep_get 获取差异项演示:')
    if updated:
        sample_pk = list(updated.keys())[0]
        added_paths, removed_paths, updated_paths = updated[sample_pk]
        
        # 从原始数据中查找对应记录
        def find_record_by_pk(data, pk):
            for record in data:
                if (record.get('company'), record.get('employee_id')) == pk:
                    return record
            return None
        
        record1 = find_record_by_pk(data1, sample_pk)
        record2 = find_record_by_pk(data2, sample_pk)
        
        if record1 and record2:
            print(f'主键 {sample_pk} 的差异项:')
            
            # 演示获取更新路径的值
            if updated_paths:
                sample_path = list(updated_paths)[0]
                print(f'  路径 {sample_path}:')
                try:
                    # 直接使用整个路径，不需要跳过任何部分
                    val1 = deep_get(record1, sample_path)
                    val2 = deep_get(record2, sample_path)
                    print(f'    列表1: {val1}')
                    print(f'    列表2: {val2}')
                except (KeyError, IndexError) as e:
                    print(f'    无法获取路径值: {e}')
            
            # 演示获取新增路径的值
            if added_paths:
                sample_path = list(added_paths)[0]
                print(f'  新增路径 {sample_path}:')
                try:
                    val2 = deep_get(record2, sample_path)
                    print(f'    列表2: {val2} (列表1中不存在)')
                except (KeyError, IndexError) as e:
                    print(f'    无法获取路径值: {e}')
            
            # 演示获取删除路径的值
            if removed_paths:
                sample_path = list(removed_paths)[0]
                print(f'  删除路径 {sample_path}:')
                try:
                    val1 = deep_get(record1, sample_path)
                    print(f'    列表1: {val1} (列表2中不存在)')
                except (KeyError, IndexError) as e:
                    print(f'    无法获取路径值: {e}')
    
    print('=' * 60)
    print('性能统计:')
    print(f'数据生成: {gen_time:.2f}秒')
    print(f'数据修改: {modify_time:.2f}秒')
    print(f'差分计算: {diff_time:.2f}秒')
    print(f'总耗时: {gen_time + modify_time + diff_time:.2f}秒')
    print('=' * 60)

if __name__ == '__main__':
    demo_deep_diff()