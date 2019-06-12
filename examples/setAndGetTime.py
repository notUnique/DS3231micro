# DS3231 library for micropython
# tested on ESP8266
#
# Author: Sebastian Maerker
# License: mit
# 
# only 24h mode is supported
#
# example on how to set the time on the DS3231

import DS3231micro
import machine
import time

# initialize DS3231
rtc = DS3231micro.DS3231(5, 4)

# set time to 2019, November, 23, Monday, 19 h, 50 min, 0 sec
rtc.setDateTime(19, 11, 23, 1, 19, 50, 0)

# print current time for 5 seconds
for each in range(5):
    print(rtc.getDateTime())
    print("\n")
    time.sleep(1)
    
# set time with individual set functions
rtc.setYear(19)
rtc.setMonth(11)
rtc.setDay(23)
rtc.setDayOfWeek(1)
rtc.setHour(9)
rtc.setMinutes(33)
rtc.setSeconds(0)

# get hour, minutes, seconds for 5 seconds
for each in range(5):
    print(rtc.getHour())
    print(rtc.getMinutes())
    print(rtc.getSeconds())
    print("\n")
    time.sleep(1)
