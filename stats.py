#!/usr/bin/python3.8

import argparse
import dataclasses
from icecream import ic
import json
import math
import pandas as pd
import sys
from scipy import stats

import util

def load_json(files):
    result = []
    for file in files:
        with open(file) as fp:
            result.extend([json.loads(line) for line in fp])
    return result

def join_ratings(ar_file):
    #Question 'Model answer' Acceptable? ...
    human_df = pd.read_csv('data/NQ301_human.tsv', sep='\t')
    human_df = pd.DataFrame(
        dict(
            question=human_df['Question'],
            pred=human_df['Model answer'],
            norm_pred=[util.normalize_answer(a) for a in human_df['Model answer']],
            h=human_df['Acceptable?']))
    #question, answer:list(str), prediction, ynu, long_answer
    with open(ar_file) as fp:
        ar_dicts = [json.loads(line) for line in fp]
    ar_df = pd.DataFrame(
        dict(
            question=[d['question'] for d in ar_dicts],
            pred=[d['prediction'] for d in ar_dicts],
            norm_pred=[util.normalize_answer(d['prediction']) for d in ar_dicts],
            a=[d['ynu'] for d in ar_dicts],
            long_answer = [d['long_answer'] for d in ar_dicts]))
    print(len(ar_df),'autorated records loaded')
    print(len(human_df), 'human rated records loaded')
    join_keys = ['question', 'norm_pred']
    human_df = human_df.set_index(join_keys)
    ar_df = ar_df.set_index(join_keys)
    join_df = ar_df.join(human_df, on=join_keys, how='left', lsuffix='_a', rsuffix='_h')
    join_df = join_df.reset_index().drop_duplicates(subset=join_keys)
    # question norm_pred pred_a a long_answer pred_h h
    s_n = join_df[join_df.h.notna()]
    s_N = join_df[join_df.h.isna()]
    print(f'n={len(s_n)} N={len(s_N)}')
    return s_n, s_N


@dataclasses.dataclass
class CI:
    method: str
    lo: float
    hi: float
    w: float = -1
    mean: float = -1

    def __post_init__(self):
        self.w = self.hi - self.lo
        if self.mean == -1:
            self.mean = self.lo + self.w / 2.0

def classical_binom_ci(s_n, s_N):
    n = len(s_n)
    k = sum(int(h == 'Yes') for h in s_n.h)
    bt = stats.binomtest(n=n, k=k).proportion_ci()
    return CI(method='classical_binom', lo=bt.low, hi=bt.high)

def classical_ci(s_n, s_N):
    tmp = s_n.copy()
    tmp['y'] = [float(h == 'Yes') for h in tmp.h]
    mean = tmp.y.mean()
    var = tmp.y.var()
    tot_size = len(tmp)
    half_w = 1.96 * math.sqrt(var/(tot_size - 1))
    return CI(method='classical', lo=mean - half_w, hi=mean + half_w)

def stratified_ci(s_n, s_N, correction=True, trace=True):
    ar_values = set(s_n.a)
    # labeled observations
    strata = {val: s_n[s_n.a == val].copy() for val in ar_values}
    for i in strata:
        strata[i]['y'] = [float(h == 'Yes') for h in strata[i].h]
    strata_size = {i:len(strata_i) for i, strata_i in strata.items()}
    tot_size = sum(strata_size.values())
    # unlabeled data
    unlab_strata = {val: s_N[s_N.a == val].copy() for val in ar_values}
    unlab_strata_size = {i:len(unlab_strata_i) for i, unlab_strata_i in unlab_strata.items()}
    unlab_tot_size = sum(unlab_strata_size.values())
    unlab_strata_prob = {i:unlab_strata_size[i] / unlab_tot_size for i in strata}
    # stratification
    # 1 / N * sum_{h=1}^L N_h xbar_h
    mean = sum(unlab_strata_prob[i] * strata[i].y.mean() for i in strata)
    # sum_{h=1}^L (N_h/N)^2 (N_h - n_h) / (N_h - 1) sigma^2_h / n_h
    if not correction:
        correct = {i: 1 for i in strata}
    else:
        correct = {i: (unlab_strata_size[i] - strata_size[i]) / (unlab_strata_size[i] - 1)
                   for i in strata}
    var = sum(
        unlab_strata_prob[i]**2 * correct[i] * (strata[i].y.var() / strata_size[i])
        for i in strata)
    half_w = 1.96 * math.sqrt(var)
    if trace:
        n = tot_size
        N = unlab_tot_size
        ic(n, N, ar_values)
        for i in sorted(list(ar_values)):
            print('-' * 10, f'strata {i}', '-' * 10)
            n_h = strata_size[i]
            N_h = unlab_strata_size[i]
            p_h = unlab_strata_prob[i]
            m_h = strata[i].y.mean()
            sd_h = math.sqrt(strata[i].y.var())
            se_h = math.sqrt(strata[i].y.var()) / n_h
            ic(N_h, n_h, p_h, m_h, sd_h, se_h)
    return CI(method='stratified', lo=mean - half_w, hi=mean + half_w)

def analyze(args):
    s_n, s_N = join_ratings(args.autorater)
    print(classical_binom_ci(s_n, s_N))
    print(classical_ci(s_n, s_N))
    print(stratified_ci(s_n, s_N, correction=args.correction))

parser = argparse.ArgumentParser(prog='stats')
parser.add_argument(
    '--autorater',
    help='autorater output file, eg "data/explain-ar.jsonl" or "data/kamaloo-ar.jsonl"')
parser.add_argument(
    '--correction', action='store_true', 
    help='use small-sample correction')
parser.add_argument(
    '--call_u_n', action='store_true', 
    help='reclassified "u" autorater labels as "n"')
args = parser.parse_args()
print(args)
analyze(args)
