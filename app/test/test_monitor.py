import unittest, unittest.mock
from unittest.mock import patch
import app.interpreter, app.monitor, app.database, app.connector
from importlib import reload

__author__ = 'Goyder'


def generate_monitor_object():
    """
    Build a monitor object for the purposes of these tests.
    :return:
    """
    input_parameters = generate_input_parameter_object_minus_inputs()
    monitor =  app.monitor.Monitor(input_parameters)
    return monitor

def generate_input_parameter_object_minus_inputs(*args):
    """
    Return a valid input parameter object, _without_ whatever parameter is specified on creation.
    :param args:
    :return:
    """
    parameters = {
        "connection_type"   : "serial",
        "database_location" : "test.db",
        "overwrite"         : False,
        "timeout"           : 1.0,
        "connection_list"   : ["/dev/tty.wchusbserial1410", "/dev/tty.wchusbserial1420"]
    }
    for option in args:
        try:
            del parameters[option]
        except KeyError:
            print("Could not remove key '{0}'.".format(option))

    return parameters


class TestInputParameterValidation(unittest.TestCase):
    """
    Test the validation of inputs to the system.
    """

    def setUp(self):
        reload(app.interpreter)
        reload(app.monitor)
        reload(app.database)
        reload(app.connector)


    def test_system_requires_database_config(self):
        """
        Ensure that the test system requires the database configuration options.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs("database_location")

        self.assertRaises(
            ValueError,
            app.monitor.Monitor,
            parameters
        )

    def test_monitor_sets_database_config_option(self):
        """
        When we build the monitor object, the database config should be set.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        monitor = app.monitor.Monitor(parameters)

        parameters_to_validate = [
            "database_location",
            "overwrite",
        ]

        for parameter in parameters_to_validate:
            self.assertEqual(
                True,
                getattr(monitor,parameter) == parameters[parameter],
                "Monitor object did not set parameter '{0}'.".format(parameter)
            )

    def test_monitor_sets_connection_type(self):
        """
        When we build the monitor object, the type of connection should be set.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        monitor = app.monitor.Monitor(parameters)

        parameters_to_validate = [
            "connection_type"
        ]

        for parameter in parameters_to_validate:
            self.assertEqual(
                True,
                getattr(monitor, parameter) == parameters[parameter],
                "Monitor object did not set parameter '{0}'.".format(parameter)
            )

    def test_monitor_rejects_invalid_connection_types(self):
        """
        When we build the monitor object, it should only accept 'serial' or 'bluetooth' as connection types.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        parameters["connection_type"] = "invalid type"

        self.assertRaises(
            TypeError,
            app.monitor.Monitor,
            parameters
        )

    def test_monitor_accepts_valid_connection_types(self):
        """
        When we build the monitor object, it should only accept 'serial' or 'bluetooth' as connection types.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()

        parameters["connection_type"] = "serial"
        monitor = app.monitor.Monitor(parameters)

        parameters["connection_type"] = "bluetooth"
        monitor = app.monitor.Monitor(parameters)

    def test_monitor_sets_connection_options(self):
        """
        When we build the monitor object, the connection options should be set.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        monitor = app.monitor.Monitor(parameters)

        parameters_to_validate = [
            "timeout",
            "connection_list"
        ]

        for parameter in parameters_to_validate:
            self.assertEqual(
                True,
                getattr(monitor, parameter) == parameters[parameter],
                "Monitor object did not set parameter '{0}'.".format(parameter)
            )


