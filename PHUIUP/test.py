def generate_subsets(itemset, size):
    """
    Tạo tất cả các tập con (k-1) từ itemset.
    """
    list_subset = []
    n = len(itemset)
    
    for i in range(n):
        subset = []
        for j in range(n):
            if i != j:
                subset.append(itemset[j])
        
        # if len(subset) == size:
        list_subset.append(subset)
    
    return list_subset

lst = generate_subsets([1], 3)
print(lst)
print(len(lst))
