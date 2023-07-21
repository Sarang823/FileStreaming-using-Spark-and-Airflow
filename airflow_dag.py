from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
# from airflow.sensors.filesystem import FileSensor
# from airflow.contrib.sensors import HdfsSensor
# from airflow.providers.apache.hdfs.sensors import HdfsSensor
# from airflow.providers.apache.hdfs.sensors.webhdfs import WebHdfsSensor
# from airflow.operators.http_operator import SimpleHttpOperator
import os
import boto3
import pyarrow
import pyarrow.hdfs as hdfs




# hdfs_client = hdfs.connect(host='localhost', port=9000, user='ubh01')
# hdfs_file = '/user/ubh01/cloud_data/retail.csv'
# bucket = 'my-bucket-28may'
# s3_client = boto3.client(service_name='s3', \
#                          aws_access_key_id= 'AKIA2U3TXUVMACK7E7FL', \
#                          aws_secret_access_key ='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')




default_args = {'owner':'airflow', 'start_date':datetime(2023,7,5)}

file_dag = DAG(dag_id='file_transfer',default_args=default_args,schedule_interval=None, catchup=False)

# def upload_to_s3(file_path,bucket, key):
#     s3_folder = f'retail/{key}'
#     s3_client.upload_file(file_path,bucket,s3_folder)
#     print(f"The file {s3_folder} is uploaded to the S3 bucket {bucket} successfully.")


## HDFS sensor to monitor the HDFS directory:
# hdfs_monitor = WebHdfsSensor(
#     task_id = 'hdfs_monitor',
#     filepath=hdfs_path,
#     hdfs_conn_id = 'hdfs_default',
#     timeout=300,
#     dag=file_dag
# )

# csv_pattern = '*.csv'

# file_sensor_task = FileSensor(
#     task_id='file_sensor_task',
#     filepath=hdfs_path,
#     fs_conn_id='webhdfs_default',
#     # mode='reschedule',
#     poke_interval=10,  # Interval between checks in seconds
#     dag=file_dag
# )


# hdfs_file_check = SimpleHttpOperator(
#     task_id='hdfs_file_check',
#     method='HEAD',
#     http_conn_id='webhdfs_default',
#     endpoint='hdfs://localhost:9000/user/ubh01/cloud_data/',
#     response_check=lambda response: True if response.status_code == 200 else False,
#     retries=3,
#     dag=file_dag
# )

delete_command = 'hadoop fs -rm -r /user/ubh01/to_cassandra/_spark_metadata'

delete_unnecessary=BashOperator(
    task_id='delete_unnecessary',
    bash_command = delete_command,
    dag=file_dag
)


# def send_data_to_s3(hdfs_file):
#     bucket = 'my-bucket-28may'
#     s3_folder='retail'

    
#     s3_client = boto3.client(service_name='s3', \
#                          aws_access_key_id= 'AKIA2U3TXUVMACK7E7FL', \
#                          aws_secret_access_key ='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')
    
    
#     with hdfs_client.open(hdfs_file, 'rb') as f:
#         content = f.read()
        
#         s3_client.put_object(Body=content,Bucket=bucket,Key=s3_folder + '/' + hdfs_file.split('/')[-1])
        
# send_to_s3 = PythonOperator(
#     task_id='send_to_s3',
#     python_callable=send_data_to_s3,
#     op_kwargs={'hdfs_file': hdfs_file},
#     dag=file_dag,
# )


spark_command = "spark-submit --jars /home/ubh01/spark-3.0.3-bin-hadoop2.7/jars/spark-cassandra-connector-assembly_2.12-3.1.0.jar /home/ubh01/spark-cassandra.py"

spark_to_cassandra = BashOperator(
    task_id='to_cassandra',
    bash_command=spark_command,
    dag=file_dag
)

send_to_s3=BashOperator(
    task_id='send_to_s3',
    bash_command='python /home/ubh01/hdfs-s3.py',
    dag=file_dag
)


delete_command = "hadoop fs -rm -r /user/ubh01/to_cassandra/*"

delete_file = BashOperator(
    task_id='delete_file',
    bash_command=delete_command,
    dag=file_dag
)

print_success = BashOperator(
    task_id='print_sucsess',
    bash_command='echo "all tasks are successful."',
    dag=file_dag
)



delete_unnecessary >> spark_to_cassandra >> send_to_s3 >> delete_file >> print_success

# delete_unnecessary >> [hdfs_to_s3, spark_to_cassandra]
# [hdfs_to_s3, spark_to_cassandra] >> delete_file
# delete_file >> print_success
