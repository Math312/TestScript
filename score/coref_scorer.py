import json
import logging

from score import score_util
from score.score_util import check_document_line


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
    result = []
    for event_index, arguments_list in enumerate(pred_event_list):
        for argument in arguments_list["arguments"]:
            id = score_util.get_argument_unique_id(argument)
            origin = statistic_table.setdefault(arg_id_to_coref_dict[id], set())
            origin.add(event_index)
    for key in statistic_table:
        if len(statistic_table[key]) > 1:
            result.append(key)
    return result


def score_documents(pred_file, truth_file):
    with open(pred_file, "r", encoding="utf-8") as pred_fd, open(truth_file, "r", encoding="utf-8") as truth_fd:
        pred_content = json.load(pred_fd)
        truth_content = json.load(truth_fd)
        check_document_line(pred_content, truth_content)
        sum_pred_argument_count = 0
        sum_truth_argument_count = 0
        sum_correct_argument_count = 0
        for (pred_document, truth_document) in zip(pred_content, truth_content):
            pred_event_list = pred_document["event_list"]
            truth_event_list = truth_document["event_list"]
            truth_coref_arguments = truth_document["coref_arguments"]
            coref_dict, arg_id_to_dict = build_virtual_coref_dict(pred_event_list, truth_coref_arguments)
            coref_items = extract_coref_item(pred_event_list, coref_dict, arg_id_to_dict)
            print(len(coref_items))

        # p = score_util.get_p(sum_correct_argument_count, sum_pred_argument_count)
        # r = score_util.get_r(sum_correct_argument_count, sum_truth_argument_count)
        # f1 = score_util.get_f1(p, r)
        # logging.info("P:{},R:{},F1:{}".format(p, r, f1))


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("scorer.log")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    # read_file("../test_file/pred_data.json", "../test_file/truth_data.json")
    event_ontology = score_util.read_event_ontology("event_ontology.json")
    score_documents("../test_file/truth_data.json", "../test_file/truth_data.json")
    # score("../test_file/error_file.json", "../test_file/error_file.json", event_ontology)
    # score("../data/FNDEE_valid.json", "../data/FNDEE_valid.json", event_ontology)
