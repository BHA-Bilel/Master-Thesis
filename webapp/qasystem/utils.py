def inverse(data):
    rev_data = []
    i = len(data) - 1
    while i >= 0:
        rev_data.append(data[i])
        i -= 1
    return rev_data
