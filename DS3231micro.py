# DS3231 library for micropython
# tested on ESP8266
#
# Author: Sebastian Maerker
# License: mit
# 
# only 24h mode is supported
#
# features: 
#    - set time
#    - read time
#    - set alarms

import machine
from math import floor

i2cAddr = 0x68 # change I2C Address here if neccessary

class DS3231:
    
    def __init__(self, i2cClockPin, i2cDataPin):
        # create RTC instance with I2C Pins
        self.sclPin = machine.Pin(i2cClockPin, pull = machine.Pin.PULL_UP, mode=machine.Pin.OPEN_DRAIN)
        self.sdaPin = machine.Pin(i2cDataPin, pull = machine.Pin.PULL_UP, mode=machine.Pin.OPEN_DRAIN)
        
        self.i2cVar = machine.I2C(-1, scl=self.sclPin, sda=self.sdaPin)
        self.i2cAddr = i2cAddr
        
    # get times functions -------------------------------------------------------------------------------------------------------
    
    def getYear(self):
        return decodeToDec(self.i2cVar.readfrom_mem(self.i2cAddr, 0x06, 1))
    
    def getMonth(self):
        temp = self.i2cVar.readfrom_mem(self.i2cAddr, 0x05, 1)
        return decodeToDec(convertToByteType(temp[0] & 0x7F))
    
    def getDay(self):
        # 0 - 31
        return decodeToDec(self.i2cVar.readfrom_mem(self.i2cAddr, 0x04, 1))
            
    def getDayOfWeek(self):
        # 1 - 7
        return decodeToDec(self.i2cVar.readfrom_mem(self.i2cAddr, 0x03, 1))
    
    def getHour(self):
        temp = self.i2cVar.readfrom_mem(self.i2cAddr, 0x02, 1)
        return decodeToDec(convertToByteType(temp[0] & 0x3F))
    
    def getMinutes(self):
        return decodeToDec(self.i2cVar.readfrom_mem(self.i2cAddr, 0x01, 1))
    
    def getSeconds(self):
        return decodeToDec(self.i2cVar.readfrom_mem(self.i2cAddr, 0x00, 1))
    
    def getDateTime(self): 
        # returns whole date and time as list 
        # (last two digits of year, month, day, day of week, hour, minutes, seconds)
        dateTime = [0, 0, 0, 0, 0, 0, 0]
        dateTime[0] = self.getYear()
        dateTime[1] = self.getMonth()
        dateTime[2] = self.getDay()
        dateTime[3] = self.getDayOfWeek()
        dateTime[4] = self.getHour()
        dateTime[5] = self.getMinutes()
        dateTime[6] = self.getSeconds()
        return dateTime
    
    # set times functions -------------------------------------------------------------------------------------------------------
    
    def setYear(self, year): 
        # only last two digits (last two digits are used if longer)
        if(year > 99):
            thousands = floor(year / 100)
            year = year - (thousands * 100)
        self.i2cVar.writeto_mem(self.i2cAddr, 0x06, convertToByteType(encodeToByte(year)))
        
    def setMonth(self, month):
        self.i2cVar.writeto_mem(self.i2cAddr, 0x05, convertToByteType(encodeToByte(month) | 0))
    
    def setDay(self, day):
        # 0 - 31
        self.i2cVar.writeto_mem(self.i2cAddr, 0x04, convertToByteType(encodeToByte(day)))
    
    def setDayOfWeek(self, dayOfWeek):
        # 1 - 7
        self.i2cVar.writeto_mem(self.i2cAddr, 0x03, convertToByteType(encodeToByte(dayOfWeek)))
        
    def setHour(self, hour):
        self.i2cVar.writeto_mem(self.i2cAddr, 0x02, convertToByteType(encodeToByte(hour) & 0x3F))
        
    def setMinutes(self, minutes):
        self.i2cVar.writeto_mem(self.i2cAddr, 0x01, convertToByteType(encodeToByte(minutes)))
    
    def setSeconds(self, seconds):
        self.i2cVar.writeto_mem(self.i2cAddr, 0x00, convertToByteType(encodeToByte(seconds)))
        
    def setDateTime(self, year, month, day, dayOfWeek, hour, minutes, seconds): 
        # set all the date and times (year is last two digits of year)
        self.setYear(year)
        self.setMonth(month)
        self.setDay(day)
        self.setDayOfWeek(dayOfWeek)
        self.setHour(hour)
        self.setMinutes(minutes)
        self.setSeconds(seconds)
        
    # get alarm functions ------------------------------------------------------------------------------------------------------
    
    def getAlarm1(self): 
        # returns list as: 
        # dayOfWeek or day (depending on setup in setAlarm), hour, minutes, seconds, type of alarm
        alarmTime = [0, 0, 0, 0, ""]
        alarmTime[0] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0A, 1)[0]
        alarmTime[1] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x09, 1)[0]
        alarmTime[2] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x08, 1)[0]
        alarmTime[3] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x07, 1)[0]
        alarmTime[4] = decodeAlarmType(alarmTime)
        alarmTime = decodeAlarmTime(alarmTime)
        return alarmTime
        
    def getAlarm2(self): 
        # returns list as: 
        # dayOfWeek or day (depending on setup in setAlarm), hour, minutes, type of alarm
        alarmTime = [0, 0, 0, ""]
        alarmTime[0] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0D, 1)[0]
        alarmTime[1] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0C, 1)[0]
        alarmTime[2] = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0B, 1)[0]
        alarmTime[3] = decodeAlarmType(alarmTime)
        alarmTime = decodeAlarmTime(alarmTime)
        return alarmTime
    
    def alarmTriggert(self, alarmNumber):
        # check if alarm triggert and reset alarm flag
        statusBits = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0F, 1)[0]
        if(statusBits & alarmNumber):
            self.resetAlarm(alarmNumber)
            return True
        else:
            return False
        
    # set alarm functions -------------------------------------------------------------------------------------------------------
    
    def setAlarm1(self, day, hour, minutes, seconds = 0, alarmType = "everyDay"):
        # alarm Types are:
        #    "everySecond"  - alarm every second
        #    "everyMinute"  - alarm when seconds match
        #    "everyHour"    - alarm when minutes and seconds match
        #    "everyDay"     - alarm when hours, minutes and seconds match ! default !
        #    "everyWeek"    - alarm when day of week, hours, minutes and seconds match
        #    "everyMonth"   - alarm when day of month, hours, minutes and seconds match
        
        alarmTime = encodeDateTime(day, hour, minutes, seconds, alarmType)
        self.i2cVar.writeto_mem(self.i2cAddr, 0x07, convertToByteType(alarmTime[3]))
        self.i2cVar.writeto_mem(self.i2cAddr, 0x08, convertToByteType(alarmTime[2]))
        self.i2cVar.writeto_mem(self.i2cAddr, 0x09, convertToByteType(alarmTime[1]))
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0A, convertToByteType(alarmTime[0]))
        
    def setAlarm2(self, day, hour, minutes, alarmType = "everyDay"): 
        # alarm Types are:
        #    "everyMinute"  - alarm every minute (at 00 seconds)
        #    "everyHour"    - alarm when minutes match
        #    "everyDay"     - alarm when hours and minutes match ! default !
        #    "everyWeek"    - alarm when day of week, hours and minutes match
        #    "everyMonth"   - alarm when day of month, hours and minutes match
        seconds = 0
        alarmTime = encodeDateTime(day, hour, minutes, seconds, alarmType)
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0B, convertToByteType(alarmTime[2]))
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0C, convertToByteType(alarmTime[1]))
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0D, convertToByteType(alarmTime[0]))
        
    def turnOnAlarmIR(self, alarmNumber):
        # set alarm interrupt. AlarmNumber 1 or 2
        # when turned on, interrupt pin on DS3231 is "False" when alarm has been triggert
        controlRegister = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0E, 1)[0]
        setByte = 0x04
        setByte = setByte + alarmNumber
        setByte = controlRegister | setByte
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0E, convertToByteType(setByte))
    
    def turnOffAlarmIR(self, alarmNumber):
        # turn off alarm interrupt. Alarmnumber 1 or 2
        # only initiation of interrupt is turned off, 
        # alarm flag is still set when alarm conditions meet (i don't get it either)
        controlRegister = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0E, 1)[0]
        setByte = 0xFF
        setByte = setByte - alarmNumber
        setByte = controlRegister & setByte
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0E, convertToByteType(setByte))
    
    def resetAlarmFlag(self, alarmNumber):
        statusBits = self.i2cVar.readfrom_mem(self.i2cAddr, 0x0F, 1)[0]
        self.i2cVar.writeto_mem(self.i2cAddr, 0x0F, convertToByteType(statusBits & (0xFF - alarmNumber)))
        
