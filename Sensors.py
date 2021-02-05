import RPi.GPIO as GPIO
import Adafruit_DHT

class Sensors:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.sensors = ['temp', 'humid', 'pressure']
        self.DHT_SENSOR = Adafruit_DHT.DHT22
        self.DHT_PIN = 27 #array of answers/sensors/database tables (they match exactly)
        self.answers = {'temp':None, 'humid':None, 'pressure':None}
        
    def populateAnswers(self):
        self.readTempHumid()
        
    def readTempHumid(self):
        for x in range(3): #DHT is not constant output
            humidity, temperature = Adafruit_DHT.read(self.DHT_SENSOR, self.DHT_PIN)
            if humidity is not None and temperature is not None:
                self.answers['temp'] = temperature
                self.answers['humid'] = humidity
#                print("Temp:", self.getAnswer('temp'))
 #               print("Humid:", self.getAnswer('humid'))
                
    def getAnswer(self, question):
        return str(self.answers[question])[0:5]
            
