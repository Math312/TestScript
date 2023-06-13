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

注意，此时会在运行脚本的目录生成一个文件`match_sequence.json`用于记录最优匹配结果。

在项目目录运行交织论元脚本如下：

```shell
python .\score\coref_scorer.py --ontology_file ./score/event_ontology.json --pred_file "./example/FNDEE_valid.json" --truth_file "./example/FNDEE_valid.json"  --match_sequence_file "./match_sequence.json"
```