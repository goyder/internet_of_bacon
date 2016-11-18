import sqlite3
import config
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

def main(debug=False):
    # Include a debug flag for differing operation.
    if debug:
        log.debug("*** Debug mode enabled. ***")

    # Connect to the database. Create the table.
    log.info("Establishing connection to database file.")
    try:
        with sqlite3.connect(config.file) as con:
            cur = con.cursor()
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
        while True:
            message = None
            parsed_message = None

            # TODO: Include the Bluetooth connection here.

            # Don't connect to the Bluetooth system.
            if debug:
                message = get_debug_message()
            if message is not None:
                log.info("Received message:")
                log.info("'{0}'".format(message))

                try:
                    parsed_message = parse_message(message)
                except ValueError:
                    log.info("Could not parse message. Message ignored.")

                if parsed_message is not None:
                    # Write the message
                    with sqlite3.connect(config.file) as con:
                        cur = con.cursor()
                        log.info("Writing row to dataset:")
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


def get_debug_message():
    """
    Generate a generic message, like from the Arduino..
    :return: Pseudo arduino message.
    """
    if random.random() < 0.8:
        tag_names = ["sensor_1", "sensor_2", "sensor_3"]
        item = random.choice(tag_names)
        return "{0},{1}".format(item, random.randrange(0,100))
    else:
        return "GARBAGE MESSAGE!"


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
        if sys.argv[1] == "debug" or sys.argv[1] == "d":
            debug = True

    main(debug=debug)
