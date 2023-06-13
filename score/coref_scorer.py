import copy
import json
import logging
import argparse
import score_util
from score_util import check_document_line


def build_match_coref_dict(pred_arguments_list, truth_argument_list, coref_arguments):
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


def build_virtual_coref_dict(pred_event_list, coref_arguments):
    coref_dict = dict()
    arg_id_to_coref = dict()
    index = 0
    for coref_list in coref_arguments:
        coref_dict[index] = coref_list
        for argument in coref_list:
            id = score_util.get_argument_unique_id(argument)
            arg_id_to_coref[id] = index
        index += 1
    text_to_coref = dict()
    for arguments_list in pred_event_list:
        for argument in arguments_list["arguments"]:
            id = score_util.get_argument_unique_id(argument)
            if id not in arg_id_to_coref:
                text = argument["text"]
                if text in text_to_coref:
                    coref_dict[text_to_coref[text]].append(argument)
                    arg_id_to_coref[id] = text_to_coref[text]
                else:
                    coref_dict[index] = [argument]
                    arg_id_to_coref[id] = index
                    text_to_coref[text] = index
                    index += 1
    return coref_dict, arg_id_to_coref


def extract_coref_item(pred_event_list, coref_virtual_dict, arg_id_to_coref_dict):
    statistic_table = dict()
    statistic_map = dict()
    result = []
    for event_index, arguments_list in enumerate(pred_event_list):
        for argument in arguments_list["arguments"]:
            id = score_util.get_argument_unique_id(argument)
            origin = statistic_table.setdefault(arg_id_to_coref_dict[id], set())
            origin.add(event_index)
            origin_list = statistic_map.setdefault(arg_id_to_coref_dict[id], [])
            origin_list.append({
                "event_id": event_index,
                "argument": argument
            })
    for key in statistic_table:
        if len(statistic_table[key]) <= 1:
            result.append(key)
    for key in result:
        del statistic_table[key]
    return statistic_table, statistic_map


def get_all_match_sequence(match_sequence_content, index):
    if index == len(match_sequence_content) - 1:
        return match_sequence_content[index]
    else:
        result = []
        next = get_all_match_sequence(match_sequence_content, index + 1)
        for sequences in match_sequence_content[index]:
            for other_sequence in next:
                temp = []
                temp.extend(sequences)
                temp.extend(other_sequence)
                result.append(temp)
    return result


def get_correct_pred_event_indexes(match_sequence):
    result = set()
    result_map = dict()
    for pair in match_sequence:
        result.add(pair[1])
        result_map[pair[1]] = pair[0]
    return result, result_map


def score_documents(pred_file, truth_file, match_sequence_file):
    with open(pred_file, "r", encoding="utf-8") as pred_fd, open(truth_file, "r", encoding="utf-8") as truth_fd, open(
            match_sequence_file, "r", encoding="utf-8") as match_fd:
        pred_content = json.load(pred_fd)
        truth_content = json.load(truth_fd)
        match_sequence_content = json.load(match_fd)
        check_document_line(pred_content, truth_content)
        sum_pred_argument_count = 0
        sum_truth_argument_count = 0
        sum_correct_argument_count = 0
        for (pred_document, truth_document, match_sequence_result) in zip(pred_content, truth_content,
                                                                          match_sequence_content):
            pred_event_list = pred_document["event_list"]
            truth_event_list = truth_document["event_list"]
            truth_coref_arguments = truth_document["coref_arguments"]
            all_match_sequences = []
            if len(match_sequence_result["match_sequences_data"]) > 0:
                all_match_sequences = get_all_match_sequence(match_sequence_result["match_sequences_data"], 0)
            coref_dict, arg_id_to_dict = build_virtual_coref_dict(pred_event_list, truth_coref_arguments)
            coref_items, coref_statistic_map = extract_coref_item(pred_event_list, coref_dict, arg_id_to_dict)
            pred_coref_data_count = len(coref_items)
            sum_pred_argument_count += pred_coref_data_count
            truth_coref_dict, truth_arg_id_to_dict = build_virtual_coref_dict(truth_event_list, truth_coref_arguments)
            truth_coref_items, truth_coref_statistic_map = extract_coref_item(truth_event_list, truth_coref_dict,
                                                                              truth_arg_id_to_dict)
            truth_coref_data_count = len(truth_coref_items)
            sum_truth_argument_count += truth_coref_data_count
            match_coref_dict, match_arg_id_to_dict = build_match_coref_dict(pred_event_list, truth_event_list,
                                                                            truth_coref_arguments)
            max_coref_score = 0
            for match_sequence_once in all_match_sequences:
                correct_pred_event_set, correct_pred_event_map = get_correct_pred_event_indexes(match_sequence_once)
                copy_coref_items = copy.deepcopy(coref_items)
                for coref_item in coref_items.keys():
                    sub_result = copy_coref_items[coref_item].difference(correct_pred_event_set)
                    if len(sub_result) != 0:
                        del copy_coref_items[coref_item]
                for key in list(copy_coref_items.keys()):
                    arguments = coref_statistic_map[key]
                    label = False
                    for argument in arguments:
                        truth_event = truth_event_list[correct_pred_event_map[argument["event_id"]]]
                        truth_argument_set = set()
                        for truth_argument in truth_event["arguments"]:
                            if truth_argument["role"] == argument["argument"]["role"]:
                                truth_argument_set.add(
                                    match_arg_id_to_dict.get(score_util.get_argument_unique_id(truth_argument)))
                        if match_arg_id_to_dict.get(
                                score_util.get_argument_unique_id(argument["argument"])) in truth_argument_set:
                            label = True
                            break
                    if not label:
                        del copy_coref_items[key]
                if max_coref_score < len(copy_coref_items):
                    max_coref_score = len(copy_coref_items)
            sum_correct_argument_count += max_coref_score
        p = score_util.get_p(sum_correct_argument_count, sum_pred_argument_count)
        r = score_util.get_r(sum_correct_argument_count, sum_truth_argument_count)
        f1 = score_util.get_f1(p, r)
        logging.info("P:{},R:{},F1:{}".format(p, r, f1))


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("coref_scorer.log")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    parser = argparse.ArgumentParser(description='Analyze the result of coref item.')
    parser.add_argument('--ontology_file', dest='ontology_file', required=True,
                        help='The event ontology file. It has been given in the Folder \"score/event_ontology.json\"')
    parser.add_argument('--pred_file', dest='pred_file', required=True,
                        help='The name of prediction file. Note: the index of document need to be same as that in the '
                             'truth file')
    parser.add_argument('--truth_file', dest='truth_file', required=True,
                        help='The name of truth file. Note: the index of document need to be same as that in the '
                             'prediction file')
    parser.add_argument('--match_sequence_file', dest='match_sequence_file', required=True,
                        help='The name of match sequence file. Note: That file can be generated by the script '
                             'args_scorer.py.')
    args = parser.parse_args()

    event_ontology = score_util.read_event_ontology(args.ontology_file)
    ## arg1:训练集结果 arg2:测试集结果 arg3: args_scores.py会生成一个文件默认名字未match_sequence.json，就是该文件
    score_documents(args.pred_file, args.truth_file, args.match_sequence_file)
