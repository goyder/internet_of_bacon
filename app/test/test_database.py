import unittest
import os
import unittest.mock as mock
import app.database, app.interpreter
import app.test
import app.test.test_interpreter as test_interpreter
import sqlite3
import datetime

"""
test_database.py
Tests to developer the functions of the Database object.
This object needs to handle the creation of, and writing to, a sqlite database.
For the purposes of testing, this is pretty much handled via integration tests.
"""

__author__ = 'Goyder'

def generate_database_object(**kwargs):
    """
    Helper function to generate a database object with the appropriate requirements.
    :return:
    """
    return app.database.Database("test.db", **kwargs)

class TestDatabaseCreation(unittest.TestCase):
    """
    Tests concerned with the creation of the Database object.
    """

    def test_database_object_can_be_created(self):
        """
        Can we simply generate a Database object?
        :return:
        """
        database = generate_database_object()

    def test_database_object_overwrite_parameter_is_set(self):
        """
        If we create a Database object with the 'overwrite' flag, it should be set.
        :return:
        """
        database = generate_database_object(overwrite=True)

        self.assertEqual(
            True,
            database.overwrite == True,
            "Database object did not have an overwrite flag, despite being created with one."
        )

    def test_database_needs_database_object_on_creation(self):
        """
        Creating a database object without specifying the database should fail.
        :return:
        """
        self.assertRaises(TypeError, app.database.Database)


