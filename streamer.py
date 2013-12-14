#!/usr/bin/env python

import serial, time, random


NUMBER_OF_LEDS = 64
FRAME_FRAGMENTS = [0x20, 0x21, 0x22, 0x23]
PIXEL_PER_FRAME_FRAGMENT = NUMBER_OF_LEDS / len(FRAME_FRAGMENTS)

HEADER = 0x10
HEADER_LENGTH = 3
ACK_REPLY_LENGTH = 4
MAX_ACK_WAIT_TIME = 50

BAUD_RATE = 115200

port = serial.Serial('/dev/cu.usbserial-A60205IF', BAUD_RATE, timeout=0.05)

print "Sleeping 2 seconds to let arduino reboot..."
time.sleep(2)

frame = []
for f in range(NUMBER_OF_LEDS):
    frame.append([0,0,0])

def makeFrame(r, g, b):
    frame = []
    for f in range(NUMBER_OF_LEDS):
        frame.append([r,g,b])
    return frame

def sendFrame(frame):

    ba = bytearray((PIXEL_PER_FRAME_FRAGMENT * 3) + HEADER_LENGTH)
    ba[0] = HEADER
    ba[1] = HEADER

    for fragment in range(len(FRAME_FRAGMENTS)):

        crc = 0

        ba[2] = FRAME_FRAGMENTS[fragment]

        for index in range(PIXEL_PER_FRAME_FRAGMENT):
            pixel = index + (PIXEL_PER_FRAME_FRAGMENT * fragment)

            crc += frame[pixel][0]
            crc += frame[pixel][1]
            crc += frame[pixel][2]

            ba[HEADER_LENGTH + (index * 3)] = frame[pixel][0]
            ba[HEADER_LENGTH + (index * 3) + 1] = frame[pixel][1]
            ba[HEADER_LENGTH + (index * 3) + 2] = frame[pixel][2]

        port.write(ba)

        # get ack
        reply = port.read(ACK_REPLY_LENGTH)

        if len(reply) < ACK_REPLY_LENGTH:
            print "No serial ACK reply for frame fragment " + str(fragment) + " after waiting for " + str(MAX_ACK_WAIT_TIME) + "ms. Serial port has only " + str(len(reply)) + " bytes available."
            return False

        ack = map(ord, reply)

        for i in range(len(ack)):
            if ack[i] == HEADER:
                stateCode = ack[i+3]
                receivedValue = (int(ack[i+1]) & 0xff) << 8 | (int(ack[i+2]) & 0xff)

                if stateCode == 0x30 and receivedValue == crc:
                    break
                else:
                    print "wtf??"
                    print crc
                    print stateCode
                    print receivedValue
                    break


newframe = frame[:]

for pixel in range(len(newframe)):
    newframe[pixel] = [255,0,0]

sendFrame(newframe)

fps = 0
last_second = int(time.time())

while True:

    newframe = frame[:]
#    newframe[33] = [255,255,255]
    for pixel in range(len(newframe)):
        newframe[pixel] = [0, random.randint(0,255), 0]

    sendFrame(newframe)

    fps += 1
    if int(time.time()) > last_second:
        print str(fps) + ' frames per second'
        last_second = int(time.time())
        fps = 0

"""
for i in range(NUMBER_OF_LEDS):
    sendFrame(frame)

    newframe = frame[:]

    newframe[i] = [255,0,0]

    print "Trying to light up LED " + str(i)
    sendFrame(newframe)

    print "Press a key"
    raw_input()

"""


