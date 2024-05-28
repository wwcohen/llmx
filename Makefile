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

## collect outputs into data

data/explain-ar.jsonl: 
	./explaining_ar.py
	cat buf/explain.*.jsonl > data/explain-ar.jsonl

data/kamalloo-ar.jsonl: 
	cat buf/kamalloo.*.jsonl > data/kamalloo-ar.jsonl

## Run statistical analysis

eval: eval-kamalloo-ar eval-explaining-ar

eval-kamalloo-ar:
	./stats.py --autorater data/kamalloo-ar.jsonl --call_u_n  --correction

eval-explaining-ar:
	./stats.py --autorater data/explain-ar.jsonl  --correction


