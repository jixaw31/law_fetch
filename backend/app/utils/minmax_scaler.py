def minmax_scale_with_range(values, min_range=0.1, max_range=0.9):
    """Scale values to custom range [min_range, max_range]"""
    min_val = min(values)
    max_val = max(values)
    
    if max_val == min_val:
        return [(min_range + max_range) / 2 for _ in values]
    
    # First scale to [0, 1]
    scaled = [(x - min_val) / (max_val - min_val) for x in values]
    
    # Then map to [min_range, max_range]
    return [min_range + s * (max_range - min_range) for s in scaled]