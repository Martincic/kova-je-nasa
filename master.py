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

def askQuestion(question, count=5):  # count = 5 will only ask 5 times (send 5 packets containing question)
    nrf.listen = False  # put radio in TX mode

    while count:
        # construct a payload to send, convert question to bytes and encode w/ utf-8
        buffer = bytes(question, 'utf-8')
        answer = nrf.send(buffer)  # send question and save the response (ACK payload)
        
        if answer:#check if we recieved an answer
            if isinstance(answer, bool): #check if answer is empty
                print(" Received an empty ACK packet")
            else:
                #print and return the answer
                print(answer.decode("utf-8"))
                return answer
        
        #if there is no answer wait and ask again counter times
        elif not answer:
            print("send() failed or timed out")
            time.sleep(0.2)  # let the RX node prepare a new ACK payload
            count -= 1
            
    
if __name__ == "__main__":
    
    questions = ['temp'] #array of sensors
    Connection = Database(); #init database class
    
    try:
        while True:
            for question in questions:
                answer = askQuestion(question)
                Connection.storeValue(question, answer)
            time.sleep(5)
                
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
