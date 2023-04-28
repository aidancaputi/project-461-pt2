# Import the Google Cloud client library
from google.cloud import storage
import base64
from database import databaseFunctions

def create_bucket():
    # Instantiates a client
    storage_client = storage.Client()
    # The name for the new bucket
    bucket_name = "ece461bucket"
    # Creates the new bucket
    storage_client.create_bucket(bucket_name)

def delete_bucket():
    # Instantiates a client
    storage_client = storage.Client()
    # The name for the bucket to delete
    blobs = storage_client.list_blobs('ece461bucket')
    for blob in blobs:
        blob.delete()
    bucket = storage_client.get_bucket("ece461bucket")
    # delete the bucket
    bucket.delete(force=True)

def write_blob(blob_name, content):
    bucket_name = "ece461bucket"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with blob.open("wb") as f:
        f.write(content)

def read_blob(blob_name):
    bucket_name = "ece461bucket"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with blob.open("rb") as f:
        content = f.read()
    
    return content

def delete_blob(blob_name):
    bucket_name = "ece461bucket"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    generation_match_precondition = None

    # set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)

delete_bucket()
create_bucket()

databaseFunctions.create_table()