#!/usr/bin/env python3

from ev3dev.auto import *

print('Setting input values')
LEFT_MOTOR_PORT = OUTPUT_B
RIGHT_MOTOR_PORT = OUTPUT_C
SCANNER_MOTOR_PORT = OUTPUT_A
SCANNER_MOTOR_GEAR_RATIO = 20 / 12

print('Initialising...')
LEFT_MOTOR = LargeMotor(LEFT_MOTOR_PORT)
RIGHT_MOTOR = LargeMotor(RIGHT_MOTOR_PORT)
assert LEFT_MOTOR.connected
assert RIGHT_MOTOR.connected
LEFT_MOTOR.reset()
RIGHT_MOTOR.reset()

SCANNER_MOTOR = MediumMotor(SCANNER_MOTOR_PORT)
assert SCANNER_MOTOR.connected
# SCANNER_MOTOR.reset()

IR_SENSOR = InfraredSensor()
ULTRASONIC_SENSOR = UltrasonicSensor()
assert IR_SENSOR.connected or ULTRASONIC_SENSOR.connected
if ULTRASONIC_SENSOR.connected:
    ULTRASONIC_SENSOR.mode = 'US-DIST-CM'
    DISTANCE_SENSOR = ULTRASONIC_SENSOR
else:
    IR_SENSOR.mode = 'IR-PROX'
    DISTANCE_SENSOR = IR_SENSOR


def run():
    # TODO: implement
    pass


print('Running...')
run()

print('Exiting...')
LEFT_MOTOR.reset()
RIGHT_MOTOR.reset()

SCANNER_MOTOR.stop_action = 'hold'
SCANNER_MOTOR.run_to_abs_pos(position_sp=0)
SCANNER_MOTOR.wait_until('running')
SCANNER_MOTOR.reset()
