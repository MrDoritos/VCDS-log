#!/bin/python3

import os
import sys
import time

import plotly.express as px
import plotly.graph_objects as go

fin = open(sys.argv[1], 'r') if len(sys.argv) > 1 else sys.stdin
fout = sys.stdout
normalize = 'norm' in sys.argv

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

markers = []

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

	row = line.split(',')
	if len(row[0]) > 0:
		#print(row[0],row[1])
		markers.append([row[0],row[1]])

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
		#print(data[i])
		for j in range(len(data[i])):
			if fields[j] == 'STAMP':
				_l.append([data[i][j], data[i][j+1]])
		out_data.append(_l)
	return out_data

def get_min_max(in_data:list):
	max_vals = []
	min_vals = []
	for i in range(len(in_data[0])):
		max_val = -1e9
		min_val = 1e9
		for j in range(len(in_data)):
			dp = in_data[j][i]
			max_val = max(max_val, dp)
			min_val = min(min_val, dp)
		max_vals.append(max_val)
		min_vals.append(min_val)
		
	return min_vals, max_vals

def normalize_data(in_data:list):
	min_vals, max_vals = get_min_max(in_data)

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
	
	for sublist_i,sublist in enumerate(in_data):
		#print(sublist_i)
		_l = []
		for pair in sublist:
			_l.append(pair[1])
		to_normalize.append(_l)

	min_vals, max_vals = get_min_max(to_normalize)
	
	offs = 0
	for field_i in range(len(fields)):
		#print(f'{field_i}/{len(fields)}')
		if fields[field_i] != 'STAMP':
			fields[field_i] += f'\n(min:{min_vals[offs]},max:{max_vals[offs]})'
			offs += 1
	
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
#print(len(normalized_pairs))
if normalize:
	normalized_pairs = normalize_pairs(normalized_pairs)

#normalized_data = normalize_data(format_data(data))

formatted_fields = [x for x in fields if x != 'STAMP']

#print(fields)
#print(len(formatted_fields))

def print_fields(fields):
	for i in range(len(fields)):
		#print(fields[i], end='')
		if i < len(fields) - 1:
			pass
			#print(',', end='')
	#print()

try:
	#print_fields([x for x in fields if x != 'STAMP'])

	for i in range(len(normalized_data)):
		pass#print_fields(normalized_data[i])

	fout.close()
except Exception as e:
	#print(e)
	pass

#exit(0)

fig = go.Figure()

fig.update_layout(title=sys.argv[1])

for i in range(len(formatted_fields)):
	#fig.add_trace(go.Scatter(x=[j for j in range(len(normalized_data))], y=[_y[i] for _y in normalized_data], name=formatted_fields[i]))
	fig.add_trace(go.Scatter(x=[_x[i][0] for _x in normalized_pairs], y=[_y[i][1] for _y in normalized_pairs], name=formatted_fields[i]))

for marker in markers:
	#fig.add_trace(go.Scatter(x=[marker[0]], y=[marker[1]], mode='markers', name='Marker'))
	fig.add_shape(dict(
		type="line",
		x0=marker[1],
		x1=marker[1],
		y0=0,
		y1=1,
		xref="x",
		yref="paper",
		line=dict(
			color="Red",
			width=1
		)
	))

fig.show()