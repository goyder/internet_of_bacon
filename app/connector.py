import serial
import os

"""
connector.py
Class to retrieve information from external connections.
"""

__author__ = 'Goyder'

class Connector(object):
    """
    Root class to define the connector class.
    """

    def connect(self):
        """
        Connect to an external object.
        :return:
        """
        raise NotImplementedError("Function must be created in a sub-class.")

    def retrieve_data(self):
        """
        Retrieve data from the external object.
        :return:
        """
        raise NotImplementedError("Function must be created in a sub-class.")

    def is_connected(self):
        """
        Check if current object's connection is valid.
        """
        raise NotImplementedError("Function must be created in a sub-class.")

    def write_data(self, message):
        """
        Write data back to the connection.
        """
        raise NotImplementedError("Function must be created in a sub-class.")

    def close_connection(self):
        """
        Close the open connection.
        """
        raise NotImplementedError("Function must be created in a sub-class.")


class SerialConnector(Connector):
    """
    Connector implemented for a Serial connection, specifically _not_ a Bluetooth unit.
    """

    def __init__(self, serial_name, time_out=1.0):
        self.serial_connection = None
        self.serial_name = serial_name
        self.time_out = time_out

    def connect(self):
        """
        Connect to a specified serial connection.
        :return:
        """
        self.serial_connection = serial.Serial(self.serial_name, timeout=self.time_out)
        self.serial_connection.flushInput()

    def retrieve_data(self):
        """
        Retrieve messages from the connection.
        :return: Strings.
        """
        return self.serial_connection.readline().decode(errors="ignore")

    def is_connected(self):
        """
        Return if the connection is open.
        :return:
        """
        # If the device has come undone, attempts to read from it return a TypeError.
        if self.serial_connection is None:
            return False

        # If the device has come undone, attempts to read from it return a OSError.
        try:
            self.serial_connection.inWaiting()
        except (TypeError,OSError):
            self.close_connection()
            return False

        return self.serial_connection.isOpen()

    def close_connection(self):
        """
        Close the connection if open.
        :return:
        """
        try:
            self.serial_connection.close()
        except:
            pass

    def write_data(self, message):
        """
        Push the data back to the serial object.
        Note that the object distinguishes messages via a newline character.
        :param message:
        :return:
        """
        message = message + "\n"
        message = message.encode("ASCII")
        self.serial_connection.write(message)


class BluetoothConnector(Connector):
    """
    Sub-class for a Bluetooth connector.
    """
