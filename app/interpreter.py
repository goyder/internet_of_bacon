import time, datetime
import app.database

"""
interpreter.py
Module for the interpreter object
Accepts and takes action based on input objects.
"""

ERROR_COULD_NOT_UNDERSTAND = "ERROR 001 - Could not understand message."
ERROR_WRONG_TYPE = "ERROR 002 - Interpret command requires a string for input."
ERROR_MISSING_KEYS_IN_MESSAGE = "ERROR 003 - Message was missing crucial keys for writing to database."
ERROR_COULD_NOT_PARSE_VALUES = "ERROR 004 - Could not parse values."
REQUEST_TIME_STRING_FLAG = "R001"  # Deliberately truncated. We only care about this index string.
DATA_MESSAGE_FLAG = "D001"

class Interpreter(object):
    """
    Central object to handle the interpretation of messages.
    Talks to databases and back to the connection.
    """

    def __init__(self, database):
        """
        Creation point for class.
        Define arguments here.
        :return:
        """
        if not isinstance(database, app.database.Database):
            raise TypeError("Interpreter requires a Database object to write to. Was given: {0}".format(
                type(database)
            ))
        self.database = database


    def interpret(self, message):
        """
        Main entry point for class.
        :param message: A string; essentially the command to be carried out.
        :return: A message, indicating if everything worked or not.
        """

        # This object is meant to handle strings.
        if not isinstance(message, str):
            raise TypeError(ERROR_WRONG_TYPE)

        # Check for specific requests.
        if self._message_is_time_request(message):
            return _get_time_response()

        if self._message_is_data_message(message):
            return self._write_to_database(message)

        raise ValueError(ERROR_COULD_NOT_UNDERSTAND)

    def _message_is_time_request(self, message):
        """
        Function to determine if the messsage is a time request.
        :param message: Message to analyse.
        :return: True/False.
        """
        if REQUEST_TIME_STRING_FLAG in message:
            return True
        else:
            return False

    def _message_is_data_message(self, message):
        """
        Function to determine if the message sent is a data message - i.e. something we can write to a database.
        :param message: Message to analyse.
        :return: True/False.
        """
        if DATA_MESSAGE_FLAG in message:
            return True
        else:
            return False

    def _write_to_database(self, message):
        """
        Function to write a valid data message to an external database object.
        :param message: Message to pass off.
        :return: True/False.
        """
        parsed_message = _parse_data_message_to_string_dict(message)
        try:
            parsed_message = _parse_string_dict_to_value_dict(parsed_message)
        except KeyError:
            raise KeyError(ERROR_MISSING_KEYS_IN_MESSAGE)
        except ValueError:
            raise ValueError(ERROR_COULD_NOT_PARSE_VALUES)

        self.database.write_to_database(parsed_message)

        return None


def _get_time_response():
    """
    Produce a response for the Arduino timing circuit of format "T%H%M%S%d%m%Y".
    15 characters in total, starting with 'T'.
    :return: Time response string.
    """
    return time.strftime("T%H%M%S%d%m%Y")


def _parse_data_message_to_string_dict(message):
    """
    Convert a data message into a dictionary.
    :param message: Data message.
    :return: Dictionary of values.
    """
    message = message.split(",")
    data_message_dict = dict()
    for key_value_pair in message:
        try:
            # Ignore empty strings.
            split_key_value_pair = key_value_pair.split(":")
            if split_key_value_pair[0] == "":
                continue
            # The time entry has colons in it, which we would like to rejoin after.
            data_message_dict[split_key_value_pair[0]] = ":".join(split_key_value_pair[1:])  # The .join syntax is bad.
        except IndexError:
            continue
    return data_message_dict


def _parse_string_dict_to_value_dict(string_dict):
    """
    Convert our string dictionary - just a bunch of string pairs - into a dictionary of meaningful key-value pairs
    we can pass to our database.
    :param string_dict: String:string dictionary, roughly converted from input message.
    :return: Key-value pairs, ready for passing to the database object.
    """

    output_dict = string_dict.copy()

    for key in app.database.input_database_keys:
        if key not in output_dict.keys():
            raise KeyError("Expected to find key '{0}' in input dictionary.")
    try:
        output_dict['Value'] = float(string_dict['Value'])
        output_dict['Time'] = datetime.datetime.strptime(string_dict['Time'], "%H:%M:%S %d/%m/%Y")
        output_dict['Debug'] = int(string_dict['Debug'])
    except (TypeError or ValueError):
        raise ValueError("Could not parse values into desired outputs.")

    return output_dict
