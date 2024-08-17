#!/bin/python3

import importlib
import os
import sys
import numpy as np

LoadLog = importlib.import_module("LoadLog")

'''['Engine Speed - (G28)',
 'Injection Timing',
   'Mass Air Flow - Sensor (G70)',
     'Throttle Valve Angle', 
     'Lambda Control - Bank 1 (actual)', 
     'Lambda Control - Bank 1 (specified)', 
     'Adaptation (Idle) - Bank 1 Sensor 1', 
     'Adaptation (Partial) - Bank 1 Sensor 1', 
     'Boost Pressure - (specified)', 'Boost Pressure - (actual)', 
     'Rail Pressure - (specified)', 'Rail Pressure - (actual)']'''
#['/min', 'ms', 'g/s', '%', '', '', '%', '%', 'mbar', 'mbar', 'bar', 'bar']

if len(sys.argv) < 2:
    print("Add filename")
    exit(1)

if not os.path.isfile(sys.argv[1]):
    print("File not found")
    exit(1)

log = LoadLog.LoadLog(sys.argv[1], False)

log.print_all(all=False)

engine_speed = 0
mass_air_flow = 2
throttle_valve_angle = 3
boost_act = 9

sample_count = 10
#selected_samples = np.array(ndmin=3, object=np.empty)
selected_samples = []
for i in range(0, sample_count):
    normtime = i / sample_count
    samples = log.get_samples_interpolated(log.get_realtime(normtime))
    #print(samples)
    selected_samples.append(samples)
    #selected_samples = np.append(selected_samples, np.array(samples))

#print([x[0] for x in selected_samples])
selected_samples = np.array(selected_samples)

#print(selected_samples)

_r = selected_samples[:,0] #rpm
_m = selected_samples[:,2] #mass
_t = selected_samples[:,3] #throt
_b = selected_samples[:,9] #boost

#print('rpm:', _r)
#print('mass:', _m)
#print('throt:', _t)

#print(selected_samples[:,0])
#print(np.corrcoef(_r, _m))

'''
Intake air model

Difference in pressure before and after throttle plate
Velocity of air in the intake system (MAF)

Velocity is determined by turbo cfm, backpressure, tb

Pressure after throttle plate is the resistance of the tb to flow, intake runners,
    intake valve advance, rpm

Temperature is constant

Turbo cfm is pressure differential, velocity and exhaust flow and temperature driving turbine

Exhaust flow is intake flow times inverse lambda

Fuel injection volume is injection ms, fuel pressure, injector flow

Determine injector flow from lambda, air data

'''

def get_start():
    rpm = log.get_column(0)
    for x in rpm:
        if x[1] > 1:
            return x

print('Engine start time (s):', get_start()[0])

def get_idle():
    times = []
    rpm = log.get_column(0)
    tb = log.get_column(3)
    for i in range(len(log.data)):
        if rpm[i][1] < 900 and tb[i][1] < 10: #valid high idle, not fast/warmup idle
            times.append(rpm[i][0])
    return times

def print_time_as_range(times):
    #print(times)
    started = False
    last = times[0]
    for x in times:
        if not started:
            print(f'{x} -> ', end='')
            started = True

        if (x > last + 2) and started:
            print(f'{last}, ', end='')
            started = False

        last = x
    print('end')
        
def print_dict(kvs:dict):
    for kv in kvs:
        print(f'{kv}: {kvs[kv]}')

idle_times = get_idle()

print('Idle times:')
#print(np.array(idle_times))
print_time_as_range(idle_times)

print('Idle data:')

idle_data = np.array([log.get_samples(x) for x in idle_times])

print(idle_data.shape)

