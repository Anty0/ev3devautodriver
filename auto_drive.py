#!/usr/bin/env python3

from ev3dev.auto import *

print('Setting input values')
LEFT_MOTOR_PORT = OUTPUT_B
RIGHT_MOTOR_PORT = OUTPUT_C
SCANNER_MOTOR_PORT = OUTPUT_A
SCANNER_MOTOR_GEAR_RATIO = 20 / 12

print('Initializing...')
LEFT_MOTOR = LargeMotor(LEFT_MOTOR_PORT)
RIGHT_MOTOR = LargeMotor(RIGHT_MOTOR_PORT)
assert LEFT_MOTOR.connected
assert RIGHT_MOTOR.connected
LEFT_MOTOR.reset()
RIGHT_MOTOR.reset()

SCANNER_MOTOR = MediumMotor(SCANNER_MOTOR_PORT)
assert SCANNER_MOTOR.connected
# SCANNER_MOTOR.reset()
SCANNER_MOTOR.stop_action = 'brake'

IR_SENSOR = InfraredSensor()
ULTRASONIC_SENSOR = UltrasonicSensor()
assert IR_SENSOR.connected or ULTRASONIC_SENSOR.connected
if ULTRASONIC_SENSOR.connected:
    ULTRASONIC_SENSOR.mode = 'US-DIST-CM'
    DISTANCE_SENSOR = ULTRASONIC_SENSOR
    MAX_DISTANCE = 255
else:
    IR_SENSOR.mode = 'IR-PROX'
    DISTANCE_SENSOR = IR_SENSOR
    MAX_DISTANCE = 100


def run():
    scan_results = [MAX_DISTANCE, MAX_DISTANCE, MAX_DISTANCE]
    scan_integrals = [0, 0, 0]

    scan_result_tmp = MAX_DISTANCE
    scan_result_tmp_pos = 1

    def rotateScanner(target):
        SCANNER_MOTOR.run_to_abs_pos(position_sp=target * SCANNER_MOTOR_GEAR_RATIO)

    def getActualScannerPos():
        scanner_position = SCANNER_MOTOR.position
        if scanner_position < -25:
            return 0
        if scanner_position > 25:
            return 2
        return 1

    def writeTmpResult(result, scanner_pos):
        global scan_result_tmp, scan_result_tmp_pos
        if scanner_pos != scan_result_tmp_pos:
            scan_results[scan_result_tmp_pos] = scan_result_tmp
            scan_integrals[scan_result_tmp_pos] = scan_result_tmp + scan_integrals[scan_result_tmp_pos] / 2
            scan_result_tmp = MAX_DISTANCE
            scan_result_tmp_pos = scanner_pos
            updateDrive()

        scan_result_tmp = min(scan_result_tmp, result)

        if scan_result_tmp < scan_results[scan_result_tmp_pos]:
            scan_results[scan_result_tmp_pos] = scan_result_tmp
            updateDrive()

    def updateDrive():
        speed_mul = (scan_results[1] * 3 - MAX_DISTANCE) / MAX_DISTANCE * 100
        left_speed = ((scan_results[2] / scan_results[0]) + (scan_integrals[2] / scan_integrals[0])) / 2 * speed_mul
        right_speed = ((scan_results[0] / scan_results[2]) + (scan_integrals[0] / scan_integrals[2])) / 2 * speed_mul

        if scan_results[2] < scan_results[0]:
            right_speed *= 1.2

        if scan_results[0] < scan_results[2]:
            left_speed *= 1.2

        LEFT_MOTOR.duty_cycle_sp = min(max(left_speed, -100), 100)
        RIGHT_MOTOR.duty_cycle_sp = min(max(right_speed, -100), 100)

    try:
        rotateScanner(80)
        SCANNER_MOTOR.wait_until('running')
        rotateScanner(-80)
        while 'running' in SCANNER_MOTOR.state:
            writeTmpResult(DISTANCE_SENSOR.value(), getActualScannerPos())
        next_positive = True

        LEFT_MOTOR.run_direct()
        RIGHT_MOTOR.run_direct()
        while True:
            scanner_target = 80 if next_positive else -80
            next_positive = not next_positive
            rotateScanner(scanner_target)
            while 'running' in SCANNER_MOTOR.state:
                writeTmpResult(DISTANCE_SENSOR.value(), getActualScannerPos())
    except Exception:
        pass
    LEFT_MOTOR.stop()
    RIGHT_MOTOR.stop()


print('Running...')
run()

print('Exiting...')
LEFT_MOTOR.reset()
RIGHT_MOTOR.reset()

SCANNER_MOTOR.stop_action = 'hold'
SCANNER_MOTOR.run_to_abs_pos(position_sp=0)
SCANNER_MOTOR.wait_until('running')
SCANNER_MOTOR.reset()
