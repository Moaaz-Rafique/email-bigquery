import datetime

from google.cloud import bigquery
import pandas
import pytz
import os
from app import getMessages, columns
import time
from dotenv import load_dotenv
load_dotenv()

while True:
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "creds.json"
        client = bigquery.Client()

        # TODO(developer): Set table_id to the ID of the table to create.
        table_id = os.getenv("TABLE_ID")

        # print(columns)

        adjustedColumns = [i.replace("-", "") for i in columns]
        adjustedColumns.append("MessageText")
        print(adjustedColumns)


        records = getMessages()


        dataframe = pandas.DataFrame(
            records,
            columns=adjustedColumns,
            # index=[i['MessageID'] for i in records]
        )

        # print(dataframe.columns)

        # dataframe.to_csv("sheesh.csv")


        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )

        job = client.load_table_from_dataframe(    
            dataframe, table_id,job_config
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )

    except Exception as e:
        print(e)

    for i in range(1 * 3 * 60 ,0,-1):
        print(f"{int(i/60)}minutes and {i%60} seconds", end="\r", flush=True)
        time.sleep(1)