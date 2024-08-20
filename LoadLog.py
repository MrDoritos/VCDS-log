#!/bin/python3

import os
import sys
import time
#import numpy as np

class LoadLog:
    def __init__(self, log_file, debug=False):
        self.log_file = log_file
        self.debug = debug
        self.extra_debug = False

        with open(self.log_file, 'r') as stream:
            self.parse(stream)

        self.time_length = self.get_time_length()
        self.sample_count = self.get_sample_count()
        self.seconds_per_sample = self.time_length / self.sample_count

    def is_float(element: any) -> bool:
        #If you expect None to be passed:
        if element is None: 
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False
        
    def print_contents(self):
        print(self.fields)
        print(self.units)
        print(self.min_max)
        for i in range(len(self.data)):
            if i > 10:
                break
            print(self.data[i])

    def print_samples(self, data, max_len=100):
        for i in range(len(data)):
            if i > max_len:
                break
            print(data[i])


    def print_details(self, all=False):
        print('File name:', self.log_file)

        samples = self.get_sample_count()
        length = self.get_time_length()

        print('In data length:', len(self.in_data))

        print('Length in seconds:', length)
        print('Number of samples:', samples)

        print('Samples per second:', samples / length)
        print('Seconds per sample:', length / samples)

        if all:
            half_time = length / 2
            half_index = self.get_index_by_time(half_time)
            half_samples = self.get_samples(half_time)
            print('Index of half:', half_index)
            print('Samples at half:', half_samples)
            print('Samples near half:')
            self.print_samples(self.get_nearest_samples(half_time, fwd=2, rev=2, pad=0))

            half_field = 11
            time_diff = 0.02
            print(f'Field {half_field} @ {half_time}s:', self.fields[half_field], half_samples[half_field])
            print(f'Field {half_field} + {time_diff}s', self.get_sample_interpolated(half_time + time_diff, half_field))
            print(f'Field {half_field} - {time_diff}s', self.get_sample_interpolated(half_time - time_diff, half_field))

            #iterpolation test
            print('Interpolation test:')
            for i in range(10):
                test_time = half_time + (i * 0.5)
                print(f'Field {half_field} @ {test_time}s:', self.get_sample_interpolated(test_time, half_field))

            print('real:', half_samples[11], 'norm:', self.get_sample_norm(11, half_samples[11]))


    def print_all(self, all=False):
        self.print_contents()
        self.print_details(all)

    def get_time_length(self):
        return self.data[-1][0][0]
    
    def get_sample_count(self):
        return len(self.data)

    def get_field_index(self, field:str):
        return self.in_fields.index(field)

    def get_sample(self, field:int, time:float):
        return self.get_samples(time)[field]
    
    def get_sample_by_value(self, value:float, field:int):
        min_val = 1e9
        min_index = 0
        for i in range(len(self.data)):
            if abs(self.data[i][field][1] - value) < min_val:
                min_val = abs(self.data[i][field][1] - value)
                min_index = i
        return self.data[min_index][field]
    
    def get_column(self, field:int):
        return [x[field] for x in self.data]

    def get_samples(self, time:float):
        index = self.get_index_by_time(time)
        return self.data[index]
    
    def get_sample_norm(self, field:int, pair):
        if self.debug:
            print('max:', self.min_max[field][1], 'min:', self.min_max[field][0])
        return [pair[0] / self.time_length, (pair[1] - self.min_max[field][0]) / (self.min_max[field][1] - self.min_max[field][0])]

    def get_realtime(self, normtime:float):
        return normtime * self.time_length

    def get_samples_interpolated(self, time:float):
        return [self.get_sample_interpolated(time, x) for x in range(len(self.fields))]

    def get_sample_interpolated(self, time:float, field:int):
        index = self.get_index_by_time(time, field)
        nearest = self.data[index][field]
        slope = self.data[index - 1][field]
        first_value = slope
        second_value = nearest

        if self.extra_debug:
            print('req time:', time, 'last sample:', slope, 'nearest by time:', nearest, 'next sample:', self.data[index + 1][field])
        if nearest[0] - time < 0 and index + 1 < self.sample_count:
            slope = self.data[index + 1][field]
            first_value = nearest
            second_value = slope
            if self.extra_debug:
                print('change to next sample:', slope)

        if slope[1] == nearest[1]:
            if self.extra_debug:
                print('same value')
            return [time, nearest[1]]

        diff = time - first_value[0]

        m = (slope[1] - nearest[1]) / (slope[0] - nearest[0])

        y = diff * m + first_value[1]

        if self.extra_debug:
            print('req time:', time, '1st:', first_value, '2nd:', second_value)
            print('calc for time:', y, 'm:', m, 'diff * m:', diff * m)

        if self.debug:
            print('out:', [time, y], '1st:', first_value, '2nd:', second_value, 'm:', m, 'diff:', diff, 'diff * m:', diff * m)

        return [time, y]


    def get_index_by_time(self, time:float, field:int=-1):
        min_dist = 1e9
        min_index = 0
        for i in range(len(self.data)):
            t_val = 0
            #skip if diff > 5s
            if abs(self.data[i][0][0] - time) > 5 * self.seconds_per_sample:
                continue

            if field == -1:
                t_vals = [x[0] for x in self.data[i]]
                t_avg = sum(t_vals) / len(t_vals)
                
                t_val = t_avg
            else:
                t_val = self.data[i][field][0]

            dist = abs(t_val - time)

            if self.extra_debug:
                print('Try:', i, time, t_val, dist)

            if dist < min_dist:
                min_dist = dist
                min_index = i

        if self.debug:
            print('min index:', min_index, 'min dist:', min_dist)
        return min_index

    def get_nearest_samples(self, time:float, fwd=0, rev=0, pad=0):
        return self.get_nearest_samples_by_index(self.get_index_by_time(time), fwd, rev, pad)
    
    def get_nearest_samples_by_index(self, index:int, fwd=0, rev=0, pad=0):
        return [self.data[i] for i in range(index - rev - pad, index + fwd + 1 + pad)]

    def parse(self, stream):

        for x in range(2): stream.readline()

        self.in_blocks = [x.strip() for x in stream.readline().split(',') if x.strip() != '']

        for x in range(2): stream.readline()

        self.in_fields = [x.strip() for x in stream.readline().split(',') if x.strip() != '']

        #fin.readline()
        self.in_units = [x.strip() for x in stream.readline().split(',')[1:]]
        self.units = [self.in_units[i * 2 + 1] for i in range(int(len(self.in_units) / 2))]

        self.in_data = []
        self.markers = []

        while stream.readable():
            line = stream.readline()
            if not line:
                break
            _l = []

            for column in line.split(',')[1:]:
                text = column.strip()
                if text == '':
                    continue
                if LoadLog.is_float(text):
                    _l.append(float(text))
                else:
                    _l.append(0.0)

                row = line.split(',')
                if len(row[0]) > 0:
                    #print(row[0],row[1])
                    self.markers.append([row[0],row[1]])

            self.in_data.append(_l)
                
        self.data = []
        
        for i in range(len(self.in_data)):
            _l = []
            for j in range(len(self.in_data[i])):
                if self.in_fields[j] == 'STAMP':
                    _l.append([self.in_data[i][j], self.in_data[i][j+1]])
            self.data.append(_l)

        self.min_max = []

        for i in range(len(self.data[0])):
            max_val = -1e9
            min_val = 1e9
            for j in range(len(self.data)):
                dp = self.data[j][i][1]
                max_val = max(max_val, dp)
                min_val = min(min_val, dp)
            self.min_max.append([min_val, max_val])

        self.fields = [x for x in self.in_fields if x != 'STAMP']