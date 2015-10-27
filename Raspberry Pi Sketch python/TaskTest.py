#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

# first [0] argument is master
try:
    fr = sys.argv[1]
except IndexError:
   print "error;no from"
   sys.exit(0)

try:
    to = sys.argv[2]
except IndexError:
   print "error;no to"
   sys.exit(0)

try:
    ac = sys.argv[3]
except IndexError:
   print "error;no action"
   sys.exit(0)

msg = "get action"

topipe = int(to) - 1

import time
from RF24 import *

# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
# Init radio
radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

# define pipes
masterid = 1;
myid = 1
masterpipe = 0;
mypipe = 0

pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2, 0xF0F0F0F0E2, 0xF0F0F0F0D3, 0xF0F0F0F0E4, 0xF0F0F0F0D5]

# variables
millis = lambda: int(round(time.time() * 1000))
waiting_timeout = 3000
payload = "AC:" + ac + ":MS:" + msg # can not send task it gets to big

# start radio
radio.begin()

# settings radio
#radio.enableDynamicPayloads()
#radio.setPayloadSize(17)
radio.setRetries(5,15)

#radio.setPALevel(RF24_PA_HIGH)
radio.setDataRate(RF24_250KBPS)
#radio.setCRCLength(RF24_CRC_8)
radio.setChannel(114)

# print radio details
radio.printDetails()

# opening pipes
radio.openWritingPipe(pipes[masterpipe])
radio.openReadingPipe(1,pipes[topipe])

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
    print "error;timeout"
else:
    # Grab the response, compare, and send to debugging spew
    len = radio.getDynamicPayloadSize()
    receive_payload = radio.read(len)
    print 'got response size=', len, ' value="', receive_payload, '"'
    print receive_payload
    sys.exit(1)
