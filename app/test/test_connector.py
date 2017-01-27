import unittest
import app.interpreter, app.database, app.connector
import os
import time

__author__ = 'Goyder'

# Depending on the platform that this is being used on, the default connection name may change.

if os.path.exists('/dev/tty.wchusbserial1410'):
    connection_name = "/dev/tty.wchusbserial1410"
elif os.path.exists('/dev/tty.wchusbserial1420'):
    connection_name = "/dev/tty.wchusbserial1420"
else:
    connection_name = None

class IntegrationTestSerialConnector(unittest.TestCase):
    """
    Tests to check that the USB connection functions effectively.
    """

    def test_can_retrieve_values_from_connection(self):
        """
        Can the connector object:
        1. Connect to a USB connection?
        2. Listen for, at most, 5 seconds?
        3. Retrieve values?
        :return:
        """

        if connection_name is None:
            self.skipTest("Test is being skipped - no connection is available to test.")

        connector = app.connector.SerialConnector(connection_name, time_out=1.0)
        connector.connect()

        retrieved_data = []

        i = 0
        while i < 5:
            i += 1
            try:
                retrieved_data += [connector.retrieve_data()]
            except TypeError:
                pass

        print(retrieved_data)
        connector.close_connection()

        self.assertEqual(
            True,
            retrieved_data != [],
            """Connection failed to retrieve any data from forming connection.
            (Is the Arduino in debug mode?)"""
        )

    def test_can_open_check_and_close_connection(self):
        """
        Tests to ensure that we can open, check, and close a connection.
        :return:
        """

        if connection_name is None:
            self.skipTest("Test is being skipped - no connection is available to test.")

        connector = app.connector.SerialConnector(connection_name, time_out=1.0)

        self.assertEqual(
            True,
            connector.is_connected() == False,
            "Connector indicated that it was connected before a connection had been formed."
        )

        connector.connect()

        self.assertEqual(
            True,
            connector.is_connected() == True,
            "Connector indicated it was not connected even though connection had been formed."
        )

        print("Message: {0}".format(connector.retrieve_data()))
        print("Message: {0}".format(connector.retrieve_data()))
        print("Message: {0}".format(connector.retrieve_data()))

        connector.close_connection()

        self.assertEqual(
            True,
            connector.is_connected() == False,
            "Connector did not indicated it was closed even though it had been closed."
        )

    def test_system_recognises_a_disconnection(self):
        """
        If we physically disconnect the connection, it should return a false.
        :return:
        """

        if connection_name is None:
            self.skipTest("Test is being skipped - no connection is available to test.")

        connector = app.connector.SerialConnector(connection_name, time_out=1.0)
        connector.connect()

        self.assertEqual(
            True,
            connector.is_connected() == True,
            "Connector indicated that it was not connected even though connection had been formed."
        )

        print("Disconnect the USB.")
        time.sleep(5)

        self.assertEqual(
            True,
            connector.is_connected() == False,
            "Connector indicated it was  connected even though device had been removed."
        )

        print("Reconnect the USB.")
        time.sleep(5)

        connector.connect()

        self.assertEqual(
            True,
            connector.is_connected() == True,
            "Connector indicated that it was not connected even though connection had been formed."
        )




