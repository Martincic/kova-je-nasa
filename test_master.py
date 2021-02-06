import time
import board
import digitalio
from Database import Database
from circuitpython_nrf24l01.rf24 import RF24

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
    """Transmits an arbitrary unsigned long value every second"""
    nrf.listen = False  # ensures the nRF24L01 is in TX mode
    while count:
        # construct a payload to send
        # add b"\0" as a c-string NULL terminating char
        buffer = bytes(question, 'utf-8')
        start_timer = time.monotonic_ns()  # start timer
        result = nrf.send(buffer)  # save the response (ACK payload)
        if not result:
            print("send() failed or timed out")
        else:  # sent successful; listen for a response
            nrf.listen = True  # get radio ready to receive a response
            timeout = time.monotonic_ns() + 200000000  # set sentinal for timeout
            while not nrf.available() and time.monotonic_ns() < timeout:
                # this loop hangs for 200 ms or until response is received
                pass
            nrf.listen = False  # put the radio back in TX mode
            end_timer = time.monotonic_ns()  # stop timer
            print(
                "Transmission successful! Time to transmit: "
                "{} us. Sent: {}".format(
                    int((end_timer - start_timer) / 1000),
                    buffer.decode("utf-8"),
                ),
                end=" ",
            )
            if nrf.pipe is None:  # is there a payload?
                # nrf.pipe is also updated using `nrf.listen = False`
                print("Received no response.")
            else:
                length = nrf.any()  # reset with read()
                pipe_number = nrf.pipe  # reset with read()
                received = nrf.read()  # grab the response & return it
                # save new counter from response
                print(
                    "Receieved {} bytes with pipe {}: {}".format(
                        length,
                        pipe_number,
                        bytes(received).decode("utf-8")))
                return received
        count -= 1
        # make example readable in REPL by slowing down transmissions
        time.sleep(1)


if __name__ == "__main__":
    #array of questions/sensors/database tables (they match exactly)
    questions = ['temp', 'humid', 'pressure'] 
    Connection = Database() #init database class
    try:
        while True:
            for question in questions:
                try:
                    answer = askQuestion(question)
                    answer = answer.decode("utf-8")
                    Connection.storeValue(question, answer)
                except AttributeError:
                    pass
            time.sleep(5) 
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
