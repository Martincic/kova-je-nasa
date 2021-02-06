import RPi.GPIO as GPIO
import Adafruit_DHT
import sys
from time import sleep

class Sensors:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.DHT_SENSOR = Adafruit_DHT.DHT22
        self.DHT_PIN = 27 #array of answers/sensors/database tables (they match exactly)
        self.answers = {'temp':None, 'humid':None, 'pressure':None}
        
    def populateAnswers(self):
        self.readTempHumid()
        #self.readPressure()
        #self.takeAPhoto()
        #etc..
        
    def readTempHumid(self):
        for x in range(5): #DHT is not constant output
            sleep(0.1)
            humidity, temperature = Adafruit_DHT.read(self.DHT_SENSOR, self.DHT_PIN)
            if humidity is not None and temperature is not None:
                self.answers['temp'] = temperature
                self.answers['humid'] = humidity

    def getAnswer(self, question):
        try:
            return str(self.answers[question])
        except KeyError:
            pass
