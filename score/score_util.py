import json

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


def get_argument_unique_id(argument):
    return argument["text"] + "[" + str(argument["offset"][0]) + "," + str(argument["offset"][1]) + "]"


def compare_num(num1, num2):
    if num1 > num2:
        return 1
    elif num1 < num2:
        return -1
    return 0


def read_event_ontology(file):
    with open(file, "r", encoding="utf-8") as fd:
        event_ontology = json.load(fd)
        return event_ontology



def check_document_line(pred_content, truth_content):
    pred_id_set = set()
    truth_id_set = set()
    for pred_document in pred_content:
        pred_id_set.add(pred_document["id"])
    for truth_document in truth_content:
        truth_id_set.add(truth_document["id"])
    check_result = pred_id_set == truth_id_set
    if not check_result:
        logging.error("documents in prediction file and truth file not match")
    return check_result