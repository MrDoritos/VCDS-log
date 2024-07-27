#!/bin/python3

from cgi import print_form
import math

class Engine:
    #ECU variables
    act_lambda = 0.0
    spec_lambda = 0.0
    idle_lambda = 0.0
    load_lambda = 0.0
    o2_reg = False
    ignition_timing = 0.0
    injection_timing = 0.0
    intake_temp = 0.0
    maf = 0.0
    act_map = 0.0
    spec_map = 0.0
    engine_rpm = 0.0
    engine_load = 0.0
    throttle_position = 0.0
    starter_activated = False
    crank_position = 0.0
    cam_position = 0.0
    intake_cam_advance = 0.0
    idle_cam_advance = 28.0
    time_since_start = 0.0

    #Default environment
    env_pressure = 900.0
    env_temp = 30.0

    #Real variables
    turbo_rpm = 0.0
    intake_volume = 0.0
    air_pressure = 0.0
    real_time = 0.0
    rotation_inertia = 0.0
    starter_torque = 0.0

    #Static variables
    displacement = 1984.0
    cylinders = 4
    compression_ratio = 10.5
    flame_speed = 0.0
    intake_valve_resistance = 0.0
    exhaust_valve_resistance = 0.0
    throttle_body_resistance = 0.0
    bore = 8.25
    stroke = 9.28
    rotation_weight = 20000.0 #20kg
    #output_friction_torque = 1000.0 #10 Nm
    #starter_start_torque = 10000.0 # 100 Nm
    starter_torque_constant = 59.688 # 1.2 Nm/A
    starter_power = 1000.0 #1kW or 1.1kw
    supply_voltage = 12.0 #12V
    time_step = 0.001 #1ms
    good_compression = 12000.0
    minimum_idle = 640.0
    fast_idle = 1000.0
    maximum_rpm = 7000.0
    starting_rpm = 250.0
    starter_rpm = 3000.0
    starter_flywheel_ratio = 15.0 

    #Units
    air_unit = 'g'
    time_unit = 's'
    pressure_unit = 'bar'
    volume_unit = 'cc'
    force_unit = 'N'
    distance_unit = 'cm'
    temp_unit = 'C'
    power_unit = 'W'
    rotational_velocity_unit = 'rpm'

    def collect_sensor_data(self):
        self.intake_temp = self.env_temp
        self.air_pressure = self.env_pressure

    def step(self, period):
        if self.time_since_start < self.time_step:
            print("Relay activated")
            self.collect_sensor_data()

        if self.engine_rpm < self.starting_rpm:
            if not self.starter_activated:
                self.injection_timing = 0.0
                

        if self.starter_activated:
            if self.engine_rpm < self.starting_rpm:
                self.engine_rpm += 128.0 * period

            if self.engine_rpm > self.minimum_idle:
                self.starter_activated = False

        self.real_time += period
        self.time_since_start += period

    def run_sim(self, time, period, callback=None):
        initial_time = self.real_time
        while self.real_time < initial_time + time:
            self.step(period)
            if callback:
                callback()

    def print_log(self):
        print(f"Real time: {self.real_time}{self.time_unit} Start time: {self.time_since_start}{self.time_unit} Engine RPM: {self.engine_rpm}{self.rotational_velocity_unit}")

    def compression_test(self):
        self.starter_activated = True
        self.run_sim(3.0, 0.1, callback=self.print_log)

sim = Engine()

sim.compression_test()