def convertToByteType(number):
    return bytes([number])

def decodeToDec(byte):
    return ((byte[0] >> 4) * 10) + (byte[0] & 0x0F)

def encodeToByte(dec):
    tens = floor(dec / 10)
    ones = dec - tens*10
    return (tens << 4) + ones

def decodeAlarmType(alarmTime):
    if(len(alarmTime) > 4):
        m1Bit = (alarmTime[3] & 0x80) >> 7
    else:
        m1Bit = False
    m2Bit = (alarmTime[2] & 0x80) >> 7
    m3Bit = (alarmTime[1] & 0x80) >> 7
    m4Bit = (alarmTime[0] & 0x80) >> 7
    dayBit = (alarmTime[0] & 0x40) >> 6
    
    if(m1Bit and m2Bit and m3Bit and m4Bit):
        return "everySecond"
    elif(not m1Bit and m2Bit and m3Bit and m4Bit):
        return "everyMinute"
    elif(not m1Bit and not m2Bit and m3Bit and m4Bit):
        return "everyHour"
    elif(not m1Bit and not m2Bit and not m3Bit and m4Bit):
        return "everyDay"
    elif(not dayBit and not m1Bit and not m2Bit and not m3Bit and not m4Bit):
        return "everyMonth"
    elif(dayBit and not m1Bit and not m2Bit and not m3Bit and not m4Bit):
        return "everyWeek"
    else:
        return "noValidAlarmType"
    
