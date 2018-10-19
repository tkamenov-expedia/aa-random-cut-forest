import os
import datetime

from .athena.athena_bookings_queries import AthenaBookings


class Fetcher:

    def __init__(self):
        self.athena_bookings = AthenaBookings()

    def query(self, query_parameters):
        """ Starts bookings time series data query in Athena. Saves the result to specified s3 location in .csv format. """
        query_id = self.athena_bookings.start_query_execution(query_parameters)
        time = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")

        if query_id:
            train_set_path = os.path.join('s3://',
                                          query_parameters['s3']['train_bucket'],
                                          query_parameters['s3']['train_set_prefix'],
                                          '')
            csv_filename = '{}.{}'.format(query_id, 'csv');
            return query_id

    def query_and_fetch(self, query_parameters):
        query_id = self.query(query_parameters)
        if query_id:
            return query_id, self.athena_bookings.fetch_data(query_id)


