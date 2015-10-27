#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, argparse

#FR:2:TO:1:TS:0:AC:1:MSG:36.00;24.00
# add arguments for the command line partameters
parser = argparse.ArgumentParser()
parser.add_argument('-ts', '--task', help="give the task id", dest='ts', default='123')
parser.add_argument('-fr', '--from', help="give the device id from witch it will send", dest='fr', default='1')
parser.add_argument('-to', '--to', help="give the device id witch it will send to", dest='to', default='2')
parser.add_argument('-ac', '--action', help="give the action id", dest='ac', default='3')
parser.add_argument('-msg', '--message', help="give data to send with it", dest='msg', default='None')

args = parser.parse_args()

ts = args.ts
fr = args.fr
to = args.to
ac = args.ac
msg = args.msg
topipe = int(to) - 1

import time
from RF24 import *

# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
# Init radio
radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

# define pipes
mypipe = 0
myid = 1
pipes = [0xF0F0F0F0A1, 0xF0F0F0F0B2, 0xF0F0F0F0C3, 0xF0F0F0F0D4, 0xF0F0F0F0E5, 0xF0F0F0F0F6]

# variables
millis = lambda: int(round(time.time() * 1000))
waiting_timeout = 1000
payload = "FR:" + fr + ":TO:" + to + ":TS:" + ts + ":AC:" + ac + ":MSG:" + msg

# start radio
radio.begin()

# settings radio
radio.enableDynamicPayloads()
radio.setRetries(15,15)

radio.setPALevel(RF24_PA_HIGH)
radio.setDataRate(RF24_250KBPS)

# print radio details
radio.printDetails()

# opening pipes
radio.openWritingPipe(pipes[mypipe])
radio.openReadingPipe(topipe,pipes[topipe])

radio.startListening()

# First, stop listening so we can talk.
radio.stopListening()
    
# send
print "Send: ", payload
radio.write(payload)
    
# start continue listening
radio.startListening()
    
# Wait here until we get a response, or timeout
waiting_started = millis()
    
timeout = False
while (not radio.available()) and (not timeout):
    if (millis() - waiting_started) > waiting_timeout:
        timeout = True
    
if timeout:
    print "Timeout"
    print "FR:" + fr + ":TO:" + to + ":TS:" + ts + ":AC:" + ac + ":MSG:timeout"
else:
    # Grab the response, compare, and send to debugging spew
    len = radio.getDynamicPayloadSize()
    receive_payload = radio.read(50)
    print 'got response size=', len, ' value="', receive_payload, '"'
    print receive_payload
    print "Received: ", receive_payload
    print receive_payload
