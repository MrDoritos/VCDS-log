#!/bin/python3

import os
import sys
import time

import plotly.express as px
import plotly.graph_objects as go

fin = sys.stdin
fout = sys.stdout

for x in range(5):
    fin.readline()

fields = [x.strip() for x in fin.readline().split(',') if x.strip() != '']

data = []

fin.readline()

def is_float(element: any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

while fin.readable():
    line = fin.readline()
    if not line:
        break
    _l = []

    #remove marker from split

    for column in line.split(',')[1:]:
        text = column.strip()
        if text == '':
            continue
        if is_float(text):
            _l.append(float(text))
        else:
            _l.append(0.0)
    data.append(_l)

    #data.append([float(x.strip()) for x in line.split(',') if x.strip() != ''])

def format_data(data:list):
    out_data = []
    for i in range(len(data)):
        _l = []
        for j in range(len(data[i])):
            if fields[j] != 'STAMP':
                _l.append(data[i][j])
        out_data.append(_l)
    return out_data

def format_pairs(data:list):
    out_data = []
    for i in range(len(data)):
        _l = []
        print(data[i])
        for j in range(len(data[i])):
            if fields[j] == 'STAMP':
                _l.append([data[i][j], data[i][j+1]])
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
            _l.append((in_data[i][j] - min_vals[j] + 0.00000001) / (max_vals[j] - min_vals[j] + 0.00000001))
        out_data.append(_l)

    return out_data

def normalize_pairs(in_data:list):
    #to_normalize = [pair[1] for sublist in in_data for pair in sublist]
    to_normalize = []

    for sublist in in_data:
        _l = []
        for pair in sublist:
            _l.append(pair[1])
        to_normalize.append(_l)

    normalized = normalize_data(to_normalize)

    out_data = []
    
    #for i in range(len(in_data)):
    #    _l = []
    #    for j in range(len(in_data[i])):
    #        _l.append([in_data[i][j][0], normalized[i][j]])

    for row_i,row in enumerate(in_data):
        _l = []
        for pair_i,pair in enumerate(row):
            _l.append([pair[0], normalized[row_i][pair_i]])
        out_data.append(_l)

    return out_data
    
normalized_pairs = format_pairs(data)#normalize_pairs(format_pairs(data))
normalized_data = normalize_data(format_data(data))

formatted_fields = [x for x in fields if x != 'STAMP']

def print_fields(fields):
    for i in range(len(fields)):
        print(fields[i], end='')
        if i < len(fields) - 1:
            print(',', end='')
    print()

try:
    #print_fields([x for x in fields if x != 'STAMP'])

    for i in range(len(normalized_data)):
        pass#print_fields(normalized_data[i])

    fout.close()
except Exception as e:
    #print(e)
    pass

fig = go.Figure()

for i in range(len(formatted_fields)):
    #fig.add_trace(go.Scatter(x=[j for j in range(len(normalized_data))], y=[_y[i] for _y in normalized_data], name=formatted_fields[i]))
    fig.add_trace(go.Scatter(x=[_x[i][0] for _x in normalized_pairs], y=[_y[i][1] for _y in normalized_pairs], name=formatted_fields[i]))

fig.show()