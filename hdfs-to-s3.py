from pydoop import hdfs
import boto3
hdfs_path = 'hdfs://localhost:9000/user/ubh01/to_cassandra/part-00000-7a3e8ab2-511a-449a-86e5-139f003ad19a-c000.csv'
# file=hdfs.ls(hdfs_path)
bucket = 'spark-file-streaming-project'
s3_client = boto3.client(service_name='s3', \
                         aws_access_key_id= 'AKIA54VCZWUMNFAEE2ET', \
                         aws_secret_access_key ='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')

s3_folder = 'retail/invoice.csv'
with hdfs.open(hdfs_path,'r') as f:
    content=f.read()
s3_client.put_object(Body=content,Bucket=bucket,Key=s3_folder)
print("The file is uploaded to the S3 bucket successfully.")


