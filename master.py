import time
import board
import digitalio
import busio
import adafruit_mcp9808
import adafruit_bmp280
from Database import Database
from circuitpython_nrf24l01.rf24 import RF24
from adafruit_htu21d import HTU21D

# change these (digital output) pins accordingly
ce = digitalio.DigitalInOut(board.D4)
csn = digitalio.DigitalInOut(board.D5)

# using board.SPI() automatically selects the MCU's
# available SPI pins, board.SCK, board.MOSI, board.MISO
spi = board.SPI()  # init spi bus object

nrf = RF24(spi, csn, ce)

nrf.ack = True  # enable ack upon recieving packets

#set power level
nrf.pa_level = 0

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

#using bool so TX and RX can switch with simple not
radio_number = False

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

#init I2C
i2c_bus = None
mcp = None
bmp280 = None
sht21 = None
try:
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    #Initialise mcp, bmp & sht21
    mcp = adafruit_mcp9808.MCP9808(i2c_bus)
    bmp280 = adafruit_bmp280.Adafruit_BMP_I2C(i2c_bus)
    sht21 = HTU21D(i2c_bus)
    bmp280.sea_level_pressure = 1027.25
except ValueError:
    print("No I2C device found")
#calibrate bmp280

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
            timeout = time.monotonic_ns() + 1000000000  # set sentinal for timeout
            while not nrf.available() and time.monotonic_ns() < timeout:
                # this loop waits 1s for slave to read data and send back
                pass
            nrf.listen = False  # put the radio back in TX mode
            end_timer = time.monotonic_ns()  # stop timer
            
            if nrf.pipe is None:  # is there a payload?
                # nrf.pipe is also updated using `nrf.listen = False`
                pass
            else:
                print(
                "Transmission successful! Sent: {}".format(buffer.decode("utf-8"),),
                end=" ",
                )
                length = nrf.any()  # reset with read()
                pipe_number = nrf.pipe  # reset with read()
                received = nrf.read()  # grab the response & return it
                # save new counter from response
                print(
                    "Receieved {} ".format(
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
            try:
                print("MCP Temp: %0.1f C" % mcp.temperature)
                print("BMP Temp: %0.1f C" % bmp280.temperature)
                print("BMP Pressure: %0.1f hPa" % bmp280.pressure)
                print("BMP Altitude: %0.1f m" % bmp280.altitude)
                print("SHT21 Temp: %0.1f C" % sht21.temperature)
                print("SHT21 Humid: %0.1f C" % sht21.relative_humidity)
            except:
                print("Error reading i2c sensors")
                
            time.sleep(5) 
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")