class TestCreationOfMonitor(unittest.TestCase):

    def setUp(self):
        reload(app.interpreter)
        reload(app.monitor)
        reload(app.database)
        reload(app.connector)

    def test_monitor_can_be_created(self):
        """
        Can we simply create a monitor object? What's the entry?
        :return:
        """
        monitor = generate_monitor_object()

    def test_creation_fails_if_database_fails(self):
        """
        If the creation of the sub-components fails, then the monitor needs to fail.
        :return:
        """
        monitor = generate_monitor_object()

        database_mock = unittest.mock.Mock()
        database_mock.side_effect = Exception
        app.database.Database = database_mock

        self.assertRaises(
            ValueError,
            monitor.generate_components,
        )

    def test_creation_fails_if_interpreter_fails(self):
        """
        If the creation of the sub-components fails, then the monitor needs to fail.
        :return:
        """
        monitor = generate_monitor_object()
        interpreter_mock = unittest.mock.Mock()
        interpreter_mock.side_effect = Exception
        app.interpreter.Interpreter = interpreter_mock

        self.assertRaises(
            ValueError,
            monitor.generate_components,
        )

    def test_connection_type_parameter_changes_connector_object(self):
        """
        The type of connection that is opened should depend on the connection_type parameter.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()

        serial_connector_mock = unittest.mock.Mock()
        app.connector.SerialConnector = serial_connector_mock
        bluetooth_connector_mock = unittest.mock.Mock()
        app.connector.BluetoothConnector = bluetooth_connector_mock

        parameters["connection_type"] = "serial"
        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()

        self.assertEqual(
            True,
            serial_connector_mock.called,
            "Serial connector was not called to be created despite setting being right."
        )

        parameters["connection_type"] = "bluetooth"
        monitor = app.monitor.Monitor(parameters)
        monitor.generate_components()

        self.assertEqual(
            True,
            bluetooth_connector_mock.called,
            "Bluetooth connector was not called to be created despite setting being right."
        )

    def test_creation_fails_if_SerialConnector_fails(self):
        """
        If the creation of the sub-components fails, then the monitor needs to fail.
        :return:
        """
        monitor = generate_monitor_object()

        connector_mock = unittest.mock.Mock()
        connector_mock.side_effect = Exception
        app.connector.SerialConnector = connector_mock

        self.assertRaises(
            ValueError,
            monitor.generate_components,
        )

    def test_creation_fails_if_BluetoothConnector_fails(self):
        """
        If the creation of the sub-components fails, then the monitor needs to fail.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        parameters['connection_type'] = "bluetooth"
        monitor = app.monitor.Monitor(parameters)

        connector_mock = unittest.mock.Mock()
        connector_mock.side_effect = Exception
        app.connector.BluetoothConnector = connector_mock

        self.assertRaises(
            ValueError,
            monitor.generate_components,
        )

class TestSerialConnectorCreation(unittest.TestCase):
    """
    Collection of tests to ensure the Serial Connector gets generated as required.
    """

    def setUp(self):
        reload(app.interpreter)
        reload(app.monitor)
        reload(app.database)
        reload(app.connector)

    def test_error_raised_if_no_connections_available(self):
        """
        If we try to make a serial connection but not connections can be formed, an error should be raised.
        :return:
        """
        parameters = generate_input_parameter_object_minus_inputs()
        parameters['connection_type'] = 'serial'

        monitor = app.monitor.Monitor(parameters)
        choose_serial_connection = unittest.mock.Mock(side_effect=ValueError)
        app.monitor.choose_serial_connection = choose_serial_connection

        self.assertRaises(
            ValueError,
            monitor.generate_components
        )


class TestSerialSelection(unittest.TestCase):
    """
    Tests to assess the functioning of the serial selection function.
    """

    def setUp(self):
        reload(app.interpreter)
        reload(app.monitor)
        reload(app.database)
        reload(app.connector)

    def test_choose_serial_connection_can_choose_the_right_connection(self):
        """
        The monitor object should choose the right serial connection for the job.
        :return:
        """

        connection_list  = ["/dev/tty.wchusbserial1410", "/dev/tty.wchusbserial1420"]
        def return_true_on_specific_option(option):
            if option == connection_list[0]:
                return True
            else:
                return False

        exists = unittest.mock.Mock()
        exists.side_effect = return_true_on_specific_option
        app.monitor.os.path.exists = exists

        connection = app.monitor.choose_serial_connection(connection_list)

        self.assertEqual(
            True,
            connection == connection_list[0],
            "Connection returned did not match required value."
        )

    def test_choose_serial_connection_can_choose_the_second_connection(self):
        """
        The monitor object should choose the right serial connection for the job.
        :return:
        """
        connection_list  = ["/dev/tty.wchusbserial1410", "/dev/tty.wchusbserial1420"]

        # Repeat - but the opposite way around
        def return_true_on_specific_option(option):
            if option == connection_list[1]:
                return True
            else:
                return False

        exists = unittest.mock.Mock()
        exists.side_effect = return_true_on_specific_option
        app.monitor.os.path.exists = exists

        connection = app.monitor.choose_serial_connection(connection_list)

        self.assertEqual(
            True,
            connection == connection_list[1],
            "Connection returned did not match required value."
        )

