#!/bin/python3

import os
import sys
import time

fin = sys.stdin
fout = sys.stdout

for x in range(5):
    fin.readline()

fields = [x.strip() for x in fin.readline().split(',') if x.strip() != '']

data = []

fin.readline()

while fin.readable():
    line = fin.readline()
    if not line:
        break
    data.append([float(x.strip()) for x in line.split(',') if x.strip() != ''])

def format_data(data:list):
    out_data = []
    for i in range(len(data)):
        _l = []
        for j in range(len(data[i])):
            if fields[j] != 'STAMP':
                _l.append(data[i][j])
        out_data.append(_l)
    return out_data

def normalize_data(in_data:list):
    max_vals = []
    min_vals = []
    for i in range(len(in_data[0])):
        max_val = -1e9
        min_val = 1e9
        for j in range(len(in_data)):
            max_val = max(max_val, in_data[j][i])
            min_val = min(min_val, in_data[j][i])
        max_vals.append(max_val)
        min_vals.append(min_val)

    out_data = []
    for i in range(len(in_data)):
        _l = []
        for j in range(len(in_data[i])):
            _l.append((in_data[i][j] - min_vals[j]) / (max_vals[j] - min_vals[j]))
        out_data.append(_l)

    return out_data

normalized_data = normalize_data(format_data(data))

def print_fields(fields):
    for i in range(len(fields)):
        print(fields[i], end='')
        if i < len(fields) - 1:
            print(',', end='')
    print()

try:
    print_fields([x for x in fields if x != 'STAMP'])

    for i in range(len(normalized_data)):
        print_fields(normalized_data[i])

    fout.close()
except Exception as e:
    #print(e)
    pass