import unittest
import unittest.mock as mock
import importlib
import app.interpreter
import app.database
from app.test import DATA_MESSAGE, DATA_MESSAGE_DEBUG, DATA_MESSAGE_DICT, DATA_MESSAGE_DICT_DEBUG, \
    DATA_MESSAGE_PARSED_DICT

"""
test_interpreter.py
Tests to support the development and functioning of the Interpreter class.
"""

__author__ = 'Goyder'

# Reference values - samples for further analysis


def generate_interpreter_object():
    """
    It's quite possible the interface to the main interpreter object will change over time.
    Hence, here's a helper object to generate the object for 90% of cases, unless we're testing specific initialisation
    code.
    :return: A plain-jane instance of the interpreter object.
    """
    database = mock.Mock(spec=app.database.Database)
    interpreter = app.interpreter.Interpreter(database)
    return interpreter


class TestInterpreter(unittest.TestCase):
    """
    Test our interpreter object.
    """

    def test_initialisation(self):
        """
        Test if we can start an interpreter object safely and cleanly. Essentially a canary-in-coalmine test.
        :return:
        """
        try:
            interpreter = generate_interpreter_object()
        except:
            interpreter = None

        self.assertEquals(
            True,
            interpreter is not None,
            "Did not generate an interpreter object."  # Kind of a cop out, if this test fails you'll never get here
        )

    def test_interpreter_not_created_without_database_parameter(self):
        """
        Test that the interpreter will reject creation unless we pass it a database object to kick-off.
        :return:
        """
        self.assertRaises(TypeError, app.interpreter.Interpreter)

    def test_interpreter_not_created_without_database_object(self):
        """
        Test that the interpreter will reject creation unless we pass it an actual database object.
        :return:
        """
        self.assertRaises(TypeError, app.interpreter.Interpreter, "I am not a database.")

    def test_interpreter_rejects_non_strings(self):
        """
        If we try and pass the interpreter something that isn't a string, it should get upset.
        Cue the argument about Python type-checking.
        :return:
        """
        interpreter = generate_interpreter_object()
        self.assertRaises(TypeError, interpreter.interpret, 1.0)
        self.assertRaises(TypeError, interpreter.interpret, 1)
        self.assertRaises(TypeError, interpreter.interpret, ["What."])

    def test_garbage_prompt(self):
        """
        If we pass a garbage message to the interpreter, it should reject our message.
        :return:
        """
        interpreter = generate_interpreter_object()

        message = "garbage message."

        self.assertRaises(ValueError, interpreter.interpret, message)


class TestInterpreterTimeResponses(unittest.TestCase):
    """
    Tests to query the functioning of the time response of the interpreter.
    """

    def test_check_time_response_format(self):
        """
        If we push a prompt to the interpreter that deserves a time response, it should get one back.
        """
        interpreter = generate_interpreter_object()
        request = "R001 - please set time in format 'T%H%M%S%d%m%Y'."

        response = interpreter.interpret(request)

        # First check - did the interpreter understand it?
        self.assertEquals(
            True,
            "ERROR" not in response,
            "Received an error in the response when a time value was requested."
        )

        # When we try to get a time message back, it should be in a standard format.
        # The format is "THHMMSSddmmYYYY". The first T is a character, 'T'.
        self.assertEquals(
            response[0] == "T",
            True,
            "Time response message did not start with a 'T'."
        )

        self.assertEquals(
            len(response) == 15,
            True,
            "Time response was not of length 15."
        )


