import app.interpreter, app.connector, app.database
import logging
import os
import yaml

"""
monitor.py
Main entry point for the temperature/humidity monitor.
"""

logger = logging.getLogger("logger")

__author__ = 'Goyder'

class Monitor(object):
    """
    Main object to tie together our various objects.
    """

    def __init__(self, input_parameters):
        """
        Specify creation parameters here.
        :param input_parameters: Dictionary of input parameters required for the monitor.
        :return:
        """
        # If anything is not valid, an error should be raised here.
        self.valid_inputs = input_parameters_are_valid(input_parameters)

        # Set parameters
        self.database_location  = input_parameters['database_location']
        self.overwrite          = input_parameters['overwrite']
        self.connection_list    = input_parameters['connection_list']
        self.timeout            = input_parameters['timeout']
        self.connection_type    = input_parameters['connection_type']

        # Define our components
        self.database       = None
        self.interpreter    = None
        self.connector      = None
        self.connection     = None

    def generate_components(self):
        """
        :return:
        """
        # Generate a database object
        try:
            self.database = app.database.Database(self.database_location, overwrite=self.overwrite)
            self.database.create_database()
        except:
            raise ValueError("Could not generate the database object.")

        # Generate the interpreter object
        try:
            self.interpreter = app.interpreter.Interpreter(self.database)
        except:
            raise ValueError("Could not generate the interpreter object.")

        try:
            if self.connection_type == "serial":
                self.connection = choose_serial_connection(self.connection_list)
                self.connector = app.connector.SerialConnector(self.connection, time_out=self.timeout)
            if self.connection_type == "bluetooth":
                self.connector = app.connector.BluetoothConnector()
        except:
            raise ValueError("Could not generate the connector object.")

    def run(self, runs=None):
        """
        Begin talking between components.
        :return:
        """
        runs_complete = 0
        while True:
            # Check if we have done enough runs
            if runs is not None:
                if runs_complete >= runs:
                    break
                runs_complete += 1

            # Open the connection if it doesn't exist.
            if not self.connector.is_connected():
                logger.info("Device not connected. Attempting to connect now.")
                self.connector.connect()

            # Read from the connection.
            response = None
            if self.connector.is_connected():
                message = self.connector.retrieve_data()
                # Thanks to the timeout, we do receive a lot of empty messages.
                if message is not "":
                    logger.info("Message: {0}".format(message.strip()))
                else:
                    logger.debug("Message: {0}".format(message))

                try:
                    response = self.interpreter.interpret(message)
                    logger.info("Response: {0}".format(response))
                except ValueError as e:
                    logger.debug(e)
                    if "ERROR" in e.args[0]:
                        pass
                if response is not None:
                    self.connector.write_data(response)


def choose_serial_connection(potential_connections):
    """
    From our list of serial connection options, we need to choose the one that actually exists.
    :return:
    """
    for connection in potential_connections:
        if os.path.exists(connection):
            return connection
    return None


def input_parameters_are_valid(input_parameters):
    """

    :return:
    """
    logger.debug("Checking that inputs are valid...")

    parameter_keys = tuple(input_parameters.keys())
    required_parameters = (
        "database_location",
        "overwrite",
        "timeout",
        "connection_list",
        "connection_type",
    )

    for parameter in required_parameters:
        if parameter not in parameter_keys:
            raise ValueError("Parameter {0} was not specified in input parameters.".format(parameter))

    valid_connection_types = (
        "serial",
        "bluetooth",
    )

    if input_parameters['connection_type'] not in valid_connection_types:
        raise TypeError("Provided connection_type, '{0}', was not of valid types: {1}".format(
            input_parameters['connection_type'],
            valid_connection_types
        ))

    logger.debug("Input parameters are valid.")
    return True


def read_config_yaml(location):
    """
    Read in a .yaml file to pull out our required config files.
    :param location:
    :return:
    """
    with open(location, 'r') as f:
        return yaml.load(f)
