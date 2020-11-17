CURRENT_DIR=`pwd`
export BERT_BASE_DIR=/home/yangzhixian/QA-Matching/models/chinese_roberta_wwm_large
export CLUE_DIR=$CURRENT_DIR/datasets
export OUTPUR_DIR=$CURRENT_DIR/outputs
TASK_NAME="cluener"
#
python run_ner_crf.py \
  --model_type=bert \
  --model_name_or_path=$BERT_BASE_DIR \
  --task_name=$TASK_NAME \
  --use_syntax \
  --do_train \
  --do_eval \
  --do_lower_case \
  --data_dir=$CLUE_DIR/${TASK_NAME}/ \
  --train_max_seq_length=128 \
  --eval_max_seq_length=128 \
  --per_gpu_train_batch_size=128 \
  --per_gpu_eval_batch_size=128 \
  --learning_rate=3e-5 \
  --crf_learning_rate=1e-3 \
  --num_train_epochs=10.0 \
  --logging_steps=84 \
  --save_steps=84 \
  --output_dir=$OUTPUR_DIR/${TASK_NAME}_output/ \
  --overwrite_output_dir \
  --seed=42

