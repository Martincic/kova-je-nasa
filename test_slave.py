import time
import board
import digitalio
from circuitpython_nrf24l01.rf24 import RF24
from Sensors import Sensors

# change these (digital output) pins accordingly
ce = digitalio.DigitalInOut(board.D17)
csn = digitalio.DigitalInOut(board.D16)

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
radio_number = True

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

def slave(timeout=6):
    """Polls the radio and prints the received value. This method expires
    after 6 seconds of no received transmission"""
    nrf.listen = True  # put radio into RX mode and power up
    start_timer = time.monotonic()  # used as a timeout
    while (time.monotonic() - start_timer) < timeout:
        if nrf.available():
            length = nrf.any()  # grab payload length info
            pipe = nrf.pipe  # grab pipe number info
            received = nrf.read(length)  # clears info from any() and nrf.pipe
            # increment counter before sending it back in responding payload
            counter[0] = received[7:8][0] + 1
            nrf.listen = False  # put the radio in TX mode
            result = False
            ack_timeout = time.monotonic_ns() + 200000000
            while not result and time.monotonic_ns() < ack_timeout:
                # try to send reply for 200 milliseconds (at most)
                result = nrf.send(b"World \0" + bytes([counter[0]]))
            nrf.listen = True  # put the radio back in RX mode
            print(
                "Received {} on pipe {}: {}{} Sent:".format(
                    length,
                    pipe,
                    bytes(received[:6]).decode("utf-8"),  # convert to str
                    received[7:8][0],
                ),
                end=" ",
            )
            if not result:
                print("Response failed or timed out")
            else:
                print("World", counter[0])
            start_timer = time.monotonic()  # reset timeout

    # recommended behavior is to keep in TX mode when in idle
    nrf.listen = False  # put the nRF24L01 in TX mode + Standby-I power state


if __name__ == "__main__":
    try:
        while True:
            slave()  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
