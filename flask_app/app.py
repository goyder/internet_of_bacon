from flask import Flask, Response, render_template, jsonify, request
import os, sys
sys.path.insert(0, os.path.abspath('..'))
import flask_app.config as config
import sqlite3

__author__ = 'Goyder'
app = Flask(__name__)


def get_json_data():
    """
    Retrieve all of the available log from the database.
    :return:
    """
    with sqlite3.connect(config.DATABASE_LOCATION) as conn:
        cur = conn.cursor()
        cur = cur.execute("SELECT * FROM data;")
        output_data = cur.fetchall()
    return (output_data)


@app.route("/test_data")
def get_test_csv_data():
    """
    Return the test csv data for testing purposes.
    :return:
    """
    with open("local_config/testdata.csv") as f:
        test_csv = f.read()
    return Response(test_csv)


@app.route("/")
def hello_world():
    # Accept debug parameters from the URL.
    # e.g. "0.0.0.0:5000/?debug=true" yields an input from a mock CSV file.
    debug = request.args.get("debug")
    if debug is not None:
        debug = "true"
    else:
        debug = "false"

    return render_template(
        "index.html",
        debug=debug,
    )


@app.route("/data")
def return_data():
    data = retrieve_data()
    data = convert_list_to_csv(data)
    return Response(data)


def retrieve_data(start_datetime="0001-01-01 00:00:00", end_datetime="2100-01-01 00:00:00"):
    """
    Retrieve data from a given database.
    :param startdate:
    :param enddate:
    :return:
    """

    with sqlite3.connect(config.DATABASE_LOCATION) as conn:
        cur  = conn.cursor()
        insertion = (start_datetime, end_datetime,)
        cur.execute('SELECT Time, ID, Value FROM data WHERE Time BETWEEN datetime( ? ) AND datetime(?)', insertion)
    return cur.fetchall()

def convert_list_to_csv(list):
    """
    Convert a list (retrieved from a database) to a string in csv format.
    :param list:
    :return:
    """
    csv_string = "Datetime,ID,Value\n"
    for row in list:
        csv_string += "{0},{1},{2}\n".format(row[0], row[1], row[2])
    return csv_string

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

