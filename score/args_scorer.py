import json

import score_util
import logging
import heapq
import copy


# def statistic_document_trigger_data(pred_document, truth_document):

def intersection(sorted_pred_list, sorted_truth_list, compare, contain_all):
    i_pred, i_truth = 0, 0
    pred_data, truth_data = [], []
    while i_pred < len(sorted_pred_list) and i_truth < len(sorted_truth_list):
        temp = compare(sorted_pred_list[i_pred], sorted_truth_list[i_truth])
        if temp == 0:
            temp_pred_data, temp_truth_data = [], []
            temp_pred_data.append(sorted_pred_list[i_pred])
            temp_truth_data.append(sorted_truth_list[i_truth])
            if contain_all:
                while i_pred + 1 < len(sorted_pred_list) and score_util.compare_trigger(sorted_pred_list[i_pred],
                                                                                        sorted_pred_list[
                                                                                            i_pred + 1]) == 0:
                    temp_pred_data.append(sorted_pred_list[i_pred + 1])
                    i_pred += 1
                while i_truth + 1 < len(sorted_truth_list) and score_util.compare_trigger(sorted_truth_list[i_truth],
                                                                                          sorted_truth_list[
                                                                                              i_truth + 1]) == 0:
                    temp_truth_data.append(sorted_truth_list[i_truth + 1])
                    i_truth += 1
            i_pred += 1
            i_truth += 1
            pred_data.append(temp_pred_data)
            truth_data.append(temp_truth_data)
        elif temp < 0:
            i_pred += 1
        else:
            i_truth += 1
    return pred_data, truth_data


def compare_arguments(ontology, event_type, pred_arguments, truth_arguments, coref_dict, arg_id_to_coref):
    roles = ontology[event_type]
    for index, item in enumerate(pred_arguments[:]):
        if item["role"] not in roles:
            pred_arguments.remove(item)

    for index, item in enumerate(truth_arguments[:]):
        if item["role"] not in roles:
            truth_arguments.remove(item)
    local_score = 0
    pred_role_group = dict()
    truth_role_group = dict()
    for role in roles:
        pred_role_group[role] = []
        truth_role_group[role] = []
    for item in pred_arguments:
        id = score_util.get_argument_unique_id(item)
        pred_role_group[item["role"]].append(arg_id_to_coref[id])
    for item in truth_arguments:
        id = score_util.get_argument_unique_id(item)
        truth_role_group[item["role"]].append(arg_id_to_coref[id])
    for role in roles:
        pred_role_group[role].sort()
        truth_role_group[role].sort()
        pred_data, truth_data = intersection(pred_role_group[role], truth_role_group[role], score_util.compare_num,
                                             False)
        local_score += len(pred_data)
    return local_score


def find_max_sum(matrix):
    m, n = len(matrix), len(matrix[0])
    k = min(m, n)

    # 统计每个数字出现的频率
    freq = {}
    for i in range(m):
        for j in range(n):
            num = matrix[i][j]
            if num in freq:
                freq[num].append((i, j))
            else:
                freq[num] = [(i, j)]

    # 按照数字的降序排序
    sorted_nums = sorted(freq.keys(), reverse=True)

    # 记录每行和每列已选中的元素个数
    row_counts = [0] * m
    col_counts = [0] * n
    max_sum = 0
    selected_nums = []

    for num in sorted_nums:
        positions = freq[num]
        for i, j in positions:
            if row_counts[i] < k and col_counts[j] < k:
                max_sum += num
                selected_nums.append((i, j))
                row_counts[i] += 1
                col_counts[j] += 1
                break  # 只选择一个位置

    return max_sum


