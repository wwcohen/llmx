## Utils

xpy:
	chmod +x *.py

## Downloading data

data: data/NQ301_human.tsv data/NQ_FiD.jsonl
	echo got em

data/NQ301_human.tsv:
	(cd data; wget https://raw.githubusercontent.com/ehsk/OpenQA-eval/main/data/NQ301_human.tsv)

data/NQ_FiD.jsonl:
	(cd data; wget https://raw.githubusercontent.com/ehsk/OpenQA-eval/main/data/model_outputs/NQ_FiD.jsonl)

## Run the basic prompt on all the fid outputs

data/ar: data/kamalloo-ar.jsonl data/explain-ar.jsonl

data/explain-ar.jsonl: 
	cat buf/explain.*.jsonl > data/explain-ar.jsonl

data/kamalloo-ar.jsonl: 
	cat buf/kamalloo.*.jsonl > data/kamalloo-ar.jsonl

buf/kamalloo.3598-3610.jsonl: 
	echo ./kamalloo_ar.py
