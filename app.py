
from google.cloud import bigquery
import pandas
import os
from Messages import getMessages, columns, getNumberOfMessages
from dotenv import load_dotenv
import json
import time
load_dotenv()
CREDENTIALS = {
    "type": "service_account",
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", '\n'),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
}
# print(CREDENTIALS)
with open("creds.json", "w") as outfile:
    json.dump(CREDENTIALS, outfile)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "creds.json"

def loadEmails(n_start, n_end):
    try:
        client = bigquery.Client()
        # TODO(developer): Set table_id to the ID of the table to create.
        table_id = os.getenv("TABLE_ID")
        # print(columns)

        adjustedColumns = [i.replace("-", "") for i in columns]
        adjustedColumns.append("MessageText")
        # print(adjustedColumns)
        records = []
        getMessages(n_start, n_end,records)
        dataframe = pandas.DataFrame(
                records,
                columns=adjustedColumns,
                # index=[i['MessageID'] for i in records]
        )
            # print(dataframe.columns)
            # dataframe.to_csv("sheesh.csv")
        job_config = bigquery.LoadJobConfig(
                # write_disposition="WRITE_TRUNCATE",
            )

        
        if n_start == 0:
            job = client.load_table_from_dataframe(    
                    dataframe, table_id,job_config=job_config
            )  # Make an API request.
            job.result()  # Wait for the job to complete.
        else:
            
            job = client.load_table_from_dataframe(    
                    dataframe, table_id
            )  # Make an API request.
            job.result()  # Wait for the job to complete.
        table = client.get_table(table_id)  # Make an API request.
        print(
                "Loaded {} rows and {} columns to {}".format(
                    table.num_rows, len(table.schema), table_id
                )
            )

    except Exception as e:
        print("upload table error")
        print(e)
n=10000
t = getNumberOfMessages()
while True:
    for i in range(t//n):
        try: 
            loadEmails(i*n, (i+1) * n)
        except Exception as e: 
            print("=====Loading Emails was unsuccessful=====")
            print(e)
    try:
        loadEmails(t//n*n,t)
    except Exception as e: 
        print("=====Loading Emails was unsuccessful=====")
        print(e)
    print("Got all the Messages")
    for i in range( * 60 * 60 ,0,-1):
        print(f"{int(i/60)} minutes and {i%60} seconds")
        time.sleep(1)


    
