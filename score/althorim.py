import numpy as np


def generate_matrix(a, b):
    maxl_mat = np.zeros((len(a) + 1, len(b) + 1))
    for i in range(1, maxl_mat.shape[0]):
        for j in range(1, maxl_mat.shape[1]):
            if a[i - 1] == b[j - 1]:
                maxl_mat[i][j] = maxl_mat[i - 1][j - 1] + 1
            else:
                maxl_mat[i][j] = max(maxl_mat[i - 1][j], maxl_mat[i][j - 1])
    return maxl_mat


def get_char_list(a, b):
    maxl_mat = generate_matrix(a, b)
    char_list = []
    for i in range(1, maxl_mat.shape[0]):
        for j in range(1, maxl_mat.shape[1]):
            if (maxl_mat[i][j] == maxl_mat[i - 1][j - 1] + 1) and (a[i - 1] == b[j - 1]):
                state_dict = {'value': maxl_mat[i][j], "x": i, "y": j, 'str': a[i - 1]}
                char_list.append(state_dict)
    return char_list


def adjust_char_list(a, b):
    char_list = get_char_list(a, b)
    adjusted_list = []
    max_length = np.int_(np.max(generate_matrix(a, b)))
    for k in range(max_length):
        adjusted_list.append([])
        for char in char_list:
            if char['value'] == k + 1:
                adjusted_list[k].append(char)
    return adjusted_list


def get_lcs(a, b):
    adjusted_list = adjust_char_list(a, b)
    lcs_list = []
    init_dict = {'str': '', 'x': 0, 'y': 0}
    lcs_list.append(init_dict)
    for v in range(len(adjusted_list)):
        new_list = lcs_list.copy()
        number = 0
        for d in lcs_list:
            for char in adjusted_list[v]:
                if (char['x'] > d['x']) and (char['y'] > d['y']):
                    new_str = d['str'] + char['str']
                    new_dict = {'str': new_str, 'x': char['x'], 'y': char['y']}
                    new_list.append(new_dict)
                    number = number + 1
                else:
                    pass
        lcs_list = new_list
        start_len = len(lcs_list) - number
        lcs_list = lcs_list[start_len:]
    return lcs_list


def get_lcs_set(a, b):
    list = get_lcs(a, b)
    result = set()
    for item in list:
        result.add(item["str"])
    return result


if __name__ == '__main__':
    print(get_lcs("湖南农业大学学习", "湖南大学农业学习"))
