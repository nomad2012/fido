#!/usr/bin/python

import serial
import time

# Servo numbers
HIPS = 1
NECK = 2
HEAD = 3
JAW = 4
TAIL = 5

# Servo positions
HIPS_DOWN=70
HIPS_UP=1
NECK_DOWN=80
NECK_UP=170
HEAD_LEFT=0x6A-0x25
HEAD_CENTER=0x6A
HEAD_RIGHT=0x6A+0x25
JAW_OPEN=160
JAW_CLOSED=70
TAIL_LEFT=0x50
TAIL_CENTER=0x80
TAIL_RIGHT=0xB0

port = serial.Serial("/dev/ttyUSB0", 19200, timeout=0.1)

def get_servo_position(servo_number=1):
    port.write(">1{0}g".format(servo_number))
    response = port.read(2)
    if len(response) != 2:
        print "get_servo_position: bad response: {0}".format(repl(response))
    return ord(response[0])

def set_servo(servo_number=1, position=0):
    port.write(">1{0}a{1}".format(servo_number, chr(position)))
    ack = port.read()
    if ack != '\r':
        print "set_servo: bad ack = {0}\n".format(repr(ack))

def ramp_servo(servo_number=0, position=0, step=1):
    for i in range(get_servo_position(servo_number), position, step):
        set_servo(servo_number, i)
    set_servo(servo_number, position)

def wag(servo, left, right, center, times=1,delay=0.3):
    for i in xrange(times):
        set_servo(servo, right)
        time.sleep(delay)
        set_servo(servo, left)
        time.sleep(delay)
    set_servo(servo, center)

def slow_wag(servo, left, right, center, rate, times=1, delay=0.3):
    if left > right:
        my_rate = -rate
    else:
        my_rate = rate
        
    for i in xrange(times):
        ramp_servo(servo, left, my_rate)
        time.sleep(delay)
        ramp_servo(servo, right, -my_rate)
        time.sleep(delay)
    ramp_servo(servo, center, delay)

def wag_tail(times=5, delay=0.2):
    wag(TAIL, TAIL_LEFT, TAIL_RIGHT, TAIL_CENTER, times, delay)

def wag_head(times=5, delay=0.25):
    wag(HEAD, HEAD_LEFT, HEAD_RIGHT, HEAD_CENTER, times, delay)

def nod(times=3, delay=0.3):
    wag(NECK, NECK_DOWN, NECK_UP, NECK_UP, times, delay)

def open_mouth():
    set_servo(JAW, JAW_OPEN)

def close_mouth():
    set_servo(JAW, JAW_CLOSED)

def raise_head():
    ramp_servo(NECK, NECK_UP, 1)

def lower_head():
    ramp_servo(NECK, NECK_DOWN, -1)