def find_max_score_seq(score_table, pred_visited, truth_visited):
    pred_label = True
    truth_label = True
    '''
    预测集与标注集任意一个匹配完毕，则匹配结束
    '''
    for label in pred_visited:
        if not label:
            pred_label = False
    for label in truth_visited:
        if not label:
            truth_label = False
    stop_label = pred_label or truth_label
    if stop_label:
        return 0, [[]]
    max_score = 0
    max_score_indexes = []
    '''
    选择未确定匹配项的truth 进行匹配
    [a,b]
    a为标注集index
    b为测试集index
    '''
    for i1, score_arr in enumerate(score_table):
        if not truth_visited[i1]:
            for i2, score in enumerate(score_arr):
                if not pred_visited[i2]:
                    if score > max_score:
                        max_score = score
                        max_score_indexes.clear()
                        max_score_indexes.append([i1, i2])
                    elif score == max_score:
                        max_score_indexes.append([i1, i2])
    '''存储 后续选择序列的最大分数'''
    max_other_score = 0
    '''存储 满足最大分数的 当前位置可以选择的序列'''
    score_index = []
    '''存储 满足最大分数的 后续位置可以选择的序列
    index 与 score_index一一对应，表示当前位置选择score_index[index]时，其达到最大score，后续序列可以是max_other_score_index[index]
    '''
    max_other_score_index = []
    for indexes in max_score_indexes:
        temp_pred_visited = copy.deepcopy(pred_visited)
        temp_truth_visited = copy.deepcopy(truth_visited)
        temp_pred_visited[indexes[1]] = True
        temp_truth_visited[indexes[0]] = True
        other_score, other_seq = find_max_score_seq(score_table, temp_pred_visited, temp_truth_visited)
        if other_score > max_other_score:
            max_other_score = other_score
            score_index.clear()
            score_index.append(indexes)
            max_other_score_index.clear()
            max_other_score_index.append(other_seq)
        elif other_score == max_other_score:
            score_index.append(indexes)
            max_other_score_index.append(other_seq)
    result_indexes = []

    '''
    这里做了两次去重，第一次去重是当前位置选[a,b]，后续序列可能重复，对后序序列集合的去重
    第二次去重是把当前序列与后序序列拼接后，可能出现重复，进行去重。
    '''
    for i, indexes in enumerate(score_index):
        temp = max_other_score_index[i]

        i1 = 0
        for i2, v2 in enumerate(temp):
            if len(v2) > 0:
                temp[i2] = sorted(v2, key=lambda x: (x[0], x[1]))
        i2 = 0
        while i2 < len(temp):
            temp[i1] = temp[i2]
            while i2 < len(temp):
                if temp[i2] == temp[i1]:
                    i2 += 1
                else:
                    break
            i1 += 1
        max_other_score_index[i] = temp[:i1]
        for temp2 in max_other_score_index[i]:
            temp2.append(indexes)
            temp2 = sorted(temp2, key=lambda x: (x[0], x[1]))
            result_indexes.append(temp2)
    i1_r = 0
    i2_r = 0
    while i2_r < len(result_indexes):
        result_indexes[i1_r] = result_indexes[i2_r]
        while i2_r < len(result_indexes):
            if result_indexes[i2_r] == result_indexes[i1_r]:
                i2_r += 1
            else:
                break
        i1_r += 1
    return max_other_score + max_score, result_indexes[:i1_r]


def compare_documents_arguments(doc_id, pred_event_list, truth_event_list, ontology, coref_dict, arg_id_to_coref):
    sum_score = 0
    document_truth_sequence = []
    for (pred_events, truth_events) in zip(pred_event_list, truth_event_list):
        score_arr = []
        for truth_event in truth_events:
            temp_arr = []
            # index_map = dict()
            for index, pred_event in enumerate(pred_events):
                score_once = compare_arguments(ontology, truth_event["event_type"], pred_event["arguments"],
                                               truth_event["arguments"], coref_dict, arg_id_to_coref)
                temp_arr.append(score_once)
            score_arr.append(temp_arr)
        seq_score, sequences = find_max_score_seq(score_arr, [False] * len(pred_events), [False] * len(truth_events))
        truth_sequences = []
        for sequence in sequences:
            temp_sequence = []
            for pair in sequence:
                temp_sequence.append([truth_events[pair[0]]["index"], pred_events[pair[1]]["index"]])
            truth_sequences.append(temp_sequence)

        sum_score += seq_score
        document_truth_sequence.append(truth_sequences)
        # sum_score += find_max_sum(score_arr)
    return sum_score, document_truth_sequence
    # logger.info("doc_id:{},max_score:{}".format(doc_id, sum_score))


