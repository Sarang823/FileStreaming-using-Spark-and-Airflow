from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, expr
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, ArrayType, IntegerType, FloatType
from pyspark.sql.functions import row_number
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("spark-to-cassandra") \
    .getOrCreate()

schema = StructType([
  StructField("InvoiceNumber", IntegerType(), True),
  StructField("CreatedTime", LongType(), True),
  StructField("StoreID", StringType(), True),
  StructField("PosID", StringType(), True),
  StructField("CustomerType", StringType(), True),
  StructField("PaymentMethod", StringType(), True),
  StructField("DeliveryType", StringType(), True),
  StructField("City", StringType(), True),
  StructField("State", StringType(), True),
  StructField("PinCode", IntegerType(), True),
  StructField("ItemCode", IntegerType(), True),
  StructField("ItemDescription", StringType(), True),
  StructField("ItemPrice", FloatType(), True),
  StructField("ItemQty", IntegerType(), True),
  StructField("TotalValue", FloatType(), True)
])

input_path = "hdfs://localhost:9000/user/ubh01/to_cassandra/"
output_path="hdfs://localhost:9000/user/ubh01/demo/"

df = spark.read \
    .format('csv') \
    .option('header', True) \
    .schema(schema) \
    .option('path',input_path) \
    .load()

windowSpec = Window.orderBy('InvoiceNumber')
spark_df = df.withColumn("cust_id", row_number().over(windowSpec) + 100)


spark_df1 = spark_df.toDF("invoicenumber", "createdtime", "storeid", "posid", "customertype", "paymentmethod", "deliverytype", "city", "state", "pincode", "itemcode", "itemdescription", "itemprice", "itemqty", "totalvalue", "cust_id")

spark_df2 = spark_df1.selectExpr("invoicenumber", "createdtime", "storeid", "posid", "customertype", "paymentmethod", "deliverytype", "city", "state", "pincode", "itemcode", "itemdescription", "itemprice", "itemqty", "totalvalue", "cust_id")

spark_df2.write \
    .format("org.apache.spark.sql.cassandra") \
    .option("spark.cassandra.connection.host", "127.0.0.1") \
    .option("spark.cassandra.connection.port", "9042") \
    .options(table="retail", keyspace="files") \
    .mode("append") \
    .save()


