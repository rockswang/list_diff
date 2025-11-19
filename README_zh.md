# listdiff2

一个可用于大量结构化数据快速差分计算的纯 Python 库，不使用循环而是使用集合运算用于计算字典列表之间的差异，支持字典对象的深层对比。

## 功能特性

- **列表比较**：比较两个字典列表，识别新增、删除和更新的项目。适合排序无关的结构化数据，如数据库记录，JSON数据文件，数据表格等
- **自定义主键**：支持单个或组合主键
- **灵活字段选择**：指定要比较的字段
- **对象级差分**：深度比较嵌套对象，支持单层展开和深度展开
- **可哈希转换**：提供工具函数，可将复杂对象转换为可哈希形式以便高效比较
- **高性能**：虽然是纯 Python 实现，但基于高速的集合运算，百万数量级对象差分可在秒级完成
- **严格 None 处理**：可选区分缺失字段和 None 值

## 安装

```bash
pip install listdiff2
```

## 快速开始

```python
from listdiff2 import list_diff

# 示例数据
list1 = [
    {'id': 1, 'name': 'Alice', 'age': 25},
    {'id': 2, 'name': 'Bob', 'age': 30},
    {'id': 3, 'name': 'Charlie', 'age': 35}
]

list2 = [
    {'id': 1, 'name': 'Alice', 'age': 26},  # age 改变
    {'id': 2, 'name': 'Bob', 'age': 30},    # 未改变
    {'id': 4, 'name': 'David', 'age': 40}   # 新项目
]

# 计算差异
# 注意：返回的三元组顺序为 (删除的主键, 新增的主键, 更新的主键)
# 如果将 list1 视为旧数据，list2 视为新数据，则对应为 (删除的, 新增的, 更新的)
removed, added, updated = list_diff(list1, list2, 'id', ['name', 'age'])

print(f"删除: {removed}") # {3}
print(f"新增: {added}")    # {4}
print(f"更新: {updated}") # {1}
```

## 高级用法

### 组合主键

```python
list1 = [{'dept': 'IT', 'emp_id': 1, 'name': 'Alice'}]
list2 = [{'dept': 'IT', 'emp_id': 1, 'name': 'Alicia'}]

removed, added, updated = list_diff(list1, list2, ['dept', 'emp_id'], ['name'])
print(f"更新: {updated}")  # {('IT', 1)}
```

### 对象级差分

```python
from listdiff2 import list_diff, as_hashable

# 深度对象比较 - 需要先转换为可哈希对象
list1 = [as_hashable({'id': 1, 'data': {'nested': {'value': 1}}})]
list2 = [as_hashable({'id': 1, 'data': {'nested': {'value': 2}}})]

removed, added, updated = list_diff(list1, list2, 'id', ['data'], diff_obj=-1)
print(f"更新详情: {updated}")
# {1: (set(), set(), {('data', 'nested', 'value')})}
```

### 对象比较

```python
from listdiff2 import obj_diff

obj1 = {'a': 1, 'b': {'c': 2}}
obj2 = {'a': 1, 'b': {'c': 3}}

added, removed, updated = obj_diff(obj1, obj2)
print(f"新增: {added}")    # set()
print(f"删除: {removed}") # set()
print(f"更新: {updated}") # {('b', 'c')}
```

## API 参考

### `list_diff(lst1, lst2, pk, fields, /, diff_obj=0, strict_none_diff=False)`

计算两个字典列表之间的差异。

**参数：**
- `lst1` (list[dict]): 第一个字典列表
- `lst2` (list[dict]): 第二个字典列表
- `pk` (str | list[str]): 主键字段或字段列表
- `fields` (list[str]): 要比较的字段列表
- `diff_obj` (int): 对象差分级别
  - `0` = 无差分（默认）
  - `1` = 浅层差分（仅展开第一层）
  - `-1` = 深度差分（递归展开所有层）
- `strict_none_diff` (bool): 深度差分时，是否严格区分缺失值和 None 值

**返回：**
- 包含三个集合的元组：(删除的主键, 新增的主键, 更新的主键或详情)
- 如果将 lst1 视为旧数据，lst2 视为新数据，则对应为 (删除的记录, 新增的记录, 更新的记录)
- 当 `diff_obj` 不为 0 时，第三个返回值是字典，包含对象级差分详情

### `obj_diff(obj1, obj2)`

计算两个对象之间的差异。

**参数：**
- `obj1`: 第一个对象
- `obj2`: 第二个对象

**返回：**
- 包含三个集合的元组：(新增路径, 删除路径, 更新路径)
- 路径使用元组表示，如 `('user', 'profile', 'name')`

### `as_hashable(val, converters={}, prop_path=tuple())`

将值转换为可哈希形式用于比较。**重要：当使用对象级差分时，必须先将字典对象通过此函数转换。**

