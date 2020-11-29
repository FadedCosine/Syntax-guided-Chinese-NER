# CLUE 2020 中文细粒度NER任务

## 概述
BERT等预训练模型虽然能够极大程度地提取出文本上下文信息，学习出通用语言表征，但却忽略了文本数据中的语言学特征，比如说句法。而句法信息通常展现了字词之间的语言依赖关系，这其中就包括了两个维度的信息，一是词汇的Lattice信息，二是字词之间的句法依赖信息。加上Lattice信息增强模型，以求改进中文NER的效果，在最近的研究中屡见不鲜，如[Lattice LSTM](https://arxiv.org/pdf/1805.02023v4.pdf)、[FLAT](https://arxiv.org/pdf/2004.11795v2.pdf)。同样作为增强模型理解能力的语言知识，目前却还没有研究深耕于句法信息改进中文NER的模型表现。

在本项目的工作中，受机器阅读理解领域的模型[SG-Net](https://arxiv.org/abs/1908.05147)的启发，我们以一种Attention机制的方式，显式地利用句法依存树中句法信息，以求增强模型对于文本的理解能力，改进其在中文NER任务的表现。

如下样本及其文本的句法依存关系：
> {"text": "记者从东营市政府获悉，东营市目前对城市低收入住房困难家庭购买经济适用房实施货币化补贴政策。", "label": {"address": {"东营市": [[11, 13]]}, "government": {"东营市政府": [[3, 7]]}, "position": {"记者": [[0, 1]]}}}

|  From ID   | From Lexicon  |  To Lexicon   | To ID  |
|  ----  | ----  |  ----  | ----  | 
| 1 | 记者 | 获悉 | 4 |
| 2 | 从 | 获悉 | 4 |
| 3 | 东营市政府 | 从 | 2 |
| 4 | 获悉 | ##核心## | 0 |
| 5 | ， | 获悉 | 4 |
| 6 | 东营市 | 实施 | 17 |
| 7 | 目前 | 实施 | 17 |
| 8 | 对 | 实施 | 17 |
| 9 | 城市 | 低收入 | 10 |
| 10 | 低收入 | 住房 | 11 |
| 11 | 住房 | 家庭 | 13 |
| 12 | 困难 | 家庭 | 13 |
| 13 | 家庭 | 对 | 8 |
| 14 | 购买 | 对 | 8 |
| 15 | 经济 | 适用房 | 16 |
| 16 | 适用房 | 购买 | 14 |
| 17 | 实施 | 获悉 | 4 |
| 18 | 货币化 | 政策 | 20 |
| 19 | 补贴 | 货币化 | 18 |
| 20 | 政策 | 实施 | 17 |
| 21 | 。 | 获悉 | 4 |

如果要构建出一棵句法依存树，可以发现该句中的命名实体都作为完整的叶子结点出现在此句法依存树当中。因此，我们希望树中的每个结点去关注以此结点作为子树的树中所有叶子结点和此结点本身，这种Attention的机制既从句法中获益引导模型去关注可能的命名实体（命名实体常常作为句法依存树的叶子结点），又能使得模型获取Lattice的信息（句法依存分析的过程中就进行了分词，每个结点关注自己本身就获得了完整的Lattice信息）。具体地我们定义句法依存关注矩阵M如下：

$$
M =\left\{
\begin{aligned}
1, & &  \text{ if j} \in \text{ Leaf(i) or j == i} \\
0, &  & otherwise  \\
\end{aligned}
\right.
$$

定义句法引导的multi-head self-attention操作如下：
$$
A_i = Softmax(\frac{M(Q_i K_i)}{\sqrt{d_k}})
$$
其中$K_i$，$V_i$，$Q_i$分别表示对于第i个head，通过三个线性转换成的$n\times d_k$的key矩阵，$n\times d_v$的value矩阵和$n\times d_q$的query矩阵。

而后通过将$A_i$与$V_i$相乘得到输入句子的句法引导词表征如下：
$$
H_i = A_i V_i
$$

以上工作主要的代码在于
```text
├── models
|  └── bert_for_ner.py # 依据上述思想实现了BertCrfForNerWithSyn模型
├── processors　
|  ├──  dependency_parsing.py # 使用pyhanlp提取句法信息，实现构建句法依存树的函数
|  ├──  ner_seq.py # 把句法依存树信息传入CnerProcessor当中，并修改convert_examples_to_features函数，构建句法attention矩阵特征
|  └──  utils_ner.py # 改动_read_json函数，利用dependency_parsing.py中的函数提取句法信息
```

### 数据介绍

数据详细描述: https://www.cluebenchmarks.com/introduce.html

### 运行方式
1. 下载CLUE_NER数据集，运行以下命令：
```shell
python tools/download_clue_data.py --data_dir=./datasets --tasks=cluener
```
2. 从 https://huggingface.co/models 下载中文预训练模型chinese_roberta_wwm_large，预训练模型文件格式，比如:
```text
├── prev_trained_model　# 预训练模型
|  └── chinese_roberta_wwm_large
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

当前默认使用最后一个checkpoint模型作为预测模型，可通过修改scripts/run_ner_crf_for_predict.sh中的参数，使用--from_checkpoint指定checkpoint路径进行预测，或指定--from_all_checkpoints将依次load所有checkpoints进行预测。而后直接执行对应shell脚本，如：
```shell
sh scripts/run_ner_crf_for_predict.sh
```

### 模型列表

model_type目前支持**bert**和**albert**

**注意:** bert ernie bert_wwm bert_wwwm_ext等模型只是权重不一样，而模型本身主体一样，因此参数model_type=bert其余同理。

### 结果

Syntax-Guide chinese_roberta_wwm_large在test上为F1分数为0.80061 (见官方评测网站 https://www.cluebenchmarks.com/ner.html)，当前目录下的cluener.zip文件即为最终测试集的结果。

> 代码改进基于 https://github.com/CLUEbenchmark/CLUENER2020 