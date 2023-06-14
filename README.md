# 使用方法

评判参数有3类:

1. score/trigger_scorer.py: 对Trigger抽取以及多事件抽取进行评判
2. score/args_scorer.py: 对普通论元抽取结果进行评判
3. score/coref_scorer.py: 对交织论元抽取结果进行评判

各个命令的使用方法以及具体参数的含义可以通过'--help'进行查询，此处给出简单举例：

假设工程目录如下：

```
score
- trigger_scorer.py
- args_scorer.py
- args_scorer_v2.py
- coref_scorer.py
- event_ontology.json
example
- FNDEE_valid.json
```

在项目目录运行trigger评测脚本如下：

```shell
python .\score\trigger_scorer.py  --pred_file "./example/FNDEE_valid.json" --truth_file "./example/FNDEE_valid.json"
```

在项目目录运行普通论元评测脚本如下：
```shell
python .\score\args_scorer.py --ontology_file ./score/event_ontology.json --pred_file "./example/FNDEE_valid.json" --truth_file "./example/FNDEE_valid.json" 
```

```shell
python .\score\args_scorer_v2.py --ontology_file ./score/event_ontology.json --pred_file "./example/FNDEE_valid.json" --truth_file "./example/FNDEE_valid.json" 
```

注意:
1. 此时会在运行脚本的目录生成一个文件`match_sequence.json`用于记录最优匹配结果。
2. args_scorer_v2.py的计算速度较args_scorer.py更快，但无法得到所有的匹配结果。
3. args_scorer_v2.py提供了`普通论元但不考虑触发词和事件类型的准确性的F1`，而args_scorer.py不提供

在项目目录运行交织论元脚本如下：

```shell
python .\score\coref_scorer.py --ontology_file ./score/event_ontology.json --pred_file "./example/FNDEE_valid.json" --truth_file "./example/FNDEE_valid.json"  --match_sequence_file "./match_sequence.json"
```

注意：
1. 由于交织论元的计算需要计算出所有的最优匹配的可能性，因此无法避免要使用递归，请使用args_scorer.py生成的`match_sequence.json`会更加准确。

## 更新日志

1. trigger_scorer.py 提供
    - 事件类型F1: 只考虑事件类型(event_type)的准确性
    - 事件触发词F1: 只考虑事件类型(event_type)和触发词Text(trigger text)的准确性
    - 事件触发词F1: 考虑事件类型(event_type)、触发词(trigger text、offset)的准确性
2. args_trigger.py 提供
   - 普通论元但不考虑触发词和事件类型的准确性的F1
   - 普通论元(考虑触发词、事件类型、论元本身)的F1
3. 由于在不考虑事件类型和触发词的情况下，会出现如下问题：
   - 交织论元的计算会简化为某一个论元计算准确，因此甚至会比普通论元F1还高（根据竞赛评分标准文档可得），这里不再提供该功能。