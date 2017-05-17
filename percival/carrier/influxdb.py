from influxdb import InfluxDBClient
import logging


class InfluxDB(object):

    def __init__(self, db_host, db_port, db_name):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._db_host = db_host
        self._db_port = db_port
        self._db_name = db_name


        self._log.info("Opening connection to influxDB at {:s}:{:d}".format(db_host, db_port))
        self._influx_client = InfluxDBClient(host=db_host, port=db_port)

        existing_dbs = self._influx_client.get_list_database()
        db_exists = False
        for db in existing_dbs:
            if db['name'] == db_name:
                db_exists = True
                break

        if db_exists:
            self._log.info("{} database exists already".format(db_name))
        else:
            self._log.info("Creating {} database".format(db_name))
            self._influx_client.create_database(db_name)

        self._influx_client.switch_database(db_name)

    def log_point(self, time, measurement, data):
        point = {
            "measurement": measurement,
            "time": time,
            "fields": {}
        }

        for item in data:
            point["fields"][item] = data[item]

        self._influx_client.write_points([point])
