import os
import duckdb
import logging

s3_region = "<your region>"
s3_bucket = "<your bucket>"
s3_prefix = "<your parquet prefix>"

# set this to True to demo trying to create a secret when it already exists
demo_error = False

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger.info(f"Welcome to the DuckDB secrets demo")

logger.info(f"Setting Python variables from ACCESS_KEY and SECRET_KEY environment variables")

env_var = "ACCESS_KEY"
env_value = os.getenv(env_var)
if env_value is None:
    logger.error(f"Error: {env_var} is set to None")
    exit(1)
else:
    logger.info("S3 access key set")
    s3_access_key = env_value

env_var = "SECRET_KEY"
env_value = os.getenv(env_var)
if env_value is None:
    logger.error(f"Error: {env_var} is set to None")
    exit(1)
else:
    s3_secret_key = env_value
    logger.info("S3 secret key set")

# httpfs is autoloadable so we don't need to explicitly install and load it
# duckdb.sql("INSTALL httpfs;")
# duckdb.sql("LOAD httpfs;")

secret_name = "s3_secret"

logger.info(f"Try 1 to set DuckDB S3 secret: {secret_name}")

try:
    duckdb.sql(f"""
    CREATE SECRET {secret_name} (
        TYPE S3,
        KEY_ID '{s3_access_key}',
        SECRET '{s3_secret_key}',
        REGION '{s3_region}'
    );
    """)
except duckdb.InvalidInputException as e:
    if str(e) == f"Invalid Input Error: Temporary secret with name '{secret_name}' already exists!":
        logger.info(f"Secret: {secret_name} already exists, skipping")
    else:
        logger.error("Unknown error when creating secret in DuckDB")
        exit(1)
else:
    logger.info(f"Successfully created secret: {secret_name}")

logger.info(f"Try 2 to set DuckDB S3 secret: {secret_name}")

try:
    duckdb.sql(f"""
    CREATE SECRET {secret_name} (
        TYPE S3,
        KEY_ID '{s3_access_key}',
        SECRET '{s3_secret_key}',
        REGION '{s3_region}'
    );
    """)
except duckdb.InvalidInputException as e:
    if str(e) == f"Invalid Input Error: Temporary secret with name '{secret_name}' already exists!":
        logger.info(f"Secret: {secret_name} already exists, skipping")
    else:
        logger.error("Unknown error when creating secret in DuckDB")
        exit(1)
else:
    logger.info(f"Successfully created secret: {secret_name}")

if demo_error:
    logger.error("This will generate a runtime error, goodbye")
    duckdb.sql(f"""
    CREATE SECRET {secret_name} (
        TYPE S3,
        KEY_ID '{s3_access_key}',
        SECRET '{s3_secret_key}',
        REGION '{s3_region}'
    );
    """)
else:
    logger.info("Skipping error demo")

logger.info("Run a test query")

query_result = duckdb.sql(f"""
select
    *
from
    's3://{s3_bucket}/{s3_prefix}/*.parquet'
limit
    1
""")

logger.info(f"Query result:\n{query_result}")
