# listdiff2

A pure Python library for fast diff of large structured data, using set operations instead of loops to calculate differences between lists of dictionaries, supporting deep comparison of dictionary objects.

## Features

- **List Comparison**: Compare two lists of dictionaries to identify added, removed, and updated items. Suitable for order-independent structured data such as database records, JSON data files, data tables, etc.

- **Custom Primary Keys**: Support for single or composite primary keys

- **Flexible Field Selection**: Specify which fields to compare

- **Object-level Diff**: Deep comparison of nested objects, supporting single-level expansion and deep expansion

- **Hashable Conversion**: Provides utility functions to convert complex objects into hashable forms for efficient comparison

- **High Performance**: Although pure Python implementation, based on high-speed set operations, object-level diff for millions of items can be completed in one second

- **Strict None Handling**: Optionally distinguish between missing fields and None values

## Installation

```bash
pip install listdiff2
```

## Quick Start

```python
from listdiff2 import list_diff

# Example data
list1 = [
    {'id': 1, 'name': 'Alice', 'age': 25},
    {'id': 2, 'name': 'Bob', 'age': 30},
    {'id': 3, 'name': 'Charlie', 'age': 35}
]

list2 = [
    {'id': 1, 'name': 'Alice', 'age': 26},  # age changed
    {'id': 2, 'name': 'Bob', 'age': 30},    # unchanged
    {'id': 4, 'name': 'David', 'age': 40}   # new item
]

# Calculate differences
# Note: The returned tuple order is (removed primary keys, added primary keys, updated primary keys)
# If list1 is considered old data and list2 is new data, then corresponding to (removed, added, updated)
removed, added, updated = list_diff(list1, list2, 'id', ['name', 'age'])

print(f"Removed: {removed}") # {3}
print(f"Added: {added}")    # {4}
print(f"Updated: {updated}") # {1}
```

## Advanced Usage

### Composite Primary Keys

```python
list1 = [{'dept': 'IT', 'emp_id': 1, 'name': 'Alice'}]
list2 = [{'dept': 'IT', 'emp_id': 1, 'name': 'Alicia'}]

removed, added, updated = list_diff(list1, list2, ['dept', 'emp_id'], ['name'])]
print(f"Updated: {updated}")  # {('IT', 1)}
```

### Object-level Diff

```python
from listdiff2 import list_diff, as_hashable

# Deep object comparison - need to convert to hashable objects first
list1 = [as_hashable({'id': 1, 'data': {'nested': {'value': 1}}})]
list2 = [as_hashable({'id': 1, 'data': {'nested': {'value': 2}}})]

removed, added, updated = list_diff(list1, list2, 'id', ['data'], diff_obj=-1)
print(f"Update details: {updated}")
# {1: (set(), set(), {('data', 'nested', 'value')})}
```

### Object Comparison

```python
from listdiff2 import obj_diff

obj1 = {'a': 1, 'b': {'c': 2}}
obj2 = {'a': 1, 'b': {'c': 3}}

added, removed, updated = obj_diff(obj1, obj2)
print(f"Added: {added}")    # set()
print(f"Removed: {removed}") # set()
print(f"Updated: {updated}") # {('b', 'c')}
```

## API Reference

### `list_diff(lst1, lst2, pk, fields, /, diff_obj=0, strict_none_diff=False)`

Calculate differences between two lists of dictionaries.

**Parameters:**
- `lst1` (list[dict]): First list of dictionaries
- `lst2` (list[dict]): Second list of dictionaries
- `pk` (str | list[str]): Primary key field or list of fields

- `fields` (list[str]): List of fields to compare

- `diff_obj` (int): Object diff level
  - `0` = No diff (default)
  - `1` = Shallow diff (only expand first level)
  - `-1` = Deep diff (recursively expand all levels)

- `strict_none_diff` (bool): Whether to strictly distinguish between missing values and None values

**Returns:**
- Tuple containing three elements: (removed primary keys, added primary keys, updated primary keys or details)

- If `lst1` is considered old data and `lst2` is new data, then corresponding to (removed records, added records, updated records)

- When `diff_obj` is not 0, the third return value is a dictionary containing object-level diff details

### `obj_diff(obj1, obj2)`

Calculate differences between two objects.

**Parameters:**
- `obj1`: First object
- `obj2`: Second object

**Returns:**
- Tuple containing three sets: (added paths, removed paths, updated paths)

- Paths are represented as tuples, e.g. `('user', 'profile', 'name')`

### `as_hashable(val, converters={}, prop_path=tuple())`

Convert value to hashable form for comparison. **Important: When using object-level diff, dictionary objects must be converted through this function first.**

