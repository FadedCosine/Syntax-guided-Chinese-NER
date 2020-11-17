
### 数据介绍

数据详细描述: https://www.cluebenchmarks.com/introduce.html

### 运行方式
1. 下载CLUE_NER数据集，运行以下命令：
```shell
python tools/download_clue_data.py --data_dir=./datasets --tasks=cluener
```
2. 从 https://huggingface.co/models 下载中文预训练模型，预训练模型文件格式，比如:
```text
├── prev_trained_model　# 预训练模型
|  └── bert-base
|  | └── vocab.txt
|  | └── config.json
|  | └── pytorch_model.bin
```
3. 训练：

直接执行对应shell脚本，如：
```shell
sh scripts/run_ner_crf.sh
```
4. 预测

当前默认使用最后一个checkpoint模型作为预测模型，可通过--from_checkpoint指定checkpoint进行预测，或指定--from_all_checkpoints将依次load所有checkpoints进行预测。

### 模型列表

model_type目前支持**bert**和**albert**

**注意:** bert ernie bert_wwm bert_wwwm_ext等模型只是权重不一样，而模型本身主体一样，因此参数model_type=bert其余同理。

### 结果

bert_wwwm_ext在dev上为F1分数为0.8064

> 代码改进基于 https://github.com/CLUEbenchmark/CLUENER2020 