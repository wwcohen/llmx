#!/usr/bin/python3.8

# Autorate using an autorater that gives an explanation
# The explanation is just a letter A,B,C,D - see the prompt for
# definitions but basically each letter should indicate a different
# level of confidence

import argparse
import json
import re
import sys

import util

def explaining_ar_prompt(qa_response):
  q = qa_response['question']
  if not q.endswith('?'):
    q += '?'
  answers = ' or '.join(qa_response['answer'])
  candidate_answer = qa_response['prediction']
  return (f"Question: {q}\n"
          + f"Known acceptible answer(s): {answers}\n"
          + f"Candidate answer: {candidate_answer}\n\n"
          + f"Is the candidate answer acceptable?  Give the best response from those below.\n\n"
          + "(A) Yes - the candidate is essentially the same as one of the known acceptable answers.\n"
          + "(B) Yes - the candidate is different from each of the known acceptable answers, but I am confident it is also correct.\n"
          + "(C) Perhaps - the candidate is different from each of the known acceptable answers, but it might be acceptable.\n"
          + "(D) No - the candidate is different from the known acceptable answers, and is incorrect.\n")

def parse_multichoice_response(long_response):
    m = re.search(r'\b[ABCD]\b', long_response)
    if m:
        return m.group(0)
    else:
        return 'C'  # ie "perhaps"

with open('data/NQ_FiD.jsonl') as fp:
  fid = [json.loads(line) for line in fp]

parser = argparse.ArgumentParser(prog='explaining_ar')
parser.add_argument(
  '--start',
  help='example number to start at - assumes previous examples stored in buf/*.jsonl')
args = parser.parse_args()
print(args)

if args.start is None:
  results = util.run_eval(
    fid,
    explaining_ar_prompt,
    parse_multichoice_response,
    filestem='buf/explain',
    time_interval=60)
else:
  lo = int(args.start)
  results = util.run_eval(
    fid[lo:],
    explaining_ar_prompt,
    parse_multichoice_response,
    service='mistral',
    filestem='buf/explain',
    time_interval=60,
    last_chkpt_k=lo,
    k=lo,
    results=[{'dummy':None}] * lo)
