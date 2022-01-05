# This file is executed on every boot (including wake-boot from deepsleep)

# SECTION 1 BEGIN: To administer OTA updates for firmware. If newer version exists on Github, it will be downloaded
# and will replace the current version (main.py).
import gc
import senko
import os
import machine
import network

# define function definitions for lcd screen control
DEFAULT_I2C_ADDR = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

ssid = ''
pwrd = ''


def get_wifi():
    global ssid
    global pwrd

    if 'ssid.txt' in os.listdir():
        ssid_file = open('ssid.txt', 'r')
        ssid = ssid_file.read()
        ssid_file.close()

        if 'ssid_pwrd.txt' in os.listdir():
            ssid_pwrd_file = open('ssid_pwrd.txt', 'r')
            pwrd = ssid_pwrd_file.read()
            ssid_pwrd_file.close()

            connect_wlan()


def connect_wlan():
    global ssid
    global pwrd
    """Connects build-in WLAN interface to the network.
    Args:
        ssid: Service name of Wi-Fi network.
        password: Password for that Wi-Fi network.
    Returns:
        True for success, Exception otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.active(True)
        sta_if.connect(ssid, pwrd)
        while not sta_if.isconnected():
            pass
    if sta_if.isconnected() == True:
        ota_update()
    return True


def ota_update():

    global lcd
    
    OTA = senko.Senko(user="edblagg", repo="label-smart", working_dir="main", files=["main.py"])

    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr('Firmware is\nUpdating!')
        time.sleep(2)
        lcd.putstr('Rebooting..')
        time.sleep(2)
        machine.reset()
    else:
        print("No update needed")
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr('Firmware is\nup to date!')
        time.sleep(2)

def main():

    global ssid
    global pwrd

    gc.collect()
    gc.enable()

    get_wifi()




# SECTION 1 END

if __name__ == "__main__":
    main()