class FunctionalDatabaseCreationTests(unittest.TestCase):
    """
    End to end tests to try out with our database. We have four scenarios.
    1. No database exists.
    2. A database exists, but we don't want to overwrite it: only validate it; and it is valid.
    3. A database exists, but we don't want to overwrite it: only validate it; and it is invalid.
    4. A database exists, but want to overwrite it.
    In each case we simply want to create the database, and ensure it has the right table that we can right to.
    """

    def test_creation_when_no_database_exists(self):
        """
        Create a database where none exists.
        :return:
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create the database object, build the database
        database = app.database.Database(database_filename)
        database.create_database()

        # Pull out the table names from the database we've created.
        column_names = extract_column_names(database_filename)

        # Assert that they are as expected:
        for column_name in app.database.database_columns:
            self.assertEqual(
                True,
                column_name in column_names,
                "Database creation process did not yield the column names expected. Missing: {0}".format(column_name)
            )

    def test_creation_when_valid_database_exists_and_overwrite(self):
        """
        Connect to, and validate a database.
        Two outcomes here: first of all, ensure that the database is valid.
        Second of all, ensure that the original database is unbesmirched, and the original database is destroyed.
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create our pre-existing, _valid_, database.
        database_creation_statement = """
        CREATE TABLE data(
            row_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ID VARCHAR,
            Time DATETIME,
            Value REAL,
            Debug INTEGER
        );
        """
        database_insertion_values = ("Temperature", datetime.datetime.now(), 20.0, 1)

        with sqlite3.connect(database_filename) as conn:
            cur  = conn.cursor()
            cur.execute(database_creation_statement)
            cur.execute("INSERT INTO data (ID, Time, Value, Debug) VALUES (?, ?, ?, ?);", database_insertion_values)
            conn.commit()

            original_data = cur.execute("SELECT * FROM data").fetchall()

        # Create the database object, build the database
        database = app.database.Database(database_filename, overwrite=True)
        database.create_database()

        # Pull out the table names from the database we've created.
        column_names = extract_column_names(database_filename)

        # Assert that they are as expected:
        for column_name in app.database.database_columns:
            self.assertEqual(
                True,
                column_name in column_names,
                "Database creation process did not yield the column names expected. Missing: {0}".format(column_name)
            )

        # Assert that the existing data has been unmolested.
        with sqlite3.connect(database_filename) as conn:
            cur = conn.cursor()
            data_after_investigation = cur.execute("SELECT * FROM data").fetchall()

        self.assertEqual(
            True,
            original_data != data_after_investigation,
            "Data retrieved after investigating database did match original data in Data table."
        )

    def test_creation_when_valid_database_exists(self):
        """
        Connect to, and validate a database.
        Two outcomes here: first of all, ensure that the database is valid.
        Second of all, ensure that the original database is unbesmirched.
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create our pre-existing, _valid_, database.
        database_creation_statement = """
        CREATE TABLE data(
            row_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ID VARCHAR,
            Time DATETIME,
            Value REAL,
            Debug INTEGER
        );
        """
        database_insertion_values = ("Temperature", datetime.datetime.now(), 20.0, 1)

        with sqlite3.connect(database_filename) as conn:
            cur  = conn.cursor()
            cur.execute(database_creation_statement)
            cur.execute("INSERT INTO data (ID, Time, Value, Debug) VALUES (?, ?, ?, ?);", database_insertion_values)
            conn.commit()

            original_data = cur.execute("SELECT * FROM data").fetchall()

        # Create the database object, build the database
        database = app.database.Database(database_filename)
        database.create_database()

        # Pull out the table names from the database we've created.
        column_names = extract_column_names(database_filename)

        # Assert that they are as expected:
        for column_name in app.database.database_columns:
            self.assertEqual(
                True,
                column_name in column_names,
                "Database creation process did not yield the column names expected. Missing: {0}".format(column_name)
            )

        # Assert that the existing data has been unmolested.
        with sqlite3.connect(database_filename) as conn:
            cur = conn.cursor()
            data_after_investigation = cur.execute("SELECT * FROM data").fetchall()

        self.assertEqual(
            True,
            original_data == data_after_investigation,
            "Data retrieved after investigating database did not match original data in Data table."
        )

    def test_creation_when_invalid_database_exists_and_overwrite(self):
        """
        Connect to, and validate a database.
        The only outcome here is that an error is raised.
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create our pre-existing, _invalid_, database.
        database_creation_statement = """
        CREATE TABLE data(
            row_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ID VARCHAR,
            Time DATETIME
        );
        """

        with sqlite3.connect(database_filename) as conn:
            cur  = conn.cursor()
            cur.execute(database_creation_statement)

        # Generate the database.
        database = app.database.Database(database_filename, overwrite=True)
        database.create_database()

        # Pull out the table names from the database we've created.
        column_names = extract_column_names(database_filename)

        # Assert that they are as expected:
        for column_name in app.database.database_columns:
            self.assertEqual(
                True,
                column_name in column_names,
                "Database creation process did not yield the column names expected. Missing: {0}".format(column_name)
            )

    def test_creation_when_invalid_database_exists_and_no_overwrite(self):
        """
        Connect to, and validate a database.
        The only outcome here is that an error is raised.
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create our pre-existing, _invalid_, database.
        database_creation_statement = """
        CREATE TABLE data(
            row_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ID VARCHAR,
            Time DATETIME
        );
        """

        with sqlite3.connect(database_filename) as conn:
            cur  = conn.cursor()
            cur.execute(database_creation_statement)

        # Create the database object, build the database
        database = app.database.Database(database_filename)
        self.assertRaises(sqlite3.DatabaseError, database.create_database)


class TestWriteToDatabase(unittest.TestCase):
    """
    Test the results of attempting to write to a database.
    """

    def test_results_can_be_written_to_database(self):
        """
        Use the write_to_database function to write a set of values to a database.
        """
        database_filename = "test.db"

        # Delete the test database if it exists.
        test_database = os.path.join(os.getcwd(), database_filename)
        if os.path.exists(test_database):
            os.remove(test_database)

        # Create the database and write values to it
        database = app.database.Database(database_filename)
        database.create_database()
        database.write_to_database(app.test.DATA_MESSAGE_PARSED_DICT)

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


def extract_column_names(database_filename):
    """
    For a given database file, ensure that we can go in and extract the right column names from the database we want.
    :param database_filename: Filename of a database to examine.
    :return: The list of column names in the 'datum' table.
    """
    with sqlite3.connect(database_filename) as conn:
        cur = conn.cursor()

        try:
            statement = "PRAGMA table_info(data);"
            cur = cur.execute(statement)
            return tuple([column[1] for column in cur.fetchall()])
        except:
            raise sqlite3.DatabaseError("Could not retrieve the desired column names from database.")
