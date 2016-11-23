import random
import sys
__author__ = 'Goyder'

"""
bt_interface.py
Module to handle the bluetooth connections between the app and relevant devices.

    QUESTIONS AT THIS POINT:
        - How obscured should this interface be? This may have to work on mac or linux.
        - What should this interface return?
        - How should this interface _function_?
"""


def connect():
    """
    Main connection point to establish a Bluetooth connection.

    :return: True if connected successfully. False otherwise.
    """
    if sys.platform == "linux2":
        import bluetooth
        conn = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        conn.connect(('98:D3:31:FC:20:34',1))  # TODO: Adjust this to be handled by config file
        conn.settimeout(0.1)  # Very short - means that when a message is finished, the system times out.
        conn = conn.makefile()
        return conn
    else:
        raise NotImplementedError


def get_readings(connection, debug=False):
    """
    Check the interface and return a single line of the system.
    Perhaps filter out blank lines, but nothing more.
    Leave the validation to the database side of things.
    Includes support for a Bluetooth free, debug mode.
    :return: Tuple of strings, each containing an individual line.
    """
    if debug:
        readings = []
        for i in range(random.choice((1,2,3))):
            if random.random() < 0.8:
                tag_names = ["sensor_1", "sensor_2", "sensor_3"]
                item = random.choice(tag_names)
                readings.append( "{0},{1}".format(item, random.randrange(0,100)))
            else:
                readings.append( "GARBAGE MESSAGE!")
            return readings

    if sys.platform == "linux2":
        readings = []
        while True:
            try:
                readings.append(connection.readline())
            except bluetooth.BluetoothError as bterror:
                if bterror.args[0] == "timed out":  # No more messages forthcoming at this time.
                    return readings

    raise NotImplementedError