**Parameters:**
- `val`: Value to convert
- `converters`: Custom converter dictionary, format: `{type: conversion_function}`

- `prop_path`: Property path for recursive conversion

**Returns:**
- Hashable object (dict converted to DICT class, list converted to LIST class, set converted to SET class)

**Conversion Rules:**
- `dict` → `DICT` (recursively convert values)
- `list` → `LIST` (recursively convert elements)
- `set` → `SET` (elements must already be hashable)

**Example:**
```python
from listdiff2 import as_hashable

# Convert complex object to hashable form
complex_obj = {
    'nested': {
        'list': [1, 2, 3],
        'dict': {'a': 1, 'b': 2}
    }
}

hashable_obj = as_hashable(complex_obj)
# Now can be used for set operations and diff calculations
```

### `deep_get(obj, prop_path)`

Get deep property value from object. Often used in conjunction with object-level diff results.

**Parameters:**
- `obj`: Object to get value from
- `prop_path`: Property path tuple, e.g. `('user', 'profile', 'name')`

**Returns:**
- Property value at specified path
- If path doesn't exist, raises `KeyError` or `IndexError`

**Example:**
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

# Get deep property
email = deep_get(data, ('user', 'profile', 'contact', 'email'))
print(email)  # 'alice@example.com'

# Use with diff results
# Suppose we have diff result updated = {1: (set(), set(), {('user', 'profile', 'name')})}
# Can get difference values like this:
# old_value = deep_get(old_record, ('user', 'profile', 'name'))
# new_value = deep_get(new_record, ('user', 'profile', 'name'))
```

## Complete Example

### Using as_hashable and deep_get for deep diff analysis

```python
from listdiff2 import list_diff, as_hashable, deep_get

# Complex nested data
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
                'age': 26,  # age updated
                'contact': {'email': 'alice@new.com'}  # email updated
            }
        }
    }
]

# Convert to hashable objects
hashable_data1 = [as_hashable(item) for item in data1]
hashable_data2 = [as_hashable(item) for item in data2]

# Deep diff calculation
removed, added, updated = list_diff(
    hashable_data1, hashable_data2, 'id', ['user'], diff_obj=-1
)

print(f"Removed: {removed}")
print(f"Added: {added}")
print(f"Update details: {updated}")

# Use deep_get to get specific difference values
if updated:
    for record_id, diff_info in updated.items():
        added_paths, removed_paths, updated_paths = diff_info
        
        # Find original record
        old_record = next(item for item in data1 if item['id'] == record_id)
        new_record = next(item for item in data2 if item['id'] == record_id)
        
        print(f"\nRecord {record_id} differences:")
        for path in updated_paths:
            old_value = deep_get(old_record, path)
            new_value = deep_get(new_record, path)
            print(f"  Path {path}: {old_value} -> {new_value}")
```

## Performance Characteristics

- **High Performance Set Operations**: Based on Python built-in set operations, avoiding loop traversal

- **Memory Optimization**: Use generators and lazy computation to handle large datasets

- **Scalability**: Support for custom converters and complex data structures

## Use Cases

- **Database Synchronization**: Compare database table record differences

- **Spreadsheet Comparison**: Compare different versions of Excel/CSV data files

- **Data Synchronization**: Data change detection in ETL processes

- **API Response Comparison**: Test environment vs production environment API response differences

- **Log Analysis**: Identify log changes across different time periods

## Demo Examples

The project contains multiple demo examples located in the `examples/` directory:

- [`simple_diff_demo.py`](examples/simple_diff_demo.py) - Simple dictionary list comparison (500,000 data items)

- [`shallow_diff_demo.py`](examples/shallow_diff_demo.py) - First-level expanded object comparison (100,000 data items)

- [`deep_diff_demo.py`](examples/deep_diff_demo.py) - Deep expanded object comparison (10,000 data items)

- [`test_composite_key.py`](examples/test_composite_key.py) - Composite primary key functionality test

- [`run_all_demos.py`](examples/run_all_demos.py) - Run all demos

Run examples:
```bash
cd examples
python run_all_demos.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## FAQ

**Q: Why does object-level diff need to use `as_hashable` conversion first?**
A: Because dictionary objects themselves are not hashable and cannot be directly used for set operations. `as_hashable` converts dictionaries to hashable `DICT` class.

**Q: Does it support custom comparison logic?**
A: Yes, custom type conversion logic can be defined through the `as_hashable.converters` parameter.

**Q: What are the performance characteristics for large datasets?**
A: The library uses high-performance set operations and can handle millions of items in seconds.