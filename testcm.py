#!/usr/bin/python3.8

# testing checkpoint manager

import util

def test_prompt(d):
    i = d['i']
    def pr(x, y=None):
        r = f'how do you write {x} in roman numbers? '
        if y is not None:
            r += y + '\n\n'
        return r
    return pr(24, 'XXIV') + pr(12, 'XII') + pr(i)

def test_parse(s):
    return s.split('\n\n')[0]

n = 3
data = [dict(i=i) for i in range(1, n+1)]
print(test_prompt(dict(i=21)))
util.run_eval(data, test_prompt, test_parse, delay=0.0, filestem='roman', k_interval=10)
