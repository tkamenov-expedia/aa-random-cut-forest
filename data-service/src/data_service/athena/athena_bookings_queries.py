import time
import boto3
import os

class AthenaBookings:

    query_string =   """SELECT timestamp AS date,
                            value AS current
                        FROM
                            (SELECT value,
                                  timestamp
                            FROM "{}"."{}"
                            WHERE tags['lob'] = '{}'
                                AND tags['pos']='{}'
                            ORDER BY  timestamp DESC LIMIT {})
                        ORDER BY  timestamp ASC; """

    def __init__(self):
        self.athena = boto3.client('athena', 'us-west-2')

    def start_query_execution(self, query_parameters):
        """ Start athena query execution to get execution_id """
        query = self.query_string.format(
            query_parameters['database']['name'],
            query_parameters['database']['table'],
            query_parameters['tags']['lob'],
            query_parameters['tags']['pos'],
            query_parameters['database']['limit']
        )
        print("Start executing Athena query: {}".format(query))

        s3_output = os.path.join(
            's3://',
            query_parameters['s3']['train_bucket'],
            query_parameters['s3']['train_set_prefix'])
        print("Running query and writing the result to: " + s3_output)

        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': query_parameters['database']['name']
            },
            ResultConfiguration={
                'OutputLocation': s3_output,
            }
        )
        print('Execution ID: ' + response['QueryExecutionId'])
        return response['QueryExecutionId']

    def fetch_data(self, query_id):
        """ Fetch results locally after calling athena's start_query_execution
        (in run_query method) the result is converted to protobuf format and uploaded as .pbr file """
        query_status = None
        while query_status in ['QUEUED', 'RUNNING'] or query_status is None:
            query_status = self.athena.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
            if query_status in ['FAILED', 'CANCELLED']:
                raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_id))
            time.sleep(10) # wait a bit for status to change
        results_paginator = self.athena.get_paginator('get_query_results')
        results_iter = results_paginator.paginate(
            QueryExecutionId=query_id,
            PaginationConfig={
                'PageSize': 1000
            }
        )
        results = []
        data_list = []
        for results_page in results_iter:
            for row in results_page['ResultSet']['Rows']:
                data_list.append(row['Data'])
        for datum in data_list[1:]:
            results.append([x['VarCharValue'] for x in datum])
        #return [(datetime.utcfromtimestamp(int(x[0])).strftime('%Y-%m-%d %H:%M:%S'),
        #         float(x[1])) for x in results]

        #return [float(x[1]) for x in results]
        return [[float(x[0]), float(x[1])] for x in results]
