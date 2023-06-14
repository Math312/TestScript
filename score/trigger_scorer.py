import argparse
import json
import score_util
import logging


# def statistic_document_trigger_data(pred_document, truth_document):

def score_trigger_full(pred, truth, others=None):
    if score_util.get_trigger_unique_id(pred["event_type"], pred["trigger"]) == score_util.get_trigger_unique_id(
            truth["event_type"], truth["trigger"]):
        return -1
    else:
        return 0


def score_trigger_without_offset(pred, truth, others=None):
    if score_util.get_trigger_name(pred["event_type"], pred["trigger"]) == score_util.get_trigger_name(
            truth["event_type"], truth["trigger"]):
        return -1
    else:
        return 0


def score_event_type(pred, truth, others=None):
    if score_util.get_event_type_id(pred["event_type"]) == score_util.get_event_type_id(
            truth["event_type"]):
        return -1
    else:
        return 0


def post_process_function(pred_list, truth_list, score_func, score_matrix, row_idx, col_idx):
    row_result = []
    col_result = []
    for idx in range(0, len(row_idx)):
        if score_matrix[row_idx[idx]][col_idx[idx]] != 0:
            row_result.append(row_idx[idx])
            col_result.append(col_idx[idx])
    return row_result, col_result


def score(pred_file, truth_file):
    with open(pred_file, "r", encoding="utf-8") as pred_fd, open(truth_file, "r", encoding="utf-8") as truth_fd:
        pred_content = json.load(pred_fd)
        truth_content = json.load(truth_fd)
        score_util.check_document_line(pred_content, truth_content)
        correct_event_type_pred_count_sum = 0
        correct_trigger_text_pred_count_sum = 0
        correct_all_pred_count_sum = 0
        pred_count_sum = 0
        truth_count_sum = 0
        for (pred_document, truth_document) in zip(pred_content, truth_content):
            pred_event_list = pred_document["event_list"]
            truth_event_list = truth_document["event_list"]
            score_event_type_row_idx, score_event_type_col_idx = score_util.hungarian(pred_event_list,
                                                                                      truth_event_list,
                                                                                      score_event_type,
                                                                                      post_process_func=post_process_function)

            score_trigger_text_row_idx, score_trigger_text_col_idx = score_util.hungarian(pred_event_list,
                                                                                          truth_event_list,
                                                                                          score_trigger_without_offset,
                                                                                          post_process_func=post_process_function)
            score_all_row_idx, score_all_col_idx = score_util.hungarian(pred_event_list, truth_event_list,
                                                                        score_trigger_full,
                                                                        post_process_func=post_process_function)

            correct_event_type_pred_count_sum += len(score_event_type_row_idx)
            correct_trigger_text_pred_count_sum += len(score_trigger_text_row_idx)
            correct_all_pred_count_sum += len(score_all_row_idx)
            pred_count_sum += len(pred_event_list)
            truth_count_sum += len(truth_event_list)

        full_p, full_r, full_f1 = score_util.get_p_r_f1(correct_all_pred_count_sum, pred_count_sum, truth_count_sum)
        event_type_p, event_type_r, event_type_f1 = score_util.get_p_r_f1(correct_event_type_pred_count_sum,
                                                                          pred_count_sum, truth_count_sum)
        trigger_text_p, trigger_text_r, trigger_text_f1 = score_util.get_p_r_f1(correct_trigger_text_pred_count_sum,
                                                                                pred_count_sum, truth_count_sum)
        logging.info(
            "Event Type(Contain [Event Type]) \tP:{},R:{},F1:{}".format(event_type_p, event_type_r, event_type_f1))
        logging.info(
            "Trigger Text(Contain [Event Type][Trigger Text]) \tP:{},R:{},F1:{}".format(trigger_text_p, trigger_text_r,
                                                                                        trigger_text_f1))
        logging.info(
            "Full(Contain [Event Type][Trigger Text][Offset]) \tP:{},R:{},F1:{}".format(full_p, full_r, full_f1))


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
