# NOTE: For efficient naviation and table of contents of this file, use PyCharm bookmarks feature.
# AUTHOR: Eric Blagg (eric.blagg@triobe.tech)
# v1.0.1

#SECTION 1 BEGIN: import needed modules for running program

import time
import utime
from ntptime import settime
import network
import machine
import neopixel
from machine import Pin, I2C, RTC
from esp8266_i2c_lcd import I2cLcd
from thermal_printer import *
from rotary_irq_esp import RotaryIRQ
import os
# import gc
# import senko

#SECTION 1 END


#SECTION 2 BEGIN: define initial global settings and variables

# define menu lists
user_days_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
mainMenu_list = ['Set Use Days', 'Configure Wifi', 'Change Date', 'Custom Label', 'Recent Labels', 'Change Time Zone', 'Factory Reset', 'Back']
setuseDays_list = list(range(0, 10))
years_list = list(range(2021, 2023))
months_list = list(range(1, 13))
days_list = list(range(1, 32))
hours_list = list(range(1, 13))
minutes_list = list(range(1, 61))
ampm_list = ['am', 'pm']
yesno_list = ['YES', 'NO']
charac_list = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 ')
wifi_charac_list = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+=.,')
charac_list.insert(0, 'DONE')
wifi_charac_list.insert(0, 'DONE')
charac_list.insert(1, 'BACK')
wifi_charac_list.insert(1, 'BACK')
charac_list.insert(2, '*TODAY')
charac_list.insert(3, '*TOMORROW')
charac_list.insert(4, '*NOW')

timezone_list = ['EDT', 'EST', 'CDT', 'CST', 'MDT', 'MST', 'PDT', 'PST', 'AKDT', 'AKST', 'HDT', 'HST']
timezone_dict = {'EDT':-4, 'EST':-5, 'CDT':-5, 'CST':-6, 'MDT':-6, 'MST':-7, 'PDT':-7, 'PST':-8, 'AKDT':-8, 'AKST':-9, 'HDT':-9, 'HST':-10}
date_dict = {'Year':years_list, 'Month':months_list, 'Day':days_list, 'Hour':hours_list, 'Minute':minutes_list,
             'AM_PM':ampm_list}
recentLabels_list = []
selection = ''
ssid_name = ''
ssid_pwrd = ''
rtc = RTC()
time_zone = ''
time_zone_value = ''

