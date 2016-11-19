import random
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
    raise NotImplementedError


def get_readings(debug=False):
    """
    Check the interface and return a single line of the system.
    Perhaps filter out blank lines, but nothing more.
    Leave the validation to the database side of things.
    Includes support for a Bluetooth free, debug mode.
    :return: Tuple of strings, each containing an individual line.
    """
    if debug:
        if random.random() < 0.8:
            tag_names = ["sensor_1", "sensor_2", "sensor_3"]
            item = random.choice(tag_names)
            return "{0},{1}".format(item, random.randrange(0,100))
        else:
            return "GARBAGE MESSAGE!"

    raise NotImplementedError