def build_virtual_coref_dict(pred_arguments_list, truth_argument_list, coref_arguments):
    coref_dict = dict()
    arg_id_to_coref = dict()
    index = 0
    for coref_list in coref_arguments:
        coref_dict[index] = coref_dict
        for argument in coref_list:
            id = score_util.get_argument_unique_id(argument)
            arg_id_to_coref[id] = index
        index += 1
    for arguments_list in pred_arguments_list:
        for argument in arguments_list["arguments"]:
            id = score_util.get_argument_unique_id(argument)
            if id not in arg_id_to_coref:
                temp_arr = [argument]
                coref_dict[index] = temp_arr
                arg_id_to_coref[id] = index
                index += 1

    for arguments_list in truth_argument_list:
        for argument in arguments_list["arguments"]:
            id = score_util.get_argument_unique_id(argument)
            if id not in arg_id_to_coref:
                temp_arr = [argument]
                coref_dict[index] = temp_arr
                arg_id_to_coref[id] = index
                index += 1

    return coref_dict, arg_id_to_coref


def score(pred_file, truth_file, ontology):
    with open(pred_file, "r", encoding="utf-8") as pred_fd, open(truth_file, "r", encoding="utf-8") as truth_fd, open(
            "match_sequence.json", "w", encoding="utf-8") as sequence_writer:
        pred_content = json.load(pred_fd)
        truth_content = json.load(truth_fd)
        score_util.check_document_line(pred_content, truth_content)
        sum_pred_argument_count = 0
        sum_truth_argument_count = 0
        sum_correct_argument_count = 0
        match_sequence_json = []
        for (pred_document, truth_document) in zip(pred_content, truth_content):
            pred_event_list = pred_document["event_list"]
            truth_event_list = truth_document["event_list"]
            index = 0
            for pred_event in pred_event_list:
                pred_event["index"] = index
                index += 1
            index = 0
            for truth_event in truth_event_list:
                truth_event["index"] = index
                index += 1
            truth_coref_arguments = truth_document["coref_arguments"]
            coref_dict, arg_id_to_coref = build_virtual_coref_dict(pred_event_list, truth_event_list,
                                                                   truth_coref_arguments)
            sorted_pred_event_list = sorted(pred_event_list, key=lambda x: (
                x["event_type"], x["trigger"]["text"], x["trigger"]["offset"]))
            sorted_truth_event_list = sorted(truth_event_list, key=lambda x: (
                x["event_type"], x["trigger"]["text"], x["trigger"]["offset"]))
            pred_inter_event_list, truth_inter_event_list = intersection(sorted_pred_event_list,
                                                                         sorted_truth_event_list,
                                                                         score_util.compare_trigger, True)
            document_max_score, document_truth_sequence = compare_documents_arguments(pred_document["id"],
                                                                                      pred_inter_event_list,
                                                                                      truth_inter_event_list, ontology,
                                                                                      coref_dict,
                                                                                      arg_id_to_coref)
            match_sequence_json.append({
                "id": pred_document["id"],
                "match_sequences_data": document_truth_sequence
            })
            pred_arguments_count = 0
            truth_arguments_count = 0
            for event in pred_event_list:
                pred_arguments_count += len(event["arguments"])
            for event in truth_event_list:
                truth_arguments_count += len(event["arguments"])
            sum_pred_argument_count += pred_arguments_count
            sum_truth_argument_count += truth_arguments_count
            sum_correct_argument_count += document_max_score
        sequence_writer.write(json.dumps(match_sequence_json))
        p = score_util.get_p(sum_correct_argument_count, sum_pred_argument_count)
        r = score_util.get_r(sum_correct_argument_count, sum_truth_argument_count)
        f1 = score_util.get_f1(p, r)
        logging.info("P:{},R:{},F1:{}".format(p, r, f1))


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("args_scorer.log")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    event_ontology = score_util.read_event_ontology("event_ontology.json")
    ## arg1:训练集结果 arg2:测试集结果
    score("../test_file/pred_data.json", "../test_file/truth_data.json", event_ontology)