**参数：**
- `val`: 要转换的值
- `converters`: 自定义转换器字典，格式为 `{type: conversion_function}`
- `prop_path`: 属性路径，用于递归转换

**返回：**
- 可哈希的对象（字典转换为 DICT 类，列表转换为 LIST 类，集合转换为 SET 类）

**转换规则：**
- `dict` → `DICT`（递归转换值）
- `list` → `LIST`（递归转换元素）
- `set` → `SET`（元素必须已可哈希）

**示例：**
```python
from listdiff2 import as_hashable

# 转换复杂对象为可哈希形式
complex_obj = {
    'nested': {
        'list': [1, 2, 3],
        'dict': {'a': 1, 'b': 2}
    }
}

hashable_obj = as_hashable(complex_obj)
# 现在可以用于集合运算和差分计算
```

### `deep_get(obj, prop_path)`

获取对象的深层属性值。常用于配合对象级差分结果使用。

**参数：**
- `obj`: 要获取值的对象
- `prop_path`: 属性路径元组，如 `('user', 'profile', 'name')`

**返回：**
- 指定路径的属性值
- 如果路径不存在，抛出 `KeyError` 或 `IndexError`

**示例：**
```python
from listdiff2 import deep_get

data = {
    'user': {
        'profile': {
            'name': 'Alice',
            'contact': {
                'email': 'alice@example.com'
            }
        }
    }
}

# 获取深层属性
email = deep_get(data, ('user', 'profile', 'contact', 'email'))
print(email)  # 'alice@example.com'

# 结合差分结果使用
# 假设有差分结果 updated = {1: (set(), set(), {('user', 'profile', 'name')})}
# 可以这样获取差异值：
# old_value = deep_get(old_record, ('user', 'profile', 'name'))
# new_value = deep_get(new_record, ('user', 'profile', 'name'))
```

## 完整示例

### 使用 as_hashable 和 deep_get 进行深度差分分析

```python
from listdiff2 import list_diff, as_hashable, deep_get

# 复杂嵌套数据
data1 = [
    {
        'id': 1,
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 25,
                'contact': {'email': 'alice@old.com'}
            }
        }
    }
]

data2 = [
    {
        'id': 1,
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 26,  # 年龄更新
                'contact': {'email': 'alice@new.com'}  # 邮箱更新
            }
        }
    }
]

# 转换为可哈希对象
hashable_data1 = [as_hashable(item) for item in data1]
hashable_data2 = [as_hashable(item) for item in data2]

# 深度差分计算
removed, added, updated = list_diff(
    hashable_data1, hashable_data2, 'id', ['user'], diff_obj=-1
)

print(f"删除: {removed}")
print(f"新增: {added}")
print(f"更新详情: {updated}")

# 使用 deep_get 获取具体差异值
if updated:
    for record_id, diff_info in updated.items():
        added_paths, removed_paths, updated_paths = diff_info
        
        # 查找原始记录
        old_record = next(item for item in data1 if item['id'] == record_id)
        new_record = next(item for item in data2 if item['id'] == record_id)
        
        print(f"\n记录 {record_id} 的差异:")
        for path in updated_paths:
            old_value = deep_get(old_record, path)
            new_value = deep_get(new_record, path)
            print(f"  路径 {path}: {old_value} -> {new_value}")
```

## 性能特点

- **高性能集合运算**：基于 Python 内置集合操作，避免循环遍历
- **内存优化**：使用生成器和惰性计算处理大数据集
- **可扩展性**：支持自定义转换器和复杂数据结构

## 使用场景

- **数据库同步**：比较数据库表记录差异
- **电子表格对比**：对比不同版本的Excel/CSV等数据文件
- **数据同步**：ETL 过程中的数据变更检测
- **API 响应对比**：测试环境与生产环境 API 响应差异
- **日志分析**：识别不同时间段的日志变化

## 演示例程

项目包含多个演示例程，位于 `examples/` 目录：

- [`simple_diff_demo.py`](examples/simple_diff_demo.py) - 简单字典列表对比（50万数据量）
- [`shallow_diff_demo.py`](examples/shallow_diff_demo.py) - 首层展开对象对比（10万数据量）
- [`deep_diff_demo.py`](examples/deep_diff_demo.py) - 深度展开对象对比（1万数据量）
- [`test_composite_key.py`](examples/test_composite_key.py) - 复合主键功能测试
- [`run_all_demos.py`](examples/run_all_demos.py) - 运行所有演示

运行示例：
```bash
cd examples
python run_all_demos.py
```

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 常见问题

**Q: 为什么对象级差分需要先使用 `as_hashable` 转换？**
A: 因为字典对象本身不可哈希，无法直接用于集合运算。`as_hashable` 将字典转换为可哈希的 `DICT` 类。

**Q: 是否支持自定义比较逻辑？**
A: 可以通过 `as_hashable.converters` 参数自定义类型转换逻辑。