class TestInterpreterDatabaseCalls(unittest.TestCase):
    """
    Tests to query that the interpreter is making the right calls to the database object when it receives a valid
    data entry value.
    """

    def test_interpreter_recognises_data_message(self):
        """
        The interpreter must be able to recognise the data message as such.
        :return:
        """
        interpreter = generate_interpreter_object()

        recognised_as_data_message = interpreter._message_is_data_message(DATA_MESSAGE)

        self.assertEqual(
            True,
            recognised_as_data_message,
            "Valid data message was not recognised as such."
        )

    def test_interpreter_calls_write_to_database_functions(self):
        """
        Ensure that if a data message is received, the intepreter will at least recognise it as such and call the
        function to write to a database.
        """
        interpreter = generate_interpreter_object()

        interpreter.database.write_to_database = mock.Mock()
        interpreter.interpret(DATA_MESSAGE)

        self.assertEqual(
            interpreter.database.write_to_database.called,
            True,
            "Interpreter did not write to database when passed a valid data message."
        )

    def test_interpreter_calls_write_to_database_function_with_right_argument(self):
        """
        When we receive a valid data message, it needs to be parsed completely and handed off to the database
        system.
        """
        interpreter = generate_interpreter_object()

        interpreter.database.write_to_database = mock.Mock()
        interpreter.interpret(DATA_MESSAGE)
        interpreter.database.write_to_database.assert_called_with(DATA_MESSAGE_PARSED_DICT)

    def test_interpreter_write_to_database_fails_with_missing_keys(self):
        """
        When we receive a valid data message, it needs to be parsed completely and handed off to the database
        system.
        """
        interpreter = generate_interpreter_object()

        interpreter.database.write_to_database = mock.Mock()

        for key in app.database.input_database_keys:
            mangled_data_message = DATA_MESSAGE.replace(key, "")
            self.assertRaises(KeyError, interpreter.interpret, mangled_data_message)

    def test_interpreter_write_to_database_fails_with_unparseable_data(self):
        """
        Interpreter should report an error if the data that is fed through cannot be parsed into a meaningful format.
        """
        interpreter = generate_interpreter_object()

        interpreter.database.write_to_database = mock.Mock()

        mangled_data_message_time = DATA_MESSAGE.replace("20:47:40 23/01/2017", "Unparseable")
        mangled_data_message_debug = DATA_MESSAGE.replace("Debug:0", "Debug:Unparseable")
        mangled_data_message_value = DATA_MESSAGE.replace("22.70", "Unparseable.")

        for mangled_message in [mangled_data_message_debug, mangled_data_message_time, mangled_data_message_value]:
            self.assertRaises(ValueError, interpreter.interpret, mangled_message)


class TestInterpreterModulePrivateFunctions(unittest.TestCase):
    """
    Tests to non-public interface points, if necessary.
    """

    def setUp(self):
        """
        Ensure that we don't have overlap with other mocks from other classes.
        :return:
        """
        importlib.reload(app.interpreter)

    def test_data_message_converted_to_dict(self):
        """
        Test that if we pass the data-parsing function a proper data message, we'll get a dictionary back.
        :return:
        """
        self.assertEqual(
            True,
            DATA_MESSAGE_DICT == app.interpreter._parse_data_message_to_string_dict(DATA_MESSAGE),
            "Returned data dictionary did not match expected output after parsing."
        )
        self.assertEqual(
            True,
            DATA_MESSAGE_DICT_DEBUG == app.interpreter._parse_data_message_to_string_dict(DATA_MESSAGE_DEBUG),
            "Returned data dictionary did not match expected output after parsing."
        )

    def test_garbled_data_message_still_converted(self):
        """
        Even if we get a half-written message, we should still be able to return something.
        :return:
        """
        # What if we only get the end
        garbled_message = DATA_MESSAGE[15:]
        garbled_message_dict = app.interpreter._parse_data_message_to_string_dict(garbled_message)
        self.assertEqual(
            True,
            type(garbled_message_dict) == dict,
            "Attempting to parse the end of a garbled message did not yield a response."
        )

        # What if we only get the start
        garbled_message = DATA_MESSAGE[:15]
        garbled_message_dict = app.interpreter._parse_data_message_to_string_dict(garbled_message)
        self.assertEqual(
            True,
            type(garbled_message_dict) == dict,
            "Attempting to parse the start of a garbled message did not yield a response."
        )

        # What if we only get the middle
        garbled_message = DATA_MESSAGE[5:-5]
        garbled_message_dict = app.interpreter._parse_data_message_to_string_dict(garbled_message)
        self.assertEqual(
            True,
            type(garbled_message_dict) == dict,
            "Attempting to parse the middle of a garbled message did not yield a response."
        )
