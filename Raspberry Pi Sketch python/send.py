#!/usr/bin/env python

import time
from RF24 import *

radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]

send_payload = 'Hello World'
millis = lambda: int(round(time.time() * 1000))

print 'send.py'
radio.begin()
radio.enableDynamicPayloads()
radio.setRetries(5,15)
radio.printDetails()


print 'Starting transmission'
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[1])

# forever loop
while 1:
    # First, stop listening so we can talk.
    radio.stopListening()

    radio.write(send_payload)

    # Now, continue listening
    #radio.startListening()

    # Wait here until we get a response, or timeout
    #started_waiting_at = millis()
    #timeout = False
    #while (not radio.available()) and (not timeout):
    #    if (millis() - started_waiting_at) > 500:
            timeout = True

    # Describe the results
    #if timeout:
    #    print 'failed, response timed out.'
    #else:
    #    # Grab the response, compare, and send to debugging spew
    #    len = radio.getDynamicPayloadSize()
    #    receive_payload = radio.read(len)
    #
    #    # Spew it
    #    print 'got response size=', len, ' value="', receive_payload, '"'

    # Update size for next time.
    #next_payload_size += payload_size_increments_by
    #if next_payload_size > max_payload_size:
    #    next_payload_size = min_payload_size
    time.sleep(5)

