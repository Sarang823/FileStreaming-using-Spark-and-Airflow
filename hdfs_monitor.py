from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, expr
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, ArrayType

# Define the schema for the JSON data
json_schema = StructType([
    StructField("InvoiceNumber", StringType(), nullable=False),
    StructField("CreatedTime", LongType(), nullable=False),
    StructField("StoreID", StringType(), nullable=False),
    StructField("PosID", StringType(), nullable=False),
    StructField("CashierID", StringType(), nullable=False),
    StructField("CustomerType", StringType(), nullable=False),
    StructField("CustomerCardNo", StringType(), nullable=True),
    StructField("TotalAmount", DoubleType(), nullable=False),
    StructField("NumberOfItems", LongType(), nullable=False),
    StructField("PaymentMethod", StringType(), nullable=False),
    StructField("TaxableAmount", DoubleType(), nullable=False),
    StructField("CGST", DoubleType(), nullable=False),
    StructField("SGST", DoubleType(), nullable=False),
    StructField("CESS", DoubleType(), nullable=False),
    StructField("DeliveryType", StringType(), nullable=False),
    StructField("DeliveryAddress", StructType([
        StructField("AddressLine", StringType(), nullable=True),
        StructField("City", StringType(), nullable=True),
        StructField("State", StringType(), nullable=True),
        StructField("PinCode", StringType(), nullable=True),
        StructField("ContactNumber", StringType(), nullable=True)
    ]), nullable=True),
    StructField("InvoiceLineItems", ArrayType(StructType([
        StructField("ItemCode", StringType(), nullable=False),
        StructField("ItemDescription", StringType(), nullable=True),
        StructField("ItemPrice", DoubleType(), nullable=False),
        StructField("ItemQty", LongType(), nullable=False),
        StructField("TotalValue", DoubleType(), nullable=False)
    ])), nullable=False)
])

input_path = "hdfs://localhost:9000/user/ubh01/json_data"
output_path = "hdfs://localhost:9000/user/ubh01/output_data"

spark = SparkSession.builder \
    .appName("HDFSFileStreaming") \
    .getOrCreate()

# spark = SparkSession.builder \
#   .appName("Write to S3 Example") \
#   .config("spark.hadoop.fs.s3a.access.key", "AKIA2U3TXUVMACK7E7FL") \
#   .config("spark.hadoop.fs.s3a.secret.key", "vEyHqgUy9NrogEx77oRBaL55BoX7Y0/2xVWh8vdd") \
#   .config("spark.hadoop.fs.s3a.endpoint", "https://s3.console.aws.amazon.com/s3/buckets/my-bucket-28may?region=ap-south-1&tab=objects") \
#   .getOrCreate()

# Read files from the HDFS directory
streaming_df = spark.readStream \
    .schema(json_schema) \
    .json(input_path)

## Here we are selecting those columns which we require and removing the nested structure of InvoiceLineItems column
explodeDF = streaming_df.selectExpr("InvoiceNumber", "CreatedTime","StoreID", \
                                    "PosID","CustomerType","PaymentMethod", \
                                    "DeliveryType","DeliveryAddress.City","DeliveryAddress.State", \
                                    "DeliveryAddress.PinCode","explode(InvoiceLineItems) as LineItem")

## Here we are renaming that columns which are within InvoiceLineItems columns and dropping the orginal InvoiceLineItems column
flattenDF = explodeDF \
                .withColumn("ItemCode", expr("LineItem.ItemCode")) \
                .withColumn("ItemDescription", expr("LineItem.ItemDescription")) \
                .withColumn("ItemPrice", expr("LineItem.ItemPrice")) \
                .withColumn("ItemQty", expr("LineItem.ItemQty")) \
                .withColumn("TotalValue", expr("LineItem.TotalValue")) \
                .drop("LineItem")


# Write the transformed data to 2 hdfs folders
outputPath2= "hdfs://localhost:9000/user/ubh01/cloud_data/"
query1 = flattenDF.writeStream \
    .format("csv") \
    .option("header",True) \
    .option("path", output_path) \
    .option("checkpointLocation", "hdfs://localhost:9000/user/ubh01/checkpoint/") \
    .start() 
query2 = flattenDF.writeStream \
    .format("csv") \
    .option('header',True) \
    .option("path", outputPath2) \
    .option("checkpointLocation", "hdfs://localhost:9000/user/ubh01/checkpoint/") \
    .start()


query1.awaitTermination()
query2.awaitTermination()

