import bisect
import json

DATA_FILE_BASE_PATH = "../data/"

'''
    根据句子终止符，当前为
    1. 句号。
    将整个Document划分为多个sentence，返回每个sentence的Index范围。
    例如[A,B]，代表一个sentence在document中的索引为A~(B-1)
'''


def sentence_index_split(text):
    sentence_end_label = ["。"]
    index_spans = []
    span_heads = []
    start = 0
    for index, c in enumerate(text):
        if c in sentence_end_label:
            index_spans.append([start, index])
            span_heads.append(start)
            start = index + 1
    if start != len(text):
        index_spans.append([start, len(text)])
        span_heads.append(start)
    return index_spans, span_heads



def analyze_event_data(text, event, span_heads, coref_word_sets):
    trigger_start = event["trigger"]["offset"][0]
    trigger_sentence_index = bisect.bisect_left(span_heads, trigger_start)
    argument_in_other_sen_count = 0
    argument_count = 0
    argument_distances = []
    coref_argument_count = []
    for coref_word_set in coref_word_sets:
        coref_argument_count.append(0)
    for argument in event["arguments"]:
        argument_count += 1
        argument_sentence_index = bisect.bisect_left(span_heads, argument["offset"][0])
        if argument_sentence_index != trigger_sentence_index:
            argument_in_other_sen_count += 1
            argument_distance = argument_sentence_index - trigger_sentence_index
            argument_distances.append(argument_distance)
        for index, coref_word_set in enumerate(coref_word_sets):
            if argument["text"] in coref_word_set:
                coref_argument_count[index] += 1
    return argument_count, argument_in_other_sen_count, argument_distances, coref_argument_count


def process_origin_data():
    with open(DATA_FILE_BASE_PATH + "FNDEE_valid.json", "r", encoding="utf-8") as f:
        content = json.load(f)
        all_argument_count = 0
        all_argument_in_other_sen_count = 0
        all_argument_distances_map = {}
        all_coref_argument_count = 0
        for line in content:
            index_spans, span_heads = sentence_index_split(line["text"])
            coref_word_sets = []
            for coref_argsuments in line["coref_arguments"]:
                coref_word_set = set()
                for corf_argsument in coref_argsuments:
                    coref_word_set.add(corf_argsument["text"])
                coref_word_sets.append(coref_word_set)
            for event in line["event_list"]:
                argument_count, argument_in_other_sen_count, argument_distances, coref_argument_counts = analyze_event_data(
                    line["text"],
                    event, span_heads,
                    coref_word_sets)
                all_argument_count += argument_count
                all_argument_in_other_sen_count += argument_in_other_sen_count
                for argument_distance in argument_distances:
                    all_argument_distances_map.setdefault(argument_distance, 0)
                    all_argument_distances_map[argument_distance] += 1
                for coref_argument_count in coref_argument_counts:
                    if coref_argument_count > 1:
                        all_coref_argument_count += coref_argument_count
        print("非Trigger所在句包含参数占比：" + str(all_argument_in_other_sen_count / all_argument_count))
        print(all_argument_count)
        print(all_argument_in_other_sen_count)
        print(all_argument_distances_map)
        print(all_coref_argument_count)


if __name__ == '__main__':
    process_origin_data()
