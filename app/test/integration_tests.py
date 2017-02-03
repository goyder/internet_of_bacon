import unittest
import sqlite3
import app.interpreter, app.database, app.connector, app.monitor
import app.test.test_monitor
import app.test
import os

"""
integration_tests.py
Can we get our modules to play nicely together?
"""

__author__ = 'Goyder'

if os.path.exists('/dev/tty.wchusbserial1410'):
    connection_name = "/dev/tty.wchusbserial1410"
elif os.path.exists('/dev/tty.wchusbserial1420'):
    connection_name = "/dev/tty.wchusbserial1420"
else:
    connection_name = None

class IntegrateDatabaseAndInterpreter(unittest.TestCase):
    """
    Tests to ensure that the interpreter and database classes can work together.
    """

    def test_interpreter_and_database_end_to_end(self):
        """
        Build the database and interpreter, pass in a value, and check whether what we get out the end is right.
        :return:
        """
        database_filename = "test.db"

        # Build our components and feed them through.
        database = app.database.Database(database_filename, overwrite=True)
        database.create_database()
        interpreter = app.interpreter.Interpreter(database=database)
        interpreter.interpret(app.test.DATA_MESSAGE)

        # Retrieve the values and validate them
        with sqlite3.connect(database_filename) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchone()

        self.assertEqual(
            True,
            output_data == app.test.DATA_MESSAGE_OUT_OF_DATABASE,
            "Retrieve data from database did not match expected output."
        )


class IntegrateInterpreterAndConnector(unittest.TestCase):
    """
    Tests to ensure the interpreter and connector can work together.
    """

    def test_interpreter_and_connector(self):
        """
        Check that the interpreter can respond to messages from the connector.
        :return:
        """
        if connection_name is None:
            self.skipTest("No connection available. Skipping test.")

        database_filename = "test.db"

        # Build our components and feed them through.
        database = app.database.Database(database_filename, overwrite=True)
        database.create_database()

        interpreter = app.interpreter.Interpreter(database=database)

        connector = app.connector.SerialConnector(connection_name)
        connector.connect()

        interpreter_input = []
        interpreter_output = []

        i = 0
        for i in range(5):
            interpreter_input += [connector.retrieve_data()]
            print("Input: {0}".format(interpreter_input[-1]))
            try:
                interpreter_output += [interpreter.interpret(interpreter_input[-1])]
                print("Output: {0}".format(interpreter_output[-1]))
            except ValueError as e:
                if "ERROR 001" in e.args[0]:
                    pass
                else:
                    raise ValueError

    def test_interpreter_and_connector_full_response(self):
        """
        Check that the interpreter can respond to messages from the connector,
        and write them back.
        :return:
        """
        if connection_name is None:
            self.skipTest("No connection available. Skipping test.")

        database_filename = "test.db"

        # Build our components and feed them through.
        database = app.database.Database(database_filename, overwrite=True)
        database.create_database()

        interpreter = app.interpreter.Interpreter(database=database)

        connector = app.connector.SerialConnector(connection_name)
        connector.connect()

        interpreter_input = []
        interpreter_output = []

        for i in range(25):
            interpreter_input += [connector.retrieve_data()]
            print("Input: {0}".format(interpreter_input[-1]))
            try:
                interpreter_output += [interpreter.interpret(interpreter_input[-1])]
                print("Output: {0}".format(interpreter_output[-1]))
                if interpreter_output[-1] is not None:
                    connector.write_data(interpreter_output[-1])
            except ValueError as e:
                if "ERROR 001" in e.args[0]:
                    pass
                else:
                    raise ValueError

        with sqlite3.connect(database_filename) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchone()
            print(output_data)


class TestMonitorAndSerialConnectorCreation(unittest.TestCase):
    """
    Can we build and make a monitor function correctly?
    """

    def test_create_monitor_and_serial_connection(self):
        """
        :return:
        """
        if connection_name is None:
            self.skipTest("No connection available. Skipping test.")

        parameters = app.test.test_monitor.generate_input_parameter_object_minus_inputs()
        parameters["connection_list"] = [connection_name]
        parameters["overwrite"] = True
        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()

        with sqlite3.connect(parameters['database_location']) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchall()
            print("Data in database: {0}".format(output_data))

        self.assertEqual(
            True,
            len(output_data) == 0,
            "Output data was retrieved from database, despite a fresh, overwrite connection being set up."
        )

    def test_create_monitor_and_serial_connection_and_data_writing(self):
        if connection_name is None:
            self.skipTest("No connection available. Skipping test.")

        parameters = app.test.test_monitor.generate_input_parameter_object_minus_inputs()
        parameters["connection_list"] = [connection_name]
        parameters["overwrite"] = True
        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()
        monitor.run(runs=5)

        with sqlite3.connect(parameters['database_location']) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchall()
            print("Data in database: {0}".format(output_data))

        self.assertEqual(
            True,
            len(output_data) > 0,
            "No data was written to the database. Check that board is in debug mode."
        )


class MonitorIntegrationTests(unittest.TestCase):
    """
    Test that the system runs end to end.
    """

    def test_monitor_end_to_end_with_config(self):
        parameters = app.monitor.read_config_yaml("config.yaml")

        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()
        monitor.run(50)

        with sqlite3.connect(parameters['database_location']) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchall()
            print("Data in database: ")
            for line in output_data:
                print(line)

        # Have we filled up the database with something?
        self.assertEqual(
            True,
            len(output_data) > 0,
            "No data was written to the database. Check that board is in debug mode."
        )

    def test_monitor_end_to_end(self):
        parameters = app.test.test_monitor.generate_input_parameter_object_minus_inputs()
        parameters['overwrite'] = True

        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()
        monitor.run(50)

        with sqlite3.connect(parameters['database_location']) as conn:
            cur = conn.cursor()
            cur = cur.execute("SELECT * FROM data;")
            output_data = cur.fetchall()
            print("Data in database: ")
            for line in output_data:
                print(line)

        # Have we filled up the database with something?
        self.assertEqual(
            True,
            len(output_data) > 0,
            "No data was written to the database. Check that board is in debug mode."
        )
