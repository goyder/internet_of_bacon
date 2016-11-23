import sqlite3
import config, bt_interface
import logging
import time, datetime
import random
import sys

import_error = None
try:
    import bluetooth
except ImportError as e:
    import_error = e.args[0]



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
    if import_error:
        log.error("Encountered following errors during start-up:")
        log.error("    " + import_error)
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
            message = []
            parsed_message = None

            if debug:
                message = get_debug_readings()
            else:
                # Ensure a connection is open.
                if not connected:
                    try:
                        connection = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                        connection.connect((config.bt_addr, config.bt_port))
                        connection.settimeout(0.1)  # very short timeout for purposes of reading data
                        connection = connection.makefile()
                        connected = True
                        log.info("Successfully made bluetooth connection.")
                    except bluetooth.BluetoothError as e:
                        log.error("Encountered BluetoothError when attempting to connect:")
                        log.error(e.args[0])
                        connected = False

                # Read from the connection.
                if connected:
                    while True:
                        try:
                            log.debug("Attempting to read messages...")
                            message += connection.readline()
                        except bluetooth.BluetoothError as e:
                            if e.args[0] == "timed out":
                                log.debug("Message retrieval complete. Encountered timeout.")
                                break
                            else:
                                log.info("Connection was broken.")
                                log.debug(e)
                                connected = False
                                connection.close()
                                break
                        except IOError as e:
                            log.info("Connection was broken - IOError.")
                            log.debug(e)
                            connected = False
                            connection.close()
                            break

            # If we retrieved something, handle it.
            if len(message) > 0:
                log.debug("Received message:")
                log.debug("'{0}'".format(message))

                # Parse the message.
                for message_line in message:
                    try:
                        parsed_message = parse_message(message_line)
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
                            # We are connecting once per write. That's not right!
            time.sleep(1)

    except KeyboardInterrupt:
        log.info("Exited main loop via keyboard interrupt.")
        if connection:
            connection.close()
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


def get_debug_readings():
    """
    Retrieve fake readings from a Bluetooth connection.
    :return:
    """
    readings = []
    for i in range(random.choice((1,2,3))):
        if random.random() < 0.8:
            tag_names = ["sensor_1", "sensor_2", "sensor_3"]
            item = random.choice(tag_names)
            readings.append( "{0},{1}".format(item, random.randrange(0,100)))
        else:
            readings.append( "GARBAGE MESSAGE!")
        return readings

# Main entry point for program.
if __name__ == "__main__":
    debug = False
    purge = False
    if len(sys.argv) > 1:
        if "debug" in sys.argv:
            debug = True
        if "purge" in sys.argv:
            purge = True

    main(debug=debug, purge=purge)
