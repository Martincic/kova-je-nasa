# Kova je naša

## About
Python based code consisting of master and slave radio transcievers (NRF24L01 +) 
Slave is inside the coal mine at depth of roughly 150m and collecting data from 
various sensors such as temperature, humidity, pressure, etc. 
Master is on top of the mine calling slave every once in a while asking for data to which 
slave responds with an answer. Master saves the data in database which will be used for further 
refference in dedicated webpage.

## Ukratko
Kod zasnovan na Pythonu koji se sastoji od glavnog i podređenog radijskog primopredajnika (NRF24L01 +)
Podređeni se nalazi u rudniku ugljena na dubini od oko 150 m te prikuplja podatke
sa raznih senzora poput temperature, vlage, tlaka itd.
Glavni je na vrhu rudnika i svako malo zove podređenog i traži podatke kojima
rob odgovara odgovorom. Glavni sprema podatke u bazu podataka koja će se koristiti za kao
daljnja referenca na web stranici.

## Pinout

** NOTE: Slave.py is using CE as pin 17 and CSN as pin 16 (because I fryed my GPIO4) This can be changed in line 16 and 17 **
![alt text](https://github.com/Martincic/kova-je-nasa/blob/main/pinout.png?raw=true)
