import json
import logging

from score.althorim import get_lcs, get_lcs_set


def analyze_coref(truth_file):
    with open(truth_file, "r", encoding="utf-8") as truth_fd:
        truth_content = json.load(truth_fd)
        statistic_count = 0
        coref_arguments_count = 0
        doc_count = 0
        static_map = dict()
        for document in truth_content:
            coref_arguments = document["coref_arguments"]
            if len(coref_arguments) > 0:
                static_map.setdefault(len(coref_arguments), 0)
                static_map[len(coref_arguments)] += 1
                doc_count += 1
            for coref_argument in coref_arguments:
                coref_arguments_count += 1
                cache = set()
                for argument in coref_argument:
                    cache.add(argument["text"])
                cache_list = list(cache)
                for i in range(0, len(cache_list)):
                    for j in range(i + 1, len(cache_list)):
                        lcs_set = get_lcs_set(cache_list[i], cache_list[j])
                        intersection_rs = lcs_set.intersection(cache)
                        if len(intersection_rs) != 0:
                            statistic_count += 1
        print(static_map)
        print("doc_count: {},coref_arguments_count:{}, statistic_count:{}".format(doc_count, coref_arguments_count,
                                                                                  statistic_count))


def cal_coref_arguments(truth_file):
    with open(truth_file, "r", encoding="utf-8") as truth_fd:
        truth_content = json.load(truth_fd)
        static_map = dict()
        match_count = 0
        match_map = dict()
        correct_count = 0
        for document in truth_content:
            argument_text_set = set()
            event_list = document["event_list"]
            coref_arguments = document["coref_arguments"]
            doc_coref_text_set = set()
            key_set_map = dict()
            for event in event_list:
                for argument in event["arguments"]:
                    argument_text_set.add(argument["text"])
            argument_text_list = list(argument_text_set)
            for i in range(0, len(argument_text_list)):
                for j in range(i + 1, len(argument_text_list)):
                    doc_coref_text_set = doc_coref_text_set.union(
                        get_lcs_set(argument_text_list[i], argument_text_list[j]))
                    for text in doc_coref_text_set:
                        key_set_map.setdefault(text, set())
                        key_set_map[text].add(argument_text_list[i])
                        key_set_map[text].add(argument_text_list[j])
            coref_arguments_map = dict()
            for coref_argument in coref_arguments:
                cache = set()
                for argument in coref_argument:
                    cache.add(argument["text"])
                cache_list = list(cache)
                for i in range(0, len(cache_list)):
                    lcs_set = get_lcs_set(cache_list[0], cache_list[i])
                    for lcs in lcs_set:
                        coref_arguments_map.setdefault(lcs, set())
                        coref_arguments_map[lcs].add(cache_list[0])
                        coref_arguments_map[lcs].add(cache_list[i])

            for coref_argument in coref_arguments_map:
                if coref_argument in key_set_map and len(
                        coref_arguments_map[coref_argument].intersection(key_set_map[coref_argument])) > 2:
                    correct_count += 1
            static_map.setdefault(len(doc_coref_text_set), 0)
            static_map[len(doc_coref_text_set)] += 1
            if len(doc_coref_text_set) > 0:
                match_map.setdefault(len(doc_coref_text_set) - len(document["coref_arguments"]), 0)
                match_map[len(doc_coref_text_set) - len(document["coref_arguments"])] += 1
        sum = 0
        for key in static_map:
            if key > 0:
                sum += static_map[key]
        print("correct_count:{}".format(correct_count))
        print(match_map)
        print("match_count:{}".format(match_count))
        print(sum)
        print(static_map)


'''
对于训练集，argument中没有公共最长子串时，没有共指参数
对于验证集，argument中没有公共最长子串的有403个事件，没有共指参数的有398个事件
'''


def valid_coref_arguments(truth_file):
    with open(truth_file, "r", encoding="utf-8") as truth_fd:
        truth_content = json.load(truth_fd)
        count = 0
        for document in truth_content:
            argument_text_set = set()
            event_list = document["event_list"]
            doc_coref_text_set = set()
            for event in event_list:
                for argument in event["arguments"]:
                    argument_text_set.add(argument["text"])
            argument_text_list = list(argument_text_set)
            for i in range(0, len(argument_text_list)):
                for j in range(i + 1, len(argument_text_list)):
                    doc_coref_text_set = doc_coref_text_set.union(
                        get_lcs_set(argument_text_list[i], argument_text_list[j]))
            if len(doc_coref_text_set) == 0 and len(document["coref_arguments"]) == 0:
                count += 1
        print(count)


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
    # analyze_coref(truth_file="../data/FNDEE_train1.json")
    cal_coref_arguments("../data/FNDEE_train1.json")
    # valid_coref_arguments("../data/FNDEE_train1.json")
    # analyze_coref(truth_file="../data/FNDEE_valid.json")
    # cal_coref_arguments("../data/FNDEE_valid.json")
    # valid_coref_arguments("../data/FNDEE_valid.json")
