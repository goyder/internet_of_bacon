import sqlite3
import os

__author__ = 'Goyder'

"""
database.py
Module for the database object.
Accepts data ready for database injection.
Handles the interaction with database files.
"""

table_definition = {'row_ID': 'INTEGER', 'Time': 'DATETIME', 'Debug': 'INTEGER', 'Value': 'REAL', 'ID': 'VARCHAR'}
# The database has these columns.
database_columns = tuple([column for column in table_definition.keys()])
# In order to accept a dictionary to be written to, it must have these keys.
input_database_keys = tuple([column for column in database_columns if column != "row_ID"])

class Database(object):
    """
    Handles creating and writing data to the database object.
    """

    def __init__(self, database_location, overwrite=False):
        """
        :param overwrite: If True, the Database should clear and overwrite any database it finds.
        :return:
        """
        self.overwrite = overwrite
        self.database_location = database_location

    def create_database(self):
        """
        Create a database using the information supplied on creation.
        :return:
        """
        # If the database already exists...
        create_new_database = True

        if os.path.exists(self.database_location):
            if self.database_is_valid() and not self.overwrite:
                create_new_database = False
            elif self.overwrite:  # We just totally scrap the file. We could just drop the reference table...
                self.delete_database()
            else:
                raise(sqlite3.DatabaseError("Database already exists, but is invalid for writing to."))

        if create_new_database:
            database_creation_statement = """
            CREATE TABLE data(
                row_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                ID VARCHAR,
                Time DATETIME,
                Value REAL,
                Debug INTEGER
            );
            """
            with sqlite3.connect(self.database_location) as conn:
                cur = conn.cursor()
                cur.execute(database_creation_statement)

    def database_is_valid(self):
        """
        Check if an existing database is valid for these purposes.
        :return:
        """
        with sqlite3.connect(self.database_location) as conn:
            cur = conn.cursor()
            try:
                statement = "PRAGMA table_info(data);"
                cur = cur.execute(statement)
                column_info = {column[1]: column[2] for column in cur.fetchall()}
            except:
                return False

        return column_info == table_definition

    def delete_database(self):
        """
        Delete a database file.
        :return:
        """
        os.remove(self.database_location)

    def write_to_database(self, value_dictionary):
        """
        Write a dictionary of values to the database.
        :param parseable_dictionary: A dictionary of key-value pairs ready for writing.
        :return:
        """
        # Key question - do we want to validate before attempting to write to the database?
        with sqlite3.connect(self.database_location) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO data (ID, Time, Value, Debug) VALUES (?, ?, ?, ?);",
                (value_dictionary["ID"],
                 value_dictionary["Time"],
                 value_dictionary["Value"],
                 value_dictionary["Debug"]
                 )
            )
            conn.commit()


