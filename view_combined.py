#!/bin/python3
import os, sys

import matplotlib.pyplot as plt
import numpy as np

def parse_log(stream):
    lines = stream.readlines()

    header = lines[0].split(',')
    lines = lines[1:]
    samples = {}
    for head in header:
        samples[head] = []

    for line in lines:
        for i,field in enumerate(line.split(',')):
            samples[header[i]].append(float(field))
        #rows.append(list(map(float,line.split(','))))

    return (header,samples)

def do_plot(header, samples):
    sec=np.array([x for x in samples[header[0]]])
    data=np.array(
        [
            [
                samples[x][i]
                for x in header[1:]
            ]
            for i in range(len(samples[header[0]]))
        ])
    plt.plot(sec,data)
    plt.figlegend(header[1:])
    plt.show()

def do_integration(header, samples):
    start=9617
    start=17796
    adj=0.38
    msmph=2.23694
    end=len(samples[header[0]])-1
    end=37570
    index=start
    secs=samples[header[0]]
    secs_plot=secs[start:end+1]
    y_accel=samples[header[14]]
    v_end=samples[header[24]][end]
    gps_speed=[samples[header[24]][i]*msmph for i in range(start,end+1)]
    rpm=[samples[header[1]][i]*0.01 for i in range(start,end+1)]
    t_tot=secs[end]-secs[start]
    a_tot=v_end/t_tot
    print('accel', a_tot, 'vel', v_end, 'time', t_tot)
    last_time=secs[index]
    vel=0
    vels=[vel]
    index+=1
    while index<=end:
        time=secs[index]
        time_diff=time-last_time
        last_time=time
        acc=y_accel[index]-adj
        vel+=(acc * (time_diff))*2.23694
        vels.append(vel)
        index+=1
    plt.plot(secs_plot, vels, label='velocity')
    plt.plot(secs_plot, y_accel[start:end+1], label='accel')
    plt.plot(secs_plot, gps_speed, label='gps_speed', mouseover=True)
    plt.plot(secs_plot, rpm, label='rpm')
    plt.figlegend(['velocity', 'accel', 'gps_speed', 'rpm'])
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("more args")
        exit(1)
    
    with open(sys.argv[1]) as stream:
        header,samples=parse_log(stream)
        #do_plot(header,samples)
        do_integration(header, samples)