import datetime

DATA_MESSAGE = "Flag:D001,Time:20:47:40 23/01/2017,Value:22.70,ID:Temperature,Debug:0,"
DATA_MESSAGE_DEBUG = "Flag:D001,Time:20:47:40 23/01/2017,Value:22.70,ID:Temperature,Debug:1,"

DATA_MESSAGE_DICT = {
    "Flag": "D001",
    "Time": "20:47:40 23/01/2017",
    "ID": "Temperature",
    "Value": "22.70",
    "Debug": "0"
}
DATA_MESSAGE_DICT_DEBUG = {
    "Flag": "D001",
    "Time": "20:47:40 23/01/2017",
    "ID": "Temperature",
    "Value": "22.70",
    "Debug": "1"
}

DATA_MESSAGE_PARSED_DICT = {
    "Flag": "D001",
    "Time": datetime.datetime.strptime("20:47:40 23/01/2017","%H:%M:%S %d/%m/%Y"),
    "ID": "Temperature",
    "Value": 22.70,
    "Debug": 0
}
DATA_MESSAGE_PARSED_DICT_DEBUG = {
    "Flag": "D001",
    "Time": datetime.datetime.strptime("20:47:40 23/01/2017","%H:%M:%S %d/%m/%Y"),
    "ID": "Temperature",
    "Value": 22.70,
    "Debug": 1
}

# Note that these values assume that this is the first entry in the database.
DATA_MESSAGE_OUT_OF_DATABASE = (1, 'Temperature', '2017-01-23 20:47:40', 22.7, 0)
DATA_MESSAGE_OUT_OF_DATABASE_DEBUG = (1, 'Temperature', '2017-01-23 20:47:40', 22.7, 1)