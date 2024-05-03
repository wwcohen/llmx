#!/usr/bin/python3.8

import json
import sys

for file in sys.argv[1:]:
    with open(file) as fp:
        for line in fp:
            d = json.loads(line)
            for k, v in d.items():
                #k = k.decode('utf-8', 'ignore')
                #v = v.decode('utf-8', 'ignore')
                print(f'{k}\t{v}')
