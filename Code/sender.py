## This file define sender behavior
## Run this file, allows user to input a string, 
## then generate a series of BlueTooth packet as a .wav file
## The .wav file will be saved, then pot it through loudspeaker
import utils
import FSK
from time import sleep
class Sender:
    pass

def main():
    message = 'abcdefg'
    packet_list = utils.generatePacket(message)
    for i in range(len(packet_list)):
        print(packet_list[i])
        FSK.Modulator(packet_list[i], 'test.wav')
        print('hello')
        sleep(0.5)
    pass

if __name__ == "__main__":
    main()