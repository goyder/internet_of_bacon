import unittest
import sqlite3
import app.interpreter, app.database, app.connector
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

        # Retrieve the values and validate them.
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
