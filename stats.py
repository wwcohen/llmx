#!/usr/bin/python3.8

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

def join_ratings(ar_files):
    #Question 'Model answer' Acceptable? ...
    human_df = pd.read_csv('data/NQ301_human.tsv', sep='\t')
    human_df = pd.DataFrame(
        dict(
            question=human_df['Question'],
            pred=human_df['Model answer'],
            norm_pred=[util.normalize_answer(a) for a in human_df['Model answer']],
            h=human_df['Acceptable?']))
    #question, answer:list(str), prediction, ynu, long_answer
    ar_dicts = load_json(ar_files)
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

def stratified_ci(s_n, s_N):
    ar_values = set(s_n.a)
    strata = {val: s_n[s_n.a == val].copy() for val in ar_values}
    for i in strata:
        strata[i]['y'] = [float(h == 'Yes') for h in strata[i].h]
    strata_size = {i:len(strata_i) for i, strata_i in strata.items()}
    tot_size = sum(strata_size.values())
    strata_prob = {i:strata_size[i]/tot_size for i in strata}
    mean = sum(strata_prob[i] * strata[i].y.mean() for i in strata)
    var = sum(
        strata_prob[i]**2 * strata[i].y.var() / (strata_size[i] - 1)
        for i in strata)
    half_w = 1.96 * math.sqrt(var)
    return CI(method='stratified', lo=mean - half_w, hi=mean + half_w)

def analyze():
    s_n, s_N = join_ratings(sys.argv[1:])
    print(classical_binom_ci(s_n, s_N))
    print(classical_ci(s_n, s_N))
    print(stratified_ci(s_n, s_N))

analyze()
