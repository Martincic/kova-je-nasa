import time
import board
import digitalio
from circuitpython_nrf24l01.rf24 import RF24
from Database import Database

# change these (digital output) pins accordingly
ce = digitalio.DigitalInOut(board.D4)
csn = digitalio.DigitalInOut(board.D5)

# using board.SPI() automatically selects the MCU's
# available SPI pins, board.SCK, board.MOSI, board.MISO
spi = board.SPI()  # init spi bus object

nrf = RF24(spi, csn, ce)

nrf.ack = True  # enable ack upon recieving packets

#set power level
nrf.pa_level = -12

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

#using bool so TX and RX can switch with simple not
radio_number = False

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

def askQuestion(question, count=5):  # count = times question is asked
    nrf.listen = False  #TX mode enabled
    while count:
        # convert question into bytes
        buffer = bytes(question, 'utf-8')
        start_timer = time.monotonic_ns()  # start timer
        answer = nrf.send(buffer)  # save the answer (ACK payload)
        if not answer:
            print("send() failed or timed out")
        else:  # question asked, listen for a response
            nrf.listen = True  # switch to RX mode 
            timeout = time.monotonic_ns() + 200000000  # set sentinal for timeout (nanoseconds)
            while not nrf.available() and time.monotonic_ns() < timeout:
                # this loop hangs for 200 ms or until response is received
                pass
            nrf.listen = False  # put the radio back in TX mode
            end_timer = time.monotonic_ns()  # stop timer
            
            if nrf.pipe is None:  # is there a payload?
                print("Received no response.")
            else:
                answer = nrf.read()  # grab & return the response
                return answer.decode('utf-8')
        count -= 1

if __name__ == "__main__":
    
    #array of questions/sensors/database tables (they match exactly)
    questions = ['temp', 'humid', 'pressure'] 
    Connection = Database() #init database class
    
    try:
        while True:
            for question in questions:
                answer = askQuestion(question)
                Connection.storeValue(question, answer)
                print(question, answer)
            time.sleep(5)
                
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
