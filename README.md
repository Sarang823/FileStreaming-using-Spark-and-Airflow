# FileStreaming-using-Spark-and-Airflow
In this project we have explained **"An End-To-End Architecture of E-commerce Invoice Handling Using Spark Streaming &amp; Apache Airflow."**
## Project Overview
The Spark File Streaming Project aims to process nested e-commerce invoice JSON data to per-product invoice information, and convert it into CSV format. The processed data will then be sent to two destinations: 'hive' directory (present in HDFS) for further analysis using Hive and 'cassandra' directory (present in HDFS) for storage in a Cassandra NoSQL database, as well as an AWS S3 bucket for querying using AWS Glue and Athena with visualization in AWS Quicksight.
## Architecture Diagram
Refer to the provided architecture diagram for an overview of the project's components.

![file_streaming_architecture](https://github.com/Sarang823/FileStreaming-using-Spark-and-Airflow/assets/133379507/4e3a7d24-13e4-44d0-bf22-741286e0971f)



## Problem Statement
The e-commerce invoice data received has a nested structure, and the goal is to create separate dataframes for each product associated with an invoice number. This data needs to be sent in CSV format to the 'hive' and 'cassandra' folders. Refer to the provided Nested JSON image for an example of the problem statement.

## Project Steps
### Step 1:

Set up three directories in HDFS:

**{hadoop fs -mkdir /user/ubh01/json_data}**   for raw data
**{hadoop fs -mkdir /user/ubh01/hive}** for Hive data
**{hadoop fs -mkdir /user/ubh01/cassandra}** for Cassandra data
### Step 2:

Place the JSON data into the raw directory using the command: **{hadoop fs -put invoice1.csv /user/ubh01/json_data}**

### Step 3:

Monitor the 'json_data' directory using Spark and convert the nested JSON data into simple per-product invoice JSON data. This data will be written to CSV format and sent to the 'hive' and 'cassandra' directories on HDFS.

### Flow Of Execution
#### Phase 1

The 'HDFS_Monitor.py' script is responsible for breaking the nested JSON data in the 'json_data' directory on HDFS and converting it to a simple per-product invoice JSON data, which is then written in CSV format.
#### This is our input invoice nested data in dataframe object format

![Nested_json_before](https://github.com/Sarang823/FileStreaming-using-Spark-and-Airflow/assets/133379507/f63e4fb2-f8a6-44d5-9801-fea75c059d39)



The data frame is created using the raw JSON data (Invoice1.json) by selecting the required columns and using the 'explode' function to separate each item per invoice number into a 'LineItem' column.

#### This is our exploded dataframe

![exploded_df_output](https://github.com/Sarang823/FileStreaming-using-Spark-and-Airflow/assets/133379507/f25c1d39-bb9b-46f6-b984-ffe297b5f0f6)



The 'LineItem' column is further used to extract keys as separate columns.
#### This is our final dataframe.

![final_extracted_output](https://github.com/Sarang823/FileStreaming-using-Spark-and-Airflow/assets/133379507/ee38856c-0e7d-42a6-8fb9-a5cacad28156)



The resulting DataFrame is converted to a CSV file and sent to the 'hive' and 'cassandra' directories.
## Phase 2

Before running this DAG, upload the provided .jar file to the path  **{/spark/jars/}** folder.

In this phase, data from the 'cassandra' directory is sent to a Cassandra table and an AWS S3 bucket using Apache Airflow's Directed Acyclic Graph (DAG) functionality.

First, a Cassandra keyspace and table are created. Refer to the **cassandra_commands.txt** file for that.

For createing the dag and dag code refer to the **'airflow_dag.py'** schedules four tasks:

1. Delete the **'_spark_metadata'** file created at the time of executing the **'HDFS_monitor.py'** Spark job creates a metadata file that needs to be deleted.
2. Send the CSV file from the **'cassandra'** directory to the Cassandra table using **'hdfs-to-cassandra.py'**.
3. Send the CSV file from the 'cassandra' directory to the S3 bucket using **'hdfs-to-s3.py'**.
4. Delete the CSV file from the 'cassandra' directory.
5. These tasks are executed in Apache Airflow to complete the project workflow.