def decodeAlarmTime(alarmTime):
    alarmTime[0] = decodeToDec(convertToByteType(alarmTime[0] & 0x3F))
    alarmTime[1] = decodeToDec(convertToByteType(alarmTime[1] & 0x3F))
    alarmTime[2] = decodeToDec(convertToByteType(alarmTime[2] & 0x7F))
    if(len(alarmTime) > 4):
        alarmTime[3] = decodeToDec(convertToByteType(alarmTime[3] & 0x7F))
    return alarmTime

def encodeAlarmType(alarmType):
    if(alarmType == "everySecond"):
        return 15   #0b01111
    elif(alarmType == "everyMinute"):
        return 14   #0b01110
    elif(alarmType == "everyHour"):
        return 12   #0b01100
    elif(alarmType == "everyDay"):
        return 8    #0b01000
    elif(alarmType == "everyMonth"):
        return 0    #0b00000
    elif(alarmType == "everyWeek"):
        return 16   #0b10000
    else:
        raise ValueError("""Not a supported alarmType. Options are: 
        'everySecond' (only Alarm 1), 'everyMinute', 'everyHour', 'everyDay', 'everyMonth', 'everyWeek'""")

def encodeDateTime(day, hour, minutes, seconds, alarmType):
    alarmBits = encodeAlarmType(alarmType)
    alarmTime = [0, 0, 0, 0]
    alarmTime[0] = (encodeToByte(day) & 0x3F) | ((alarmBits & 0x10) << 2) | ((alarmBits & 0x08) << 4)
    alarmTime[1] = (encodeToByte(hour) & 0x3F) | ((alarmBits & 0x04) << 5)
    alarmTime[2] = (encodeToByte(minutes) & 0x7F) | ((alarmBits & 0x02) << 6)
    alarmTime[3] = (encodeToByte(seconds) & 0x7F) | ((alarmBits & 0x01) << 7)
    return alarmTime