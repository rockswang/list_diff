# -*- coding: utf-8 -*-
# ruff: noqa: E731 E701
from itertools import groupby

# Define specialized types for hashing to avoid confusion
class DICT(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))
class LIST(tuple): pass
class SET(frozenset): pass

def deep_get(obj, prop_path):
    """
    Get deep property value from object
    
    Args:
        obj: Object to get value from
        prop_path: Property path tuple, e.g. ('user', 'profile', 'name')
    
    Returns:
        Property value at specified path
    
    Raises:
        KeyError: When key in path doesn't exist
        IndexError: When index in path is out of range
    
    Example:
        >>> data = {'user': {'profile': {'name': 'Alice'}}}
        >>> deep_get(data, ('user', 'profile', 'name'))
        'Alice'
    """
    pth = list(prop_path)[::-1]
    while pth: obj = obj[pth.pop()]
    return obj


def as_hashable(val, converters={}, prop_path = tuple()):
    """
    Convert value to hashable form to ensure it can be used in set operations
    
    Important: When using object-level diff, dictionary objects must be converted through this function first
    
    Args:
        val: Value to convert
        converters: Custom converter dictionary, format: {type: conversion_function}
        prop_path: Property path for recursive conversion
    
    Returns:
        Hashable object
    
    Conversion rules:
        - dict -> DICT (recursively convert values)
        - list -> LIST (recursively convert elements)
        - set -> SET (elements must already be hashable)
    
    Example:
        >>> complex_obj = {'nested': {'list': [1, 2, 3]}}
        >>> hashable_obj = as_hashable(complex_obj)
        >>> type(hashable_obj)
        <class 'list_diff.list_diff.DICT'>
    """
    if (fn := converters.get(ty := type(val))):
        try:
            val = fn(val, prop_path, ty)
            ty = type(val)
        except:  # noqa: E722
            pass # Conversion function threw exception, continue with default rules
    if ty is dict:
        return DICT((k, as_hashable(v, converters, prop_path + (k,))) for k, v in val.items())
    elif ty is list:
        return LIST(as_hashable(v, converters, prop_path + (i, )) for i, v in enumerate(val))
    elif ty is set:
        return SET(val)
    else:
        return val

