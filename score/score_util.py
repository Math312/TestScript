import json
import logging
import scipy
import numpy as np

"""
:parameter pred_true_count 正确预测结果的数量
:parameter pred_count 所有预测结果的数量
P = 正确预测结果数量/所有预测结果的数量
"""


def get_p(pred_true_count, pred_count):
    return float(pred_true_count) / float(pred_count)


"""
:parameter pred_true_count 正确预测结果的数量
:parameter truth_count 所有标注结果的数量
R = 正确预测结果数量/所有标注结果的数量
"""


def get_r(pred_true_count, truth_count):
    return float(pred_true_count) / float(truth_count)


"""
:parameter p 准确率
:parameter r 召回率
f1 = 2 * P * R / ( P + R )
"""


def get_f1(p, r):
    return 2 * p * r / (p + r)


def get_p_r_f1(pred_true_count, pred_count, truth_count):
    p_score = get_p(pred_true_count, pred_count)
    r_score = get_r(pred_true_count, truth_count)
    f1 = get_f1(p_score, r_score)
    return p_score, r_score, f1


def compare_trigger(trigger1, trigger2):
    if trigger1["event_type"] > trigger2["event_type"]:
        return 1
    elif trigger1["event_type"] < trigger2["event_type"]:
        return -1
    if trigger1["trigger"]["text"] > trigger2["trigger"]["text"]:
        return 1
    elif trigger1["trigger"]["text"] < trigger2["trigger"]["text"]:
        return -1
    if trigger1["trigger"]["offset"] > trigger2["trigger"]["offset"]:
        return 1
    elif trigger1["trigger"]["offset"] < trigger2["trigger"]["offset"]:
        return -1
    return 0


def compare_argument(argument1, argument2):
    if argument1["role"] > argument2["role"]:
        return 1
    elif argument1["role"] < argument2["role"]:
        return -1
    if argument1["text"] > argument2["text"]:
        return 1
    elif argument1["text"] < argument2["text"]:
        return -1
    if argument1["offset"] > argument2["offset"]:
        return 1
    elif argument1["offset"] < argument2["offset"]:
        return -1
    return 0


def get_full_argument_unique_id(event_type, argument):
    return event_type + "@" + argument["role"] + "@" + argument["text"] + "[" + str(argument["offset"][0]) + "," + str(
        argument["offset"][1]) + "]"


def get_argument_unique_id(argument):
    return argument["text"] + "[" + str(argument["offset"][0]) + "," + str(argument["offset"][1]) + "]"


def get_trigger_unique_id(event_type, trigger):
    return event_type + "_" + trigger["text"] + "[" + str(trigger["offset"][0]) + "," + str(
        trigger["offset"][1]) + "]"


def get_trigger_name(event_type, trigger):
    return event_type + "_" + trigger["text"]


def get_event_type_id(event_type):
    return event_type


def compare_num(num1, num2):
    if num1 > num2:
        return 1
    elif num1 < num2:
        return -1
    return 0


def build_score_matrix(pred_list, truth_list, score_func, others):
    result = np.zeros((len(pred_list), len(truth_list)))
    for pred_idx, pred_item in enumerate(pred_list):
        for truth_idx, truth_item in enumerate(truth_list):
            result[pred_idx][truth_idx] = score_func(pred_item, truth_item, others)
    return result


def hungarian(pred_list, truth_list, score_func, others=None, post_process_func=None):
    score_matrix = build_score_matrix(pred_list, truth_list, score_func, others)
    row_idx, col_idx = scipy.optimize.linear_sum_assignment(score_matrix)
    if post_process_func:
        return post_process_func(pred_list, truth_list, score_func, score_matrix, row_idx, col_idx)
    else:
        return row_idx, col_idx


def read_event_ontology(file):
    with open(file, "r", encoding="utf-8") as fd:
        event_ontology = json.load(fd)
        return event_ontology


def check_document_line(pred_content, truth_content):
    pred_id_set = set()
    truth_id_set = set()
    for pred_document in pred_content:
        pred_id_set.add(int(pred_document["id"]))
    for truth_document in truth_content:
        truth_id_set.add(int(truth_document["id"]))
    check_result = pred_id_set.difference(truth_id_set)
    if len(check_result) != 0:
        logging.error("documents in prediction file and truth file not match")
    return check_result