def determine_variables(time):
    period = 5 #s
    step = 0.01
    stime = 0

    filled_data = []

    while True:
        stime = stime + step
        if stime > period:
            break

        row = log.get_samples_interpolated(time + stime)
        #print(row)
        filled_data.append(row)

    rpm_avg = np.average(np.array(filled_data)[:,0,1])
    inj_avg = np.average(np.array(filled_data)[:,1,1])
    mass_avg = np.average(np.array(filled_data)[:,2,1])
    throt_avg = np.average(np.array(filled_data)[:,3,1])
    lambda_avg = np.average(np.array(filled_data)[:,4,1])
    ltft_idle_avg = np.average(np.array(filled_data)[:,6,1])
    boost_avg = np.average(np.array(filled_data)[:,9,1])
    rail_avg = np.average(np.array(filled_data)[:,11,1])

    #print(f'time: {time}:{period}s rpm: {rpm_avg}, mass: {mass_avg}, throt: {throt_avg}, boost: {boost_avg}')

    values = dict()

    values['time'] = time
    values['period'] = period
    values['revolutions per minute'] = rpm_avg
    values['injection ms'] = inj_avg
    values['mass air flow'] = mass_avg
    values['throttle valve angle'] = throt_avg
    values['actual lambda'] = lambda_avg
    values['idle long term fuel trim'] = ltft_idle_avg
    values['actual boost'] = boost_avg
    values['actual fuel rail pressure'] = rail_avg

    air_density = values['air density'] = 1019.6 # g/m^3
    intake_area = values['intake_area'] = 0.003478 # m^2
    intake_strokes_per_second = values['intake strokes per second'] = rpm_avg / 30 # intakes per s
    intake_velocity = values['intake velocity'] = mass_avg / (air_density * intake_area) # m/s
    intake_volumetric_flow = values['intake volumetric flow'] = mass_avg / air_density # m^3/s
    volume_per_stroke = values['volume per stroke'] = intake_volumetric_flow / intake_strokes_per_second # l/s
    mass_per_stroke = values['air mass per stroke'] = mass_avg / intake_strokes_per_second # g/stroke
    liters_per_stroke = values['liters per stroke'] = volume_per_stroke * 1000 # l/s
    bore = values['bore'] = 0.0825 # m
    stroke = values['stroke'] = 0.0928 # m
    compression_ratio = values['compression ratio'] = 10.5
    cylinder_volume = values['cylinder volume'] = (np.pi * (bore / 2)**2 * stroke) # m^3
    liters_per_cylinder = values['liters per cylinder'] = cylinder_volume * 1000 # l
    ideal_air_mass_per_cylinder = values['ideal air mass per stroke'] = cylinder_volume * air_density # g

    values['intake permeance'] = intake_volumetric_flow / cylinder_volume 
    values['cylinder fill %'] = volume_per_stroke / cylinder_volume

    fuel_density = values['fuel density'] = 710000 # g/m^3
    fuel_stoichiometry = values['fuel stoichiometry'] = 14.7
    fuel_mass_per_stroke = values['fuel mass per stroke (avg,real)'] = mass_per_stroke / (fuel_stoichiometry * lambda_avg) # g/stroke
    #fuel_mass_per_stroke = values['fuel mass per stroke (avg,ltft,idle)'] = mass_per_stroke / (fuel_stoichiometry * ltft_idle_avg) # g/stroke
    fuel_volume_per_stroke = values['fuel volume per stroke'] = fuel_mass_per_stroke / fuel_density # m^3
    fuel_volume_per_second = values['fuel volume per second'] = fuel_volume_per_stroke * intake_strokes_per_second # m^3/s
    fuel_usage_per_hour = values['fuel usage per hour'] = fuel_volume_per_second * 3600 # m^3/h
    fuel_liters_per_hour = values['fuel liters per hour'] = fuel_usage_per_hour * 1000 # l/h
    ms_times_p = values['inj ms x p'] = inj_avg * rail_avg

    total_energy = values['total energy'] = (fuel_mass_per_stroke * (1 / lambda_avg)) * 44000 # J/stroke
    used_energy = values['used energy'] = total_energy * 0.25 # J/stroke
    combustion_power = values['combustion power per second'] = used_energy * intake_strokes_per_second # W
    angular_velocity = values['angular velocity'] = rpm_avg * 2 * np.pi / 60 # rad/s
    angular_acceleration = values['angular acceleration'] = angular_velocity * (rpm_avg/60) # rad/s^2
    torque = values['torque'] = combustion_power / angular_acceleration # Nm
    max_ftlb_torque = 148
    max_torque = values['max torque in J'] = 148 / 0.7376 # J
    hp = values['horsepower'] = combustion_power * 0.74 * rpm_avg / 5252 # hp
    max_hp = values['max horsepower'] = max_ftlb_torque * 4000 * 60 / 5252 # hp
    driveline_power = values['driveline power'] = rpm_avg



    '''
        print(  'air density:', air_density, 
                'intake area:', intake_area, 
                'intake strokes per second:', intake_strokes_per_second,
                'intake velocity:', intake_velocity,
                'intake volumetric flow:', intake_volumetric_flow,
                'volume per stroke:', volume_per_stroke, 
                'liters per stroke:', liters_per_stroke)
    '''
    #print(values)
    #print_dict(values)
    


    print()

    return values


tp = [
    determine_variables(t) for t in range(100, int(log.time_length)-5, 5)
    #determine_variables(123.0),
    #determine_variables(212.0),
    #determine_variables(275.0),
]

tp.sort(key=lambda x : x['revolutions per minute'])

def norm(v,x):
    max = np.max(x)
    min = np.min(x)
    if max == min or v == min:
        return 0
    return (v - min) / (max - min)

dict_combined = dict()
for x in tp:
    for k in x:
        if k not in dict_combined:
            dict_combined[k] = []
        dict_combined[k].append(norm(x[k], [x_[k] for x_ in tp]))

print(dict_combined)

#print(np.corrcoef([dict_combined['revolutions per minute'], dict_combined['throttle valve angle'], dict_combined['mass air flow']]))

import plotly.express as px
import plotly.graph_objects as go

fig = go.Figure()
fig.update_layout(title='Model')

#for i in range(len(dict_combined['time'])):
for k,v in dict_combined.items():
    #[_x for _x in dict_combined['mass air flow']], 
    #[(dict_combined['injection ms'][_i] * dict_combined['actual fuel rail pressure'][_i]) for _i in range(len(v))],
    fig.add_trace(go.Scatter(x=[_x for _x in dict_combined['revolutions per minute']], 
                                y=[_y for _y in v], 
                                name=f'{k}'))

print('points:', len(dict_combined['time']))

fig.show()

print('Done')