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
topipe = to -1

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
radio.setRetries(5,15)

# print radio details
radio.printDetails()

# opening pipes
radio.openWritingPipe(pipes[mypipe])
radio.openReadingPipe(topipe,pipes[topipe])

radio.startListening()

def send():
    # First, stop listening so we can talk.
    radio.stopListening()
    
    # send
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
        print "FR:" + fr + ":TO:" + to + ":TS:" + ts + ":AC:" + ac + ":MSG:timeout"
    else:
        # Grab the response, compare, and send to debugging spew
        len = radio.getDynamicPayloadSize()
        receive_payload = radio.read(len)
        print receive_payload

def receive():
    # if there is data ready
    if radio.available():
        while radio.available():
            # Fetch the payload, and see if this was the last one.
	    len = radio.getDynamicPayloadSize()
	    receive_payload = radio.read(len)
            
	    # Spew it
	    print receive_payload
            
            # First, stop listening so we can talk
            #radio.stopListening()
            
            # Send the final one back.
            #radio.write(receive_payload)

            # Now, resume listening so we catch the next packets.
            radio.startListening()