def list_diff(lst1, lst2, pk, fields, /, diff_obj=0, strict_none_diff=False):
    """
    Calculate differences between two lists of dictionaries
    
    Args:
        lst1: First list of dictionaries
        lst2: Second list of dictionaries
        pk: Primary key field or list of fields
        fields: List of fields to compare
        diff_obj: Object diff level
            - 0: No diff (default)
            - 1: Shallow diff (only expand first level)
            - -1: Deep diff (recursively expand all levels)
        strict_none_diff: Whether to strictly distinguish between missing values and None values
    
    Returns:
        Tuple containing three elements: (removed primary keys, added primary keys, updated primary keys or details)
        
        If lst1 is considered old data and lst2 is new data, then corresponding to:
            - Removed records
            - Added records
            - Updated records
        
        When diff_obj is not 0, the third return value is a dictionary containing object-level diff details:
            {primary_key: (added path set, removed path set, updated path set)}
    
    Note:
        - When using object-level diff, it's recommended to convert dictionary objects through as_hashable first
        - Primary key fields are automatically excluded from comparison fields
    
    Example:
        >>> list1 = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        >>> list2 = [{'id': 1, 'name': 'Alice'}, {'id': 3, 'name': 'Charlie'}]
        >>> removed, added, updated = list_diff(list1, list2, 'id', ['name'])
        >>> removed
        {2}
        >>> added
        {3}
        >>> updated
        set()
    """

    NONE = object() if strict_none_diff else None # In strict mode, use this singleton to represent missing field

    def _flat(_set): # Flatten elements within set
        def _deepflat(o, fidx, pref): # Recursively flatten
            if (t := type(o)) is DICT: # Original type is dict, add dict keys as subkeys
                for k, v in o.items(): _deepflat(v, fidx + 1, pref + (k,))
            elif t is LIST: # Original type is list, add index integers as subkeys
                for i, v in enumerate(o): _deepflat(v, fidx + 1, pref + (i,))
            else:
                res.add((pref, o))

        res = set() # Result set
        for tt in _set:
            kk = tt[0:pkn] # Primary key combination, as prefix
            if diff_obj == 1: # No deep expansion
                res.update((((kk, ff[i]), v) for i, v in enumerate(tt) if i >= pkn)) # Non-primary key values split by field
                continue
            for i, v in enumerate(tt): # Deep recursive expansion
                if i < pkn: continue # Skip primary keys
                _deepflat(v, i, (kk, ff[i]))
        return res
        

    if diff_obj not in (0, 1, -1):
        raise ValueError('diff_obj parameter error')
    combo_pk = type(pk) is not str # Whether it's composite primary key
    pk = tuple(pk) if combo_pk else (pk,) # Unify to composite primary key
    pkn = len(pk)
    fields = set(fields) - set(pk) # Remove all primary key fields
    ff = [*pk, *fields] # All fields after deduplication, ensuring primary keys come first
    set1 = {tuple(o.get(f, NONE) for f in ff) for o in lst1} # Create tuples for each dict including primary key field values, convert list to set
    set2 = {tuple(o.get(f, NONE) for f in ff) for o in lst2}
    dif1 = set1 - set2 # Difference set, including left-side additions and updates
    dif2 = set2 - set1
    difpk1 = {t[0:pkn] for t in dif1} # Extract primary key part from each tuple in difference set
    difpk2 = {t[0:pkn] for t in dif2}
    add1 = difpk1 - difpk2 # Difference set filters out additions
    add2 = difpk2 - difpk1
    upd = difpk1 - add1 # The remainder (i.e., intersection) are updates
    if diff_obj == 0: # No object-level diff, return directly
        if combo_pk:
            return add1, add2, upd
        else: # Non-composite primary key, restore result to string set instead of tuple set
            return {v[0] for v in add1}, {v[0] for v in add2}, {v[0] for v in upd}

    set1 = _flat({t for t in set1 if t[0:pkn] in upd}) # Reuse set1, filter updated records, then flatten to 2D set
    set2 = _flat({t for t in set2 if t[0:pkn] in upd}) # set2 ditto
    dif1 = set1 - set2
    dif2 = set2 - set1
    difpk1 = {t[0] for t in dif1}
    difpk2 = {t[0] for t in dif2}
    subadd1 = difpk1 - difpk2
    subadd2 = difpk2 - difpk1
    subupd = difpk1 - subadd1
    # print(subupd)
    fn = lambda t: t[0] # Get primary key for sorting and grouping
    subadd1, subadd2, subupd = [{k: set(e[1:] for e in g) for k, g in groupby(sorted(st, key=fn), key=fn)} # Group by primary key (sorted)
        for st in (subadd1, subadd2, subupd)]
    fn = lambda d, k: {v[0] for v in s} if (s := d.get(k, set())) and diff_obj == 1 else s # For single-level expansion, convert subkey tuple to first element
    # Update object deep diff result format: dict(pk=(add1_set, add2_set, upd_set))
    deepupd = {k: (fn(subadd1, k), fn(subadd2, k), fn(subupd, k)) for k in upd}
    if combo_pk:
        return add1, add2, deepupd
    else: # Non-composite primary key, restore result to string set instead of tuple set
        return {v[0] for v in add1}, {v[0] for v in add2}, {k[0]: v for k, v in deepupd.items()}


def obj_diff(obj1, obj2):
    """
    Calculate differences between two objects
    
    Args:
        obj1: First object
        obj2: Second object
    
    Returns:
        Tuple containing three sets: (added paths, removed paths, updated paths)
        
        Paths are represented as tuples, e.g. ('user', 'profile', 'name')
    
    Note:
        - This function internally uses list_diff, supports deep object comparison
        - Paths start from root level, excluding wrapped primary keys
    
    Example:
        >>> obj1 = {'a': 1, 'b': {'c': 2}}
        >>> obj2 = {'a': 1, 'b': {'c': 3}}
        >>> added, removed, updated = obj_diff(obj1, obj2)
        >>> added
        set()
        >>> removed
        set()
        >>> updated
        {('b', 'c')}
    """
    dif = list_diff([as_hashable(dict(k=1, v=obj1))], [as_hashable(dict(k=1, v=obj2))], 'k', ['v'], diff_obj=-1)
    add1, add2, upd = list(dif[2].values())[0]
    return {t[1:] for t in add1}, {t[1:] for t in add2}, {t[1:] for t in upd}


