""" Named entity recognition fine-tuning: utilities to work with CLUENER task. """
import torch
import logging
import os
import copy
import json
import numpy as np
from .utils_ner import DataProcessor
logger = logging.getLogger(__name__)

class InputExample(object):
    """A single training/test example for token classification."""
    def __init__(self, guid, text_a, labels, lexicon_to_wordspan_dir=None, hpsg_list=None, leaves_list=None):
        """Constructs a InputExample.
        Args:
            guid: Unique id for the example.
            text_a: list. The words of the sequence.
            labels: (Optional) list. The labels for each word of the sequence. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.labels = labels
        self.lexicon_to_wordspan_dir = lexicon_to_wordspan_dir
        self.hpsg_list = hpsg_list
        self.leaves_list = leaves_list

    def __repr__(self):
        return str(self.to_json_string())
    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output
    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

class InputFeatures(object):
    """A single set of features of data."""
    def __init__(self, input_ids, input_mask, input_len,segment_ids, label_ids, input_span_mask=None):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids
        self.input_len = input_len
        self.input_span_mask = input_span_mask

    def __repr__(self):
        return str(self.to_json_string())

    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output

    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

def collate_fn(batch):
    """
    batch should be a list of (sequence, target, length) tuples...
    Returns a padded tensor of sequences sorted from longest to shortest,
    """
    all_input_ids, all_attention_mask, all_token_type_ids, all_lens, all_labels, all_input_span_mask = map(torch.stack, zip(*batch))
    max_len = max(all_lens).item()
    all_input_ids = all_input_ids[:, :max_len]
    all_attention_mask = all_attention_mask[:, :max_len]
    all_token_type_ids = all_token_type_ids[:, :max_len]
    all_labels = all_labels[:,:max_len]
    all_input_span_mask = all_input_span_mask[:, :max_len, :max_len]
    return all_input_ids, all_attention_mask, all_token_type_ids, all_lens, all_labels, all_input_span_mask

def convert_examples_to_features(examples,label_list,max_seq_length,tokenizer,
                                 cls_token_at_end=False,cls_token="[CLS]",cls_token_segment_id=1,
                                 sep_token="[SEP]",pad_on_left=False,pad_token=0,pad_token_segment_id=0,
                                 sequence_a_segment_id=0,mask_padding_with_zero=True,):
    """ Loads a data file into a list of `InputBatch`s
        `cls_token_at_end` define the location of the CLS token:
            - False (Default, BERT/XLM pattern): [CLS] + A + [SEP] + B + [SEP]
            - True (XLNet/GPT pattern): A + [SEP] + B + [SEP] + [CLS]
        `cls_token_segment_id` define the segment id associated to the CLS token (0 for BERT, 2 for XLNet)
    """
    """
    examples 中加入了提取出的句法信息，包括每个句法结点的词汇到单字的范围字典：lexicon_to_wordspan_dir ，和对应词汇的在依存树当中结点的覆盖范围：hpsg_list
    """
    label_map = {label: i for i, label in enumerate(label_list)}
    features = []
    for (ex_index, example) in enumerate(examples):
        if ex_index % 10000 == 0:
            logger.info("Writing example %d of %d", ex_index, len(examples))
        tokens = tokenizer.tokenize(example.text_a)
        label_ids = [label_map[x] for x in example.labels]
        # 需要把 基于lexicon的hpsg_list扩展成基于char的hpsg_list，注意，这里 都还是从1开始的编号
        char_hpsg_list = []
        # char_leaves_list[i]表示[i]个字的所有叶结点lexicon的所有单字组成的列表
        char_leaves_list = [[] for _ in range(len(label_ids))]
        for lexicon_number, lexicon_span in example.lexicon_to_wordspan_dir.items():
            # hpsg
            #example.hpsg_list[lexicon_number-1]是当前lexicon的hpsg的span
            cur_lexicon_min_word_number = example.lexicon_to_wordspan_dir[example.hpsg_list[lexicon_number-1][0]][0]
            cur_lexicon_max_word_number = example.lexicon_to_wordspan_dir[example.hpsg_list[lexicon_number-1][1]][1]
            # for char_number in range(lexicon_span[0], lexicon_span[1] + 1):
            #     char_hpsg_list.append((cur_lexicon_min_word_number, cur_lexicon_max_word_number))

            # 按照毕设代码的做法，只有第一个字作为句法依存树真正的结点
            char_hpsg_list.append((cur_lexicon_min_word_number, cur_lexicon_max_word_number))
            for char_number in range(lexicon_span[0] + 1, lexicon_span[1] + 1):
                # 对于一个lexicon里除了首字的其他字，span为这个lexicon本身的span
                # char_hpsg_list.append((lexicon_span[0], lexicon_span[1]))
                char_hpsg_list.append((char_number, char_number))

            #leaves
            cur_leaf_list = []
            for leaf_lexicon_number in example.leaves_list[lexicon_number-1]:
                for char_number in range(example.lexicon_to_wordspan_dir[leaf_lexicon_number][0], example.lexicon_to_wordspan_dir[leaf_lexicon_number][1] + 1):
                    cur_leaf_list.append(char_number)
            for char_number in range(lexicon_span[0], lexicon_span[1] + 1):
                char_leaves_list[char_number-1].extend(cur_leaf_list)
        
        

        hpsg_span_mask = np.zeros((len(char_hpsg_list), len(char_hpsg_list)))
        #每个单字关注其所属lexicon的所有祖先lexicon的所有单字及其所属lexicon的所有兄弟单字
        # for idx, span_list in enumerate(char_hpsg_list):
        #     # 把从1开始的编号换成从0开始的idx
        #     start_idx = span_list[0] - 1
        #     end_idx = span_list[1] - 1
        #     hpsg_span_mask[start_idx:end_idx + 1, idx] = 1

        #每个单字关注其所属lexicon的所有兄弟单字和其所属lexicon的子树所包括的所有叶子lexicon的所有单字
        for idx, leaf_list in enumerate(char_leaves_list):
            # 把从1开始的编号换成从0开始的idx
            for leaf_char_number in leaf_list:
                hpsg_span_mask[idx, leaf_char_number-1] = 1
            

        # Account for [CLS] and [SEP] with "- 2".
        special_tokens_count = 2
        if len(tokens) > max_seq_length - special_tokens_count:
            tokens = tokens[: (max_seq_length - special_tokens_count)]
            label_ids = label_ids[: (max_seq_length - special_tokens_count)]

            hpsg_span_mask = hpsg_span_mask[: (max_seq_length - special_tokens_count), : (max_seq_length - special_tokens_count)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids:   0   0  0    0    0     0       0   0   1  1  1  1   1   1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids:   0   0   0   0  0     0   0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambiguously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens += [sep_token]
        label_ids += [label_map['O']]
        segment_ids = [sequence_a_segment_id] * len(tokens)

        if cls_token_at_end:
            tokens += [cls_token]
            label_ids += [label_map['O']]
            segment_ids += [cls_token_segment_id]
        else:
            tokens = [cls_token] + tokens
            label_ids = [label_map['O']] + label_ids
            segment_ids = [cls_token_segment_id] + segment_ids

        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        input_len = len(label_ids)
        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        # 训练时使用的句法mask矩阵
        input_span_mask = np.zeros((max_seq_length, max_seq_length))
        if pad_on_left:
            input_ids = ([pad_token] * padding_length) + input_ids
            input_mask = ([0 if mask_padding_with_zero else 1] * padding_length) + input_mask
            segment_ids = ([pad_token_segment_id] * padding_length) + segment_ids
            label_ids = ([pad_token] * padding_length) + label_ids
            
            if cls_token_at_end:
                input_span_mask[padding_length: padding_length+hpsg_span_mask.shape[0], padding_length: padding_length+hpsg_span_mask.shape[1]] = hpsg_span_mask
            else:
                input_span_mask[padding_length+1: padding_length+hpsg_span_mask.shape[0], padding_length+1: padding_length+hpsg_span_mask.shape[1]] = hpsg_span_mask
        else:
            input_ids += [pad_token] * padding_length
            input_mask += [0 if mask_padding_with_zero else 1] * padding_length
            segment_ids += [pad_token_segment_id] * padding_length
            label_ids += [pad_token] * padding_length
            if cls_token_at_end:
                input_span_mask[:hpsg_span_mask.shape[0], :hpsg_span_mask.shape[1]] = hpsg_span_mask
            else:
                input_span_mask[1:1+hpsg_span_mask.shape[0], 1:1+hpsg_span_mask.shape[1]] = hpsg_span_mask


        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length
        assert len(label_ids) == max_seq_length
        assert input_span_mask.shape[0] == max_seq_length
        assert input_span_mask.shape[1] == max_seq_length

        if ex_index < 2:
            logger.info("*** Example ***")
            logger.info("guid: %s", example.guid)
            logger.info("tokens: %s", " ".join([str(x) for x in tokens]))
            logger.info("input_ids: %s", " ".join([str(x) for x in input_ids]))
            logger.info("input_mask: %s", " ".join([str(x) for x in input_mask]))
            logger.info("segment_ids: %s", " ".join([str(x) for x in segment_ids]))
            logger.info("label_ids: %s", " ".join([str(x) for x in label_ids]))
            logger.info("input_span_mask:")
            for row in input_span_mask:
                logger.info("%s", " ".join([str(x) for x in row]))
            

        features.append(InputFeatures(input_ids=input_ids, input_mask=input_mask, input_len = input_len,
                                      segment_ids=segment_ids, label_ids=label_ids, input_span_mask=input_span_mask))
    return features


class CnerProcessor(DataProcessor):
    """Processor for the chinese ner data set."""

    def get_train_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_text(os.path.join(data_dir, "train.char.bmes")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_text(os.path.join(data_dir, "dev.char.bmes")), "dev")

    def get_test_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_text(os.path.join(data_dir, "test.char.bmes")), "test")

    def get_labels(self):
        """See base class."""
        return ["X",'B-CONT','B-EDU','B-LOC','B-NAME','B-ORG','B-PRO','B-RACE','B-TITLE',
                'I-CONT','I-EDU','I-LOC','I-NAME','I-ORG','I-PRO','I-RACE','I-TITLE',
                'O','S-NAME','S-ORG','S-RACE',"[START]", "[END]"]

    def _create_examples(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            if i == 0:
                continue
            guid = "%s-%s" % (set_type, i)
            text_a= line['words']
            # BIOS
            labels = []
            for x in line['labels']:
                if 'M-' in x:
                    labels.append(x.replace('M-','I-'))
                elif 'E-' in x:
                    labels.append(x.replace('E-', 'I-'))
                else:
                    labels.append(x)
            examples.append(InputExample(guid=guid, text_a=text_a, labels=labels))
        return examples

class CluenerProcessor(DataProcessor):
    """Processor for the chinese ner data set."""

    def get_train_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_json(os.path.join(data_dir, "train.json")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_json(os.path.join(data_dir, "dev.json")), "dev")

    def get_test_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_json(os.path.join(data_dir, "test.json")), "test")

    def get_labels(self):
        """See base class."""
        return ["X", "B-address", "B-book", "B-company", 'B-game', 'B-government', 'B-movie', 'B-name',
                'B-organization', 'B-position','B-scene',"I-address",
                "I-book", "I-company", 'I-game', 'I-government', 'I-movie', 'I-name',
                'I-organization', 'I-position','I-scene',
                "S-address", "S-book", "S-company", 'S-game', 'S-government', 'S-movie',
                'S-name', 'S-organization', 'S-position',
                'S-scene','O',"[START]", "[END]"]

    def _create_examples(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            
            guid = "%s-%s" % (set_type, i)
            text_a= line['words']
            # BIOS
            labels = line['labels']

            # 加入提取出的句法信息
            lexicon_to_wordspan_dir = line['lexicon_to_wordspan_dir']
            hpsg_list = line['hpsg_list']
            leaves_list = line['leaves_list']

            examples.append(InputExample(guid=guid, text_a=text_a, labels=labels, lexicon_to_wordspan_dir=lexicon_to_wordspan_dir, hpsg_list=hpsg_list, leaves_list=leaves_list))
        return examples

ner_processors = {
    "cner": CnerProcessor,
    'cluener':CluenerProcessor
}
