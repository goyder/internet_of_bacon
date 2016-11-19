import sqlite3
import config, bt_interface
import logging
import time, datetime
import random
import sys

__author__ = 'Goyder'
"""
database.py
Main library to handle:
- The creation
- The contact w/
- The parsing of data
of the central database of the IOW.
"""

# Establish our log
log = logging.getLogger("logger")
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(config.logfile)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
log.addHandler(fh)
log.addHandler(ch)

def main(debug=False, purge=False):
    # Include a debug flag for differing operation.
    log.info("==================")
    log.info("Program initiated.")
    log.info("==================")
    if debug:
        log.debug("*** Debug mode enabled. ***")
    if purge:
        log.info("*** Purge mode enabled. ***")

    # Connect to the database. Create the table.
    log.info("Establishing connection to database file.")
    try:
        with sqlite3.connect(config.file) as con:
            cur = con.cursor()
            if purge:
                log.info("Dropping existing table...")
                cur.execute("DROP TABLE IF EXISTS ProcessDatum")
                log.info("Creating new table...")
                cur.execute("CREATE TABLE ProcessDatum(id VARCHAR, value REAL, time DATETIME)")
                con.commit()
                log.info("Done.")
    except sqlite3.OperationalError as e:
        log.error( "Encountered operational error in creation:")
        log.error(e.message)
    except Exception as e:  # Something generic went bad.
        log.error("Encountered error in creation:")
        log.error(e.message)

    # Main loop for listening.
    # Needs to:
    #  - Ensure we're connected to Bluetooth
    #  - Receive a message
    #  - Parse and insert this message.
    try:
        # Periodically poll the connection
        connected = False
        while True:
            # Initialise our variables
            message = None
            parsed_message = None

            # Ensure a connection is open.
            if not connected:
                if not debug:
                    connected = bt_interface.connect()

            # Retrieve the messages.
            message = bt_interface.get_readings(debug=debug)

            # If we retrieved something, handle it.
            if message is not None:
                log.debug("Received message:")
                log.debug("'{0}'".format(message))

                # Parse the message.
                try:
                    parsed_message = parse_message(message)
                except ValueError:
                    log.info("Could not parse message. Message ignored.")

                # If we got something useful...
                if parsed_message is not None:
                    # Write the message
                    with sqlite3.connect(config.file) as con:
                        cur = con.cursor()
                        log.debug("Writing row to dataset:")
                        log.info("  {0}".format(str(parsed_message)))
                        cur.execute("INSERT INTO ProcessDatum VALUES (?,?,?)", parsed_message)
            time.sleep(1)

    except KeyboardInterrupt:
        log.info("Exited main loop via keyboard interrupt.")
        with sqlite3.connect(config.file) as con:
                cur = con.cursor()
                for row in cur.execute("""
                SELECT *
                FROM ProcessDatum
                ORDER BY time
                LIMIT 5
                """
                                       ):
                    log.debug(row)


def parse_message(message):
    """
    Take the expected message from the Arduino and parse it into a form for SQL insertion.
    :param message: String in the format "tag, value".
    :return:
    """
    try:
        components = message.split(",")
        return (
            str(components[0]),
            float(components[1]),
            datetime.datetime.now(),
        )
    except:
        raise ValueError


# Main entry point for program.
if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 1:
        if "debug" in sys.argv:
            debug = True
        if "purge" in sys.argv:
            purge = True

    main(debug=debug, purge=purge)
