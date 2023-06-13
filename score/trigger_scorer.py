import argparse
import json

import score_util
import logging


# def statistic_document_trigger_data(pred_document, truth_document):



def intersection(sorted_pred_list, sorted_truth_list):
    i_pred, i_truth = 0, 0
    result = []
    while i_pred < len(sorted_pred_list) and i_truth < len(sorted_truth_list):
        temp = score_util.compare_trigger(sorted_pred_list[i_pred], sorted_truth_list[i_truth])
        if temp == 0:
            result.append(sorted_pred_list[i_pred])
            i_pred += 1
            i_truth += 1
        elif temp < 0:
            i_pred += 1
        else:
            i_truth += 1
    return result


def score(pred_file, truth_file):
    with open(pred_file, "r", encoding="utf-8") as pred_fd, open(truth_file, "r", encoding="utf-8") as truth_fd:
        pred_content = json.load(pred_fd)
        truth_content = json.load(truth_fd)
        score_util.check_document_line(pred_content, truth_content)
        correct_pred_count_sum = 0
        pred_count_sum = 0
        truth_count_sum = 0
        for (pred_document, truth_document) in zip(pred_content, truth_content):
            pred_event_list = pred_document["event_list"]
            truth_event_list = truth_document["event_list"]
            sorted_pred_event_list = sorted(pred_event_list, key=lambda x: (
                x["event_type"], x["trigger"]["text"], x["trigger"]["offset"]))
            sorted_truth_event_list = sorted(truth_event_list, key=lambda x: (
                x["event_type"], x["trigger"]["text"], x["trigger"]["offset"]))
            intersection_list = intersection(sorted_pred_event_list, sorted_truth_event_list)
            correct_pred_count_sum += len(intersection_list)
            pred_count_sum += len(pred_event_list)
            truth_count_sum += len(truth_event_list)

        p = score_util.get_p(correct_pred_count_sum, pred_count_sum)
        r = score_util.get_r(correct_pred_count_sum, truth_count_sum)
        f1 = score_util.get_f1(p, r)
        logging.info("P:{},R:{},F1:{}".format(p, r, f1))


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("trigger_scorer.log")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    parser = argparse.ArgumentParser(description='Analyze the result of trigger')
    parser.add_argument('--pred_file', dest='pred_file', required=True,
                        help='The name of prediction file. Note: the index of document need to be same as that in the '
                             'truth file')
    parser.add_argument('--truth_file', dest='truth_file', required=True,
                        help='The name of truth file. Note: the index of document need to be same as that in the '
                             'prediction file')

    args = parser.parse_args()
    ## arg1:训练集结果 arg2:测试集结果
    score(args.pred_file, args.truth_file)