# define function definitions for rotary encoder
button_press = Pin(26, Pin.IN, Pin.PULL_DOWN)
r = RotaryIRQ(pin_num_clk=14,
              pin_num_dt=13,
              min_val=0,
              max_val=500,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
lastval = r.value()
val = r.value()

# define placement counters
mainMenu_counter = 0
setuseDays_counter = 0
changeDate_counter = 0
timezone_counter = 0
yesno_counter = 0

# define printer
printer = thermal_printer()
printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small

# define function definitions for lcd screen control
DEFAULT_I2C_ADDR = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

# define function definitions for break beam sensors (2)
break_beam_1 = Pin(23, Pin.IN, Pin.PULL_UP)
break_beam_2 = Pin(18, Pin.IN, Pin.PULL_UP)

# define class for neopixel for LED lights
led_qty = 9
led_pin = 15
led_np = neopixel.NeoPixel(machine.Pin(led_pin), led_qty)

#SECTION 2 END


#SECTION 3 BEGIN: create main menu that will provide direction for menu options upon user input

def mainMenu():
    global mainMenu_counter
    global selection
    global lcd
    global rtc
    print('Main Menu:', mainMenu_list[mainMenu_counter])
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Main Menu:')
    lcd.move_to(0, 1)
    lcd.putstr(mainMenu_list[mainMenu_counter])
    lcd.move_to(0, 0)
    selection=rotary_change()

    if selection == 'a':
        if mainMenu_counter == 0:
            mainMenu_counter = len(mainMenu_list) - 1
        else:
            mainMenu_counter -= 1
        mainMenu() ####RE-RUNNING ADDS TO RECURSION STACKS....
    elif selection == 'b':
        if mainMenu_counter == len(mainMenu_list) - 1:
            mainMenu_counter = 0
        else:
            mainMenu_counter += 1
        mainMenu() ####RE-RUNNING ADDS TO RECURSION STACKS....
    elif selection == 'c':
        choice = mainMenu_list[mainMenu_counter]
        print(choice, 'selected!')
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(choice + '\nselected!')
        time.sleep(1)
        selection = ''
        mainMenu_counter = 0
        if choice == 'Set Use Days':
            setuseDays()
        elif choice == 'Configure Wifi':
            configureWifi()
        elif choice == 'Change Date':
            changedate()
        elif choice == 'Custom Label':
            customLabel()
        elif choice == 'Recent Labels':
            recentLabels()
        elif choice == 'Change Time Zone':
            time_zone_selection()
            default_screen()
        elif choice == 'Factory Reset':
            factory_reset()
        else:
            default_screen()

#SECTION 3 END


#SECTION 4 BEGIN: create function for user to set days in use period accessible via main menu

def setuseDays():
    global setuseDays_counter
    global selection
    global user_days
    global useby_date
    global lcd

    print('Set Use Days: '+ str(setuseDays_list[setuseDays_counter]))
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Set Use Days: '+ str(setuseDays_list[setuseDays_counter]))
    selection = rotary_change()

    if selection == 'a':
        if setuseDays_counter == 0:
            setuseDays_counter = len(setuseDays_list) - 1
        else:
            setuseDays_counter -= 1
        setuseDays() ####RE-RUNNING ADDS TO RECURSION STACKS....
    elif selection == 'b':
        if setuseDays_counter == len(setuseDays_list) - 1:
            setuseDays_counter = 0
        else:
            setuseDays_counter += 1
        setuseDays() ####RE-RUNNING ADDS TO RECURSION STACKS....
    elif selection == 'c':
        choice = setuseDays_list[setuseDays_counter]
        print(choice, 'selected!')
        user_days = choice
        with open("user_days.txt", 'w') as user_days_file:
            user_days_file.write(str(choice))
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(str(choice) + ' selected!')
        useby_date = use_days_compute(choice)
        setuseDays_counter = 0
        selection = ''
        default_screen()

#SECTION 4 END


#SECTION 5 BEGIN: create function for user to configure wifi settings

def configureWifi():
    global selection
    global lcd
    global ssid_name
    global ssid_pwrd
    global wifi_charac_list
    global rtc
    global time_zone_value

    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    wifi_data = nic.scan()
    ssid_counter = 0
    ssids_list = [i[0].decode('utf-8') for i in wifi_data]
    temp_ssid_pwrd = ''

    while True:
        print('Scroll to Select SSID:', ssids_list[ssid_counter])

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr('Select SSID:')
        lcd.move_to(0, 1)
        lcd.putstr(ssids_list[ssid_counter][:16])

        selection = rotary_change()
        if selection == 'a':
            if ssid_counter == 0:
                ssid_counter = len(ssids_list) - 1
            else:
                ssid_counter -= 1
        elif selection == 'b':
            if ssid_counter == len(ssids_list) - 1:
                ssid_counter = 0
            else:
                ssid_counter += 1
        elif selection == 'c':
            choice = ssids_list[ssid_counter]
            print(choice, 'selected!')
            lcd.clear()
            lcd.putstr(choice + ' selected!')

            ssid_counter = 0
            ssid_name = choice
            selection = ''
            break

    while True:
        print('Scroll to Enter Password:', wifi_charac_list[ssid_counter])

        lcd.clear()
        lcd.putstr('Scroll to Enter\nPassword: ' + wifi_charac_list[ssid_counter])
        selection = rotary_change()
        if selection == 'a':
            if ssid_counter == 0:
                ssid_counter = len(wifi_charac_list) - 1
            else:
                ssid_counter -= 1
        elif selection == 'b':
            if ssid_counter == len(wifi_charac_list) - 1:
                ssid_counter = 0
            else:
                ssid_counter += 1
        elif selection == 'c':
            choice = wifi_charac_list[ssid_counter]
            print(choice, 'selected!')
            if choice == 'BACK':
                temp_ssid_pwrd = temp_ssid_pwrd[:-1]
                print(temp_ssid_pwrd)
                lcd.clear()
                lcd.putstr('Charac Deleted!\n' + temp_ssid_pwrd)
                time.sleep(1)
            elif choice != 'DONE':
                temp_ssid_pwrd = temp_ssid_pwrd + choice
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr(choice + ' selected!')
                lcd.move_to(0, 1)
                lcd.putstr(temp_ssid_pwrd)
                time.sleep(1)
            else:
                print('Password Complete:', temp_ssid_pwrd)
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr('Password Entered')
                lcd.move_to(0, 1)
                lcd.putstr(temp_ssid_pwrd)
                charac_counter = 0
                time.sleep(1)

                lcd.clear()
                lcd.putstr('Connecting to\nwifi...')
                nic.connect(ssid_name, str(temp_ssid_pwrd))
                #time.sleep(2)
                for x in range(1,10):
                    print('sleep cycle1', x)
                    print(nic.isconnected())
                    time.sleep(1)
                if nic.isconnected() == True:
                    lcd.clear()
                    lcd.putstr('Wifi Connected\nSuccessfully')

                    ssid_pwrd = temp_ssid_pwrd

                    #to save ssid and password into settings
                    with open("ssid_pwrd.txt", 'w') as ssid_pwrd_file:
                        ssid_pwrd_file.write(ssid_pwrd)
                    with open("ssid.txt", 'w') as ssid_name_file:
                        ssid_name_file.write(ssid_name)

                    time.sleep(2)
                    settime()
                    for y in range(1, 5):
                        print('sleep cycle1', y)
                        time.sleep(1)
                    print(utime.localtime())
                    live_date_tuple = utime.localtime()
                    live_date = (live_date_tuple[0], live_date_tuple[1], live_date_tuple[2], live_date_tuple[6],
                                 live_date_tuple[3] + time_zone_value, live_date_tuple[4], live_date_tuple[5], 0)
                    rtc.datetime(live_date)
                    print(rtc.datetime())
                    #ota_update()
                else:
                    lcd.clear()
                    lcd.putstr('Wifi Failed to\nConnect!')
                    time.sleep(2)
                    nic.active(False)
                    print(utime.localtime())
                selection = ''
                break
    default_screen()

#SECTION 5 END


#SECTION 6 BEGIN: function to allow user to set date manually if not connected to wifi

def changedate():
    global changeDate_counter
    global selection
    global lcd
    global rtc

    for key in date_dict:
        while True:
            print('Select', key, ':', date_dict[key][changeDate_counter])
            lcd.clear()
            lcd.putstr('Select' + key + ':' + str(date_dict[key][changeDate_counter]))
            selection = rotary_change()
            if selection == 'a':
                if changeDate_counter == 0:
                    changeDate_counter = len(date_dict[key]) - 1
                else:
                    changeDate_counter -= 1
            elif selection == 'b':
                if changeDate_counter == len(date_dict[key]) - 1:
                    changeDate_counter = 0
                else:
                    changeDate_counter += 1
            elif selection == 'c':
                choice = date_dict[key][changeDate_counter]
                print(choice, 'selected!')
                lcd.clear()
                lcd.putstr(str(choice) + ' selected!')
                changeDate_counter = 0
                selection = ''
                if key == 'Year':
                    set_Year = choice
                elif key == 'Month':
                    set_Month = choice
                elif key == 'Hour':
                    set_Hour = choice
                elif key == 'Minute':
                    set_Minute = choice
                elif key == 'AM_PM':
                    set_AMPM = choice
                elif key == 'Day':
                    set_Day = choice
                    print('Date is set:', set_AMPM, set_Minute, set_Hour, set_Month, set_Day, set_Year)
                    lcd.clear()
                    lcd.putstr('Date set:\n' + str(set_Hour) + ":" + str(set_Minute) + set_AMPM + str(set_Month) +
                               str(set_Day) + str(set_Year))
                    start_date_tuple = (set_Year, set_Month, set_Day, 0, set_Hour, set_Minute, 0, 0)
                    rtc.datetime(start_date_tuple)
                break

    default_screen()

#SECTION 6 END


#SECTION 7 BEGIN: function to allow the user to create a custom label that is saved in flash memory

def customLabel():
    global recentLabels_list
    global selection
    global printer
    global lcd
    global inuse_date
    global rtc
    charac_counter = 0
    line1 = ''
    line2 = ''

    while True:
        print('Scroll to Select Characters for Line 1:', charac_list[charac_counter])
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr('Scroll to select')
        lcd.move_to(0, 1)
        lcd.putstr('Line 1:' + charac_list[charac_counter])
        selection = rotary_change()
        if selection == 'a':
            if charac_counter == 0:
                charac_counter = len(charac_list) - 1
            else:
                charac_counter -= 1
        elif selection == 'b':
            if charac_counter == len(charac_list) - 1:
                charac_counter = 0
            else:
                charac_counter += 1
        elif selection == 'c':
            choice = charac_list[charac_counter]

            if choice == 'BACK':
                line1 = line1[:-1]
                print(line1)
                lcd.clear()
                lcd.putstr('Charac Deleted!\n' + line1)
                time.sleep(1)
            elif choice == '*TODAY' or choice == '*TOMORROW' or choice == '*NOW':
                line1 = choice
                print('Line 1 Complete:', line1)
                lcd.clear()
                lcd.putstr('Line 1 Complete\n' + line1)
                charac_counter = 0
                break
            elif choice == 'DONE':
                print('Line 1 Complete:', line1)
                lcd.clear()
                lcd.putstr('Line 1 Complete\n' + line1)
                charac_counter = 0
                break
            else:
                line1 = line1 + choice
                print('Line 1:', line1)
                print(choice, 'selected!')
                lcd.clear()
                lcd.putstr(choice + ' selected!\n' + line1)
                time.sleep(1)
            #charac_counter = 0

    while True:
        print('Scroll to Select Characters for Line 2:', charac_list[charac_counter])
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr('Scroll to select')
        lcd.move_to(0, 1)
        lcd.putstr('Line 2:' + charac_list[charac_counter])
        selection = rotary_change()
        if selection == 'a':
            if charac_counter == 0:
                charac_counter = len(charac_list) - 1
            else:
                charac_counter -= 1
        elif selection == 'b':
            if charac_counter == len(charac_list) - 1:
                charac_counter = 0
            else:
                charac_counter += 1
        elif selection == 'c':
            choice = charac_list[charac_counter]
            print(choice, 'selected!')
            lcd.clear()
            lcd.putstr(choice + ' selected!')
            if choice == 'BACK':
                line2 = line2[:-1]
                print(line2)
                lcd.clear()
                lcd.putstr('Charac Deleted!\n' + line2)
                time.sleep(1)
            elif choice == '*TODAY' or choice == '*TOMORROW' or choice == '*NOW':
                line2 = choice
                print('Line 2 Complete:', line2)
                lcd.clear()
                lcd.putstr('Line 2 Complete\n' + line2)
                charac_counter = 0
                break
            elif choice == 'DONE':
                print('Line 2 Complete:', line2)
                lcd.clear()
                lcd.putstr('Line 2 Complete\n' + line2)
                charac_counter = 0
                break
            else:
                line2 = line2 + choice
                print('Line 2:', line2)
                lcd.clear()
                lcd.putstr(choice + ' selected!\n' + line2)
                time.sleep(1)
            #charac_counter = 0

    temp_list = [line1, line2]
    print('line 475 - printing temp_list..')
    print(temp_list)
    lcd.clear()
    lcd.putstr('Printing Label..')
    printer.feed(1)
    if line1 == '*TODAY':
        printer.print('Today: ' + inuse_date)
    elif line1 == '*TOMORROW':
        tomorrow = use_days_compute(1)
        printer.print('Tomor: ' + tomorrow)
    elif line1 == '*NOW':
        now = rtc.datetime()
        nowyear = str(now[0])
        nowmonth = str(now[1])
        nowday = str(now[2])
        if len(str(now[4])) == 1:
            nowhr = '0' + str(now[4])
        else:
            nowhr = str(now[4])
        if len(str(now[5])) == 1:
            nowmin = '0' + str(now[5])
        else:
            nowmin = str(now[5])
        nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
        printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
        printer.print('Now: ' + nowts)
        printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
    else:
        printer.print(line1)
    printer.feed(2)
    if line2 == '*TODAY':
        printer.print('Today: ' + inuse_date)
    elif line2 == '*TOMORROW':
        tomorrow = use_days_compute(1)
        printer.print('Tomor: ' + tomorrow)
    elif line2 == '*NOW':
        now = rtc.datetime()
        nowyear = str(now[0])
        nowmonth = str(now[1])
        nowday = str(now[2])
        if len(str(now[4])) == 1:
            nowhr = '0' + str(now[4])
        else:
            nowhr = str(now[4])
        if len(str(now[5])) == 1:
            nowmin = '0' + str(now[5])
        else:
            nowmin = str(now[5])
        nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
        printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
        printer.print('Now: ' + nowts)
        printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
    else:
        printer.print(line2)
    printer.feed(1)
    # Feed lines to make visible:
    printer.feed(4)
    printer.write(b'\x1D\x56\x01')
    printer.feed(1)
    recentLabels_list.insert(0, temp_list)
    # if len(recentLabels_list) == 0:
    #     recentLabels_list = temp_list
    # else:
    #     recentLabels_list.insert(0, temp_list)

    # with open("recent_labels.txt", 'w') as recent_labels_file:
    #     recent_labels_file.write(str(recentLabels_list))

    recent_labels_file = open("recent_labels.txt", 'w')
    recent_labels_file.write(str(recentLabels_list))
    recent_labels_file.close()

    selection = ''
    default_screen()

#SECTION 7 END


#SECTION 8 BEGIN: define function to allow user to select and print recently used labels from flash memory

def recentLabels():
    global selection
    global recentLabels_list
    global printer
    global lcd
    global inuse_date
    recentLabels_counter = 0

    try:
        print('Scroll to Select Recent Label:', recentLabels_list[recentLabels_counter])
        lcd.clear()
        lcd.putstr('Scroll to Select\nRecent Labels..')
        time.sleep(2)
    except:
        lcd.clear()
        lcd.putstr('No Recent Labels')
        time.sleep(2)
        return

    while True:
        line1_str = recentLabels_list[recentLabels_counter][0]
        line2_str = recentLabels_list[recentLabels_counter][1]
        lcd.clear()
        lcd.putstr(line1_str + '\n' + line2_str)
        selection = rotary_change()

        if selection == 'a':
            if recentLabels_counter == 0:
                recentLabels_counter = len(recentLabels_list) - 1
            else:
                recentLabels_counter -= 1
        elif selection == 'b':
            if recentLabels_counter == len(recentLabels_list) - 1:
                recentLabels_counter = 0
            else:
                recentLabels_counter += 1
        elif selection == 'c':
            choice = recentLabels_list[recentLabels_counter]
            print(choice, 'selected!')
            lcd.clear()
            lcd.putstr('Printing Label..')
            if line1_str == '*TODAY':
                printer.print('Today: ' + inuse_date)
            elif line1_str == '*TOMORROW':
                tomorrow = use_days_compute(1)
                printer.print('Tomor: ' + tomorrow)
            elif line1_str == '*NOW':
                now = rtc.datetime()
                nowyear = str(now[0])
                nowmonth = str(now[1])
                nowday = str(now[2])
                if len(str(now[4])) == 1:
                    nowhr = '0' + str(now[4])
                else:
                    nowhr = str(now[4])
                if len(str(now[5])) == 1:
                    nowmin = '0' + str(now[5])
                else:
                    nowmin = str(now[5])
                nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
                printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
                printer.print('Now: ' + nowts)
                printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
            else:
                printer.print(line1_str)
            printer.feed(2)
            if line2_str == '*TODAY':
                printer.print('Today: ' + inuse_date)
            elif line2_str == '*TOMORROW':
                tomorrow = use_days_compute(1)
                printer.print('Tomor: ' + tomorrow)
            elif line2_str == '*NOW':
                now = rtc.datetime()
                nowyear = str(now[0])
                nowmonth = str(now[1])
                nowday = str(now[2])
                if len(str(now[4])) == 1:
                    nowhr = '0' + str(now[4])
                else:
                    nowhr = str(now[4])
                if len(str(now[5])) == 1:
                    nowmin = '0' + str(now[5])
                else:
                    nowmin = str(now[5])
                nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
                printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
                printer.print('Now: ' + nowts)
                printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
            else:
                printer.print(line2_str)
            printer.feed(4)
            printer.write(b'\x1D\x56\x01')
            printer.feed(1)
            # the below line brings the selected item to the front of the list for next use
            recentLabels_list.insert(0, recentLabels_list.pop(recentLabels_counter))

            # with open("recent_labels.txt", 'w') as recent_labels_file:
            #     recent_labels_file.write(str(recentLabels_list))
            recent_labels_file=open("recent_labels.txt", 'w')
            recent_labels_file.write(str(recentLabels_list))
            recent_labels_file.close()

            break

    selection = ''
    default_screen()

#SECTION 8 END


#SECTION 9 BEGIN: define function to convert inuse date to string format

def inuse_date_compute():
    global rtc
    thepresent = rtc.datetime()

    if len(str(thepresent[1]))==1:
        month = '0'+ str(thepresent[1])
    else:
        month = str(thepresent[1])
    if len(str(thepresent[2]))==1:
        day = '0'+ str(thepresent[2])
    else:
        day = str(thepresent[2])

    inuse_date = month + '/' + day + '/' + str(thepresent[0])[2:]
    return inuse_date

#SECTION 9 END


#SECTION 10 BEGIN: define function to compute expiry date and then convert to string format

def use_days_compute(user_days):
    global rtc
    thepresent = rtc.datetime()
    future_date = utime.mktime((thepresent[0], thepresent[1], thepresent[2] + user_days, thepresent[3], thepresent[4],
                                thepresent[5], thepresent[6], thepresent[7]))
    future_date1 = utime.localtime(future_date)

    if len(str(future_date1[1]))==1:
        month = '0'+ str(future_date1[1])
    else:
        month = str(future_date1[1])
    if len(str(future_date1[2]))==1:
        day = '0'+ str(future_date1[2])
    else:
        day = str(future_date1[2])

    useby_date = month + '/' + day + '/' + str(future_date1[0])[2:]
    return useby_date

#SECTION 10 END


#SECTION 11 BEGIN: define function to detect and report changes in rotary encoder

def rotary_change():
    global lastval
    global selection
    global val
    global r
    global button_press
    lastval = r.value()

    while True:
        val = r.value()
        if lastval != val:
            if lastval > val:
                selection = 'a'
            else:
                selection = 'b'
            lastval = val
            print('result =', val)
            break
        elif button_press.value() == 0:
            selection = 'c'
            time.sleep(1)
            break
        time.sleep_ms(50)

    return selection

#SECTION 11 END


# SECTION 12 BEGIN: create function for returning to default screen

def default_screen():
    global inuse_date
    global useby_date
    global lcd

    print('displaying in use and use by now!')
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('In Use: '+inuse_date)
    lcd.move_to(0, 1)
    lcd.putstr('Use By: '+useby_date)
    #### test code ####
    time.sleep(2)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Recent    In Use')
    lcd.move_to(0, 1)
    lcd.putstr('Label     Use By')
    #### test code end ####
# SECTION 12 END


#SECTION 13 BEGIN: set an initial inuse date (will change with each day that passes)

# require user to select time zone
def time_zone_selection():
    global timezone_dict
    global timezone_list
    global timezone_counter
    global time_zone
    global time_zone_value
    global selection
    global lcd

    print('Beginning time zone selection now!')
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Scroll to Select')
    lcd.move_to(0, 1)
    lcd.putstr('Time Zone: ' + timezone_list[timezone_counter])

    selection = rotary_change()

    if selection == 'a':
        if timezone_counter == 0:
            timezone_counter = len(timezone_list) - 1
        else:
            timezone_counter -= 1
        time_zone_selection()
    elif selection == 'b':
        if timezone_counter == len(timezone_list) - 1:
            timezone_counter = 0
        else:
            timezone_counter += 1
        time_zone_selection()
    elif selection == 'c':
        choice = timezone_list[timezone_counter]
        print(choice, 'selected!')
        time_zone = choice
        with open("timezone.txt", 'w') as timezone_name_file:
            timezone_name_file.write(choice)
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(str(choice) + ' selected!')
        time_zone_value = timezone_dict[time_zone]
        timezone_counter = 0
        selection = ''
        print('time zone is:',time_zone)
        print('time zone value is:',time_zone_value)


# set an initial user days value (user can change)
user_days = 6
inuse_date = inuse_date_compute()

# set an initial expiry date (will change with each day that passes and if user changes user_days)
useby_date = use_days_compute(user_days)

#SECTION 13 END


# SECTION 14 BEGIN: define main loop that monitors for beam breaks or rotary encoder movement and controls subsequent
# actions.

def main_loop():
    global printer
    global inuse_date
    global useby_date
    global user_days
    global button_press
    global lcd
    global break_beam_1
    global break_beam_2
    global lastval
    global r
    global val
    global recentLabels_list
    global rtc
    global led_np
    lastval = r.value()

    default_screen()

    while True:
        val = r.value()
        old_inuse_date = inuse_date
        inuse_date = inuse_date_compute()
        if inuse_date != old_inuse_date:
            useby_date = use_days_compute(user_days)
            default_screen()
        useby_date = use_days_compute(user_days)
        if break_beam_1.value() == 0:
            # Break beam input is at a low logic level, i.e. broken!
            print('Beam 1 is broken')
            led_cycle(0, 255, 255, 50)
            led_set_color(0,255,255)
            lcd.clear()
            lcd.putstr('Printing Label..')
            printer.print('In Use: ' + inuse_date, '\n')
            printer.feed(1)
            printer.print('Use by: ', useby_date)
            printer.feed(4)
            printer.write(b'\x1D\x56\x01')
            printer.feed(1) #new line - replaces feed before print
            time.sleep(1)
            led_set_color(0,0,0)
            default_screen()
        elif break_beam_2.value() == 0:
            try:
                line1_str = recentLabels_list[0][0]
                line2_str = recentLabels_list[0][1]
                print('Printing Recent..')
                print(recentLabels_list)
                led_cycle(0, 255, 0, 50)
                led_set_color(0, 255, 0)
                lcd.clear()
                lcd.putstr('Printing Recent')

                if line1_str == '*TODAY':
                    printer.print('Today: ' + inuse_date)
                elif line1_str == '*TOMORROW':
                    tomorrow = use_days_compute(1)
                    printer.print('Tomor: ' + tomorrow)
                elif line1_str == '*NOW':
                    now = rtc.datetime()
                    nowyear = str(now[0])
                    nowmonth = str(now[1])
                    nowday = str(now[2])
                    if len(str(now[4])) == 1:
                        nowhr = '0' + str(now[4])
                    else:
                        nowhr = str(now[4])
                    if len(str(now[5])) == 1:
                        nowmin = '0' + str(now[5])
                    else:
                        nowmin = str(now[5])
                    nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
                    printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
                    printer.print('Now: ' + nowts)
                    printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
                else:
                    printer.print(line1_str)
                printer.feed(2)
                if line2_str == '*TODAY':
                    printer.print('Today: ' + inuse_date)
                elif line2_str == '*TOMORROW':
                    tomorrow = use_days_compute(1)
                    printer.print('Tomor: ' + tomorrow)
                elif line2_str == '*NOW':
                    now = rtc.datetime()
                    nowyear = str(now[0])
                    nowmonth = str(now[1])
                    nowday = str(now[2])
                    if len(str(now[4])) == 1:
                        nowhr = '0' + str(now[4])
                    else:
                        nowhr = str(now[4])
                    if len(str(now[5])) == 1:
                        nowmin = '0' + str(now[5])
                    else:
                        nowmin = str(now[5])
                    nowts = nowmonth + '/' + nowday + '/' + nowyear + ' ' + nowhr + ':' + nowmin
                    printer.setSize('M')  # options are 'L' for large, 'M' for medium font or any other value for small
                    printer.print('Now: ' + nowts)
                    printer.setSize('L')  # options are 'L' for large, 'M' for medium font or any other value for small
                else:
                    printer.print(line2_str)
                printer.feed(4)
                printer.write(b'\x1D\x56\x01')
                printer.feed(1)
                time.sleep(1)
                led_set_color(0, 0, 0)
                default_screen()
            except:
                lcd.clear()
                lcd.putstr('No Recent Labels')
                time.sleep(1)
                default_screen()
        elif lastval != val:
            lastval = val
            mainMenu()
        elif button_press.value() == 0:
            time.sleep(1)
            mainMenu()
        # Delay for 0.050 and repeat again.
        time.sleep_ms(50)

#END SECTION 14


# SECTION 15 BEGIN: check to see if settings files exist to recall settings from prior device state

def check_settings():
    global ssid_name
    global ssid_pwrd
    global timezone_dict
    global timezone_list
    global timezone_counter
    global time_zone
    global time_zone_value
    global user_days
    global recentLabels_list

    if 'user_days.txt' in os.listdir():
        user_days_file = open('user_days.txt', 'r')
        user_days = int(user_days_file.read())
        user_days_file.close()

    if 'recent_labels.txt' in os.listdir():
        recent_labels_file = open('recent_labels.txt', 'r')
        recentLabels_list_pre = recent_labels_file.read()
        recentLabels_list = eval(recentLabels_list_pre)
        recent_labels_file.close()

    if 'timezone.txt' in os.listdir():
        timezone_file = open('timezone.txt', 'r')
        time_zone = timezone_file.read()
        timezone_file.close()
        time_zone_value = timezone_dict[time_zone]

        if 'ssid.txt' in os.listdir():
            ssid_file = open('ssid.txt', 'r')
            ssid_name = ssid_file.read()
            ssid_file.close()

            if 'ssid_pwrd.txt' in os.listdir():
                ssid_pwrd_file = open('ssid_pwrd.txt', 'r')
                ssid_pwrd = ssid_pwrd_file.read()
                ssid_pwrd_file.close()

                connectWifi()
    else:
        time_zone_selection()


#END SECTION 15


# SECTION 16 BEGIN: connect to wifi upon boot if wifi settings are available

def connectWifi():
    global ssid_name
    global ssid_pwrd
    global lcd
    global time_zone_value

    nic = network.WLAN(network.STA_IF)
    nic.active(True)

    lcd.clear()
    lcd.putstr('Connecting to\nwifi...')
    nic.connect(ssid_name, str(ssid_pwrd))
    # time.sleep(2)
    for x in range(1, 10):
        print('sleep cycle1', x)
        print(nic.isconnected())
        time.sleep(1)
    if nic.isconnected() == True:
        lcd.clear()
        lcd.putstr('Wifi Connected\nSuccessfully')
        time.sleep(2)
        settime()
        for y in range(1, 5):
            print('sleep cycle1', y)
            time.sleep(1)
        print(utime.localtime())
        live_date_tuple = utime.localtime()

        live_date = (live_date_tuple[0], live_date_tuple[1], live_date_tuple[2], live_date_tuple[6],
                     live_date_tuple[3] + time_zone_value, live_date_tuple[4], live_date_tuple[5], 0)
        rtc.datetime(live_date)
        print(rtc.datetime())
        #ota_update()
    else:
        lcd.clear()
        lcd.putstr('Wifi Failed to\nConnect!')
        time.sleep(2)
        nic.active(False)
        print(utime.localtime())


# SECTION 16 END


# SECTION 17 BEGIN: To reset to factory settings (remove all items held in memory including timezone, wifi ssid,
# wifi password and custom labels
def factory_reset():
    global yesno_list
    global yesno_counter
    global selection

    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Delete Settings?')
    lcd.move_to(0, 1)
    lcd.putstr(yesno_list[yesno_counter])

    selection = rotary_change()

    if selection == 'a':
        if yesno_counter == 0:
            yesno_counter = len(yesno_list) - 1
        else:
            yesno_counter -= 1
        factory_reset()
    elif selection == 'b':
        if yesno_counter == len(yesno_list) - 1:
            yesno_counter = 0
        else:
            yesno_counter += 1
        factory_reset()
    elif selection == 'c':
        choice = yesno_list[yesno_counter]
        print(choice, 'selected!')

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(str(choice) + ' selected!')
        time.sleep(2)

        if choice == 'YES':

            #### code to delete all settings files...#####
            if 'user_days.txt' in os.listdir():
                os.remove('user_days.txt')
            if 'ssid.txt' in os.listdir():
                os.remove('ssid.txt')
            if 'ssid_pwrd.txt' in os.listdir():
                os.remove('ssid_pwrd.txt')
            if 'timezone.txt' in os.listdir():
                os.remove('timezone.txt')
            if 'recent_labels.txt' in os.listdir():
                os.remove('recent_labels.txt')

            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr('Settings Deleted')
            time.sleep(2)
            lcd.putstr('Rebooting..')
            time.sleep(2)
            selection = ''
            machine.reset()
        else:
            pass
        mainMenu()

# SECTION 17 END


# SECTION 18 BEGIN: To provide functions for driving LED lights in swipe channel
def led_clear():
  global led_qty
  global led_np

  for i in range(led_qty):
    led_np[i] = (0, 0, 0)
    led_np.write()

def led_set_color(r, g, b):
  global led_qty
  global led_np

  for i in range(led_qty):
      led_np[i] = (r, g, b)
  led_np.write()

def led_cycle(r, g, b, wait):
  global led_qty
  global led_np
  led_sequence = [1, 2, 3, 4, 9, 8, 7, 6, 5]

  for i in led_sequence:
    for j in range(led_qty):
      led_np[j] = (0, 0, 0)
    led_np[i-1] = (r, g, b)
    led_np.write()
    time.sleep_ms(wait)

  for i in range(led_qty):
    led_np[i] = (r, g, b)
  led_np.write()
  time.sleep_ms(200)

  for i in range(led_qty):
    led_np[i] = (0, 0, 0)
    led_np.write()

# SECTION 18 END

# SECTION 19 BEGIN: To administer OTA updates for firmware. If newer version exists on Github, it will be downloaded
# and will replace the current version (main.py). This has been commented out as it was moved to boot.py.
# def ota_update():
#     gc.collect()
#     gc.enable()
#
#     OTA = senko.Senko(user="edblagg", repo="label-smart", working_dir="main", files=["main.py"])
#
#     if OTA.update():
#         print("Updated to the latest version! Rebooting...")
#         lcd.clear()
#         lcd.move_to(0, 0)
#         lcd.putstr('Firmware is\nUpdating!')
#         time.sleep(2)
#         lcd.putstr('Rebooting..')
#         time.sleep(2)
#         machine.reset()
#     else:
#         print("No update needed")

# SECTION 19 END

check_settings()
main_loop()
