import logging, logging.config
import yaml
import time
import os, sys
sys.path.insert(0, os.path.abspath('../..'))
import app.connector, app.interpreter, app.database, app.monitor
__author__ = 'Goyder'

def main(app_config, logging_config):
    """
    Main entry point for the bacon monitor.
    :return:
    """
    construct_loggers(logging_config)
    logger = logging.getLogger('logger')

    # Construct the bacon monitoring objects
    parameters = app.monitor.read_config_yaml(app_config)

    monitor = app.monitor.Monitor(parameters)
    logger.info("System running. Ctrl-c to exit program.")
    while True:
        try:
            monitor.generate_components()
            monitor.run()
        except Exception as e:
            logger.info("Encountered error:")
            logger.info(e)
            time.sleep(5)


def construct_loggers(logging_config):
    """
    Construct the logging set-up.
    :param logging_config:
    :return:
    """
    with open(logging_config, 'r') as f:
        logging_config_dict =  yaml.load(f)
    print(logging_config_dict)
    logging.config.dictConfig(logging_config_dict)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bacon_monitor.py [APP_CONFIG].yaml [LOGGING_CONFIG].yaml")
    else:
        app_config = sys.argv[1]
        logging_config = sys.argv[2]
        main(app_config, logging_config)




