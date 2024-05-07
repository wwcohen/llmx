#!/usr/bin/python3.8

# Autorate using a tweaked version of the Kamalloo autorater prompt

import argparse
import json
import pandas as pd

import util

def tweaked_kamalloo_ar_prompt(qa_response):
  q = qa_response['question']
  if not q.endswith('?'):
    q += '?'
  answers = ' or '.join(qa_response['answer'])
  candidate_answer = qa_response['prediction']
  return (f"Question: {q}\n"
          + f"Known acceptible answer(s): {answers}\n"
          + f"Candidate answer: {candidate_answer}\n\n"
          + f"Is the candidate answer acceptable?  Start your answer with yes or no.")

def parse_yn_response(long_response):
  lc_response = long_response.lower()
  if lc_response.startswith('yes'):
    return 'y'
  elif lc_response.startswith('no'):
    return 'n'
  else:
    return 'u'

with open('data/NQ_FiD.jsonl') as fp:
  # dicts of question, answer, prediction
  data = [json.loads(line) for line in fp]

util.run_eval(
    data,
    tweaked_kamalloo_ar_prompt,
    parse_yn_response,
    delay=0.1,
    filestem='buf/kamalloo',
    time_interval=60)
