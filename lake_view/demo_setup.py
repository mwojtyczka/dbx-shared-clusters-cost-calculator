# Databricks notebook source
# MAGIC %md
# MAGIC # Run this notebook manually to setup additional sample data for the dashboard!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define output catalog and schema

# COMMAND ----------

dbutils.widgets.text("output_catalog", "main")
dbutils.widgets.text("output_schema", "billing_usage_granular")

catalog = dbutils.widgets.get("output_catalog")
schema = dbutils.widgets.get("output_schema")

catalog_and_schema = f"{catalog}.{schema}"
print(f"Use {catalog_and_schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Populate User Info table with autogenerated data

# COMMAND ----------

# Sample predefined lists of departments and cost centers
import random
from pyspark.sql.types import StructType, StructField, StringType

# Predefined department and cost center pairs
department_cost_center_pairs = [
    ("R&D", "701"),
    ("FE", "702"),
    ("PS", "703")
]

users = spark.table(f"{catalog_and_schema}.cost_agg_day").select("user_name")

# Define user_info_schema
user_info_schema = StructType(
    [
        StructField("user_name", StringType(), False),
        StructField("user_id", StringType(), False),
        StructField("display_name", StringType(), False),
        StructField("department", StringType(), False),
        StructField("cost_center", StringType(), True),
    ]
)

def create_user_info(data_df):
    user_info_list = []
    i = 0
    for row in data_df.collect():
        user_name = row["user_name"]
        user_id = i
        i = i+1
        display_name = user_name
        department, cost_center = random.choice(department_cost_center_pairs)
        user_info_list.append((user_name, user_id, display_name, department, cost_center))

    return spark.createDataFrame(user_info_list, schema=user_info_schema)

user_info_df = create_user_info(users)
user_info_df.write.mode("overwrite").saveAsTable(f"{catalog_and_schema}.user_info")

# COMMAND ----------

display(user_info_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Populate Budget

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO ${output_catalog}.${output_schema}.budget(organizational_entity_name, organizational_entity_value, dbu_cost_limit, cloud_cost_limit, currency_code, effective_start_date) VALUES
# MAGIC ("department", "R&D", 3000000, 3500000, "USD", "2024-04-01"),
# MAGIC ("department", "FE", 3000000, 3500000, "USD", "2024-04-01"),
# MAGIC ("department", "PS", 1000000, 1500000, "USD", "2024-04-01");

# COMMAND ----------

