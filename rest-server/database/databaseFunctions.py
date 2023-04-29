from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import storage
from datetime import datetime
import sqlalchemy
import json
import os
import base64

# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            password='461isSUPERcool!', # os.environ['DBPW']
            db="packages_database", # database name
            timeout=60,
            ip_type=IPTypes.PUBLIC, # public IP
        )
    return conn

# create SQLAlchemy connection pool
def authenticate():
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

# establish table formats
def create_table():
    pool = authenticate()
    with pool.connect() as db_conn:
        db_conn.execute(
            # create packages table
            sqlalchemy.text(
            "CREATE TABLE IF NOT EXISTS packages "
            "(ID VARCHAR(255) NOT NULL, "
            "Name VARCHAR(255) NOT NULL, "
            "Version VARCHAR(255) NOT NULL, "
            "URL VARCHAR(255), "
            "JSProgram MEDIUMTEXT NOT NULL, "
            "ContentHash VARCHAR(255), "
            "PRIMARY KEY (id));"
            )
        )
        db_conn.commit()

        # create package history table
        db_conn.execute(
            sqlalchemy.text(
            "CREATE TABLE IF NOT EXISTS package_versions "
            "(ID VARCHAR(255) NOT NULL, "
            "Name VARCHAR(255) NOT NULL, "
            "Version VARCHAR(255) NOT NULL, "
            "Date VARCHAR(255) NOT NULL, "
            "Action VARCHAR(255) NOT NULL, "
            "PRIMARY KEY (Date));"
            )
        )
        db_conn.commit()


# POST /packages
def get_all_packages():
    pool = authenticate()
    with pool.connect() as db_conn:
        # get all packages from packages table
        result = db_conn.execute(sqlalchemy.text('SELECT Version, Name, ID FROM packages')).fetchall()
        db_conn.commit()

    # convert the results to a list of dictionaries
    packages = []
    for row in result:
        package = {
            'Version': row[0],
            'Name': row[1],
            'ID': row[2]
        }
        packages.append(package)

    return json.dumps(packages) # convert the list of dictionaries to JSON format and return it

# DELETE /reset
def reset_database():
    pool = authenticate()
    with pool.connect() as db_conn:
        db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS packages')) # delete old packages table
        db_conn.commit()

        db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS package_versions')) # delete old package history table
        db_conn.commit() # commit transaction 

    delete_bucket() # delete old content bucket
    create_bucket() # create new content bucket
    create_table() # create new tables

    return 200

# GET /package/{id}
def get_package(id):
    pool = authenticate()
    with pool.connect() as db_conn:
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id}) # search for packages with matching ID
        db_conn.commit()

        package = {}
        for row in package_data:
            if row[3]: # URL and content
                content = read_blob(id) # get content from bucket
                content_str = chopString(content) # truncate content as needed
                # build package JSON
                package = {
                    'metadata': {
                        'Name': row[1],
                        'Version': row[2],
                        'ID': row[0]
                    },
                    'data': {
                        'Content': content_str,
                        'URL': row[3],
                        'JSProgram': row[4]
                    }
                }
            else: # only content
                content = read_blob(id)
                content_str = chopString(content)
                package = {
                    'metadata': {
                        'Name': row[1],
                        'Version': row[2],
                        'ID': row[0]
                    },
                    'data': {
                        'Content': content_str,
                        'JSProgram': row[4]
                    }
                }
            
            # update package version history with a new download entry
            insert_stmt = sqlalchemy.text(
                "INSERT INTO package_versions (ID, Name, Version, Date, Action) VALUES (:ID, :Name, :Version, :Date, :Action)",)
            dateTime = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ") # get current date and time
            db_conn.execute(insert_stmt, parameters={"ID": id, "Name": row[1], "Version": row[2], "Date": dateTime, "Action": "DOWNLOAD"})
            db_conn.commit() # commit transactions

    if package == {}: # no package found
        return 404
    return package

# PUT /package/{id}
def update_package(name, version, id, new_content, new_url, new_jsprogram):
    pool = authenticate()
    with pool.connect() as db_conn:
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id}) # search for packages with matching ID
        db_conn.commit()

        # if package exists and matches name and version, update it
        for row in package_data:
            if row[1] == name and row[2] == version:
                new_hash = hash(new_content) # calculate new hash
                db_conn.execute(sqlalchemy.text("UPDATE packages SET URL = :new_URL, JSProgram = :new_JSProgram, ContentHash = :new_hash WHERE ID = :id"), 
                                parameters={"new_URL": new_url, "new_JSProgram": new_jsprogram, "new_hash": new_hash, "id": id})
                db_conn.commit()

                # update content bucket
                delete_blob(id)
                write_blob(id, new_content)

                # update package version history with a new download entry
                insert_stmt = sqlalchemy.text(
                    "INSERT INTO package_versions (ID, Name, Version, Date, Action) VALUES (:ID, :Name, :Version, :Date, :Action)",)
                dateTime = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ") # get current date and time
                db_conn.execute(insert_stmt, parameters={"ID": id, "Name": name, "Version": version, "Date": dateTime, "Action": "UPDATE"})
                db_conn.commit()
                pool.dispose()

                return 200

    return 404 # matching package not found

# DELETE /package/{id}
def delete_package(id):
    pool = authenticate()
    with pool.connect() as db_conn:
        print("deleting package with id " + id)
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id}) # search for packages with matching ID
        db_conn.commit()
        for row in package_data:
            db_conn.execute(sqlalchemy.text("DELETE FROM packages WHERE ID = :id_value"), 
                                        parameters={"id_value": id}) # delete said matching package
            db_conn.commit()

            delete_blob(id) # delete content

            # update package version history with a new download entry
            insert_stmt = sqlalchemy.text(
                "INSERT INTO package_versions (ID, Name, Version, Date, Action) VALUES (:ID, :Name, :Version, :Date, :Action)",)
            dateTime = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ") # get current date and time
            db_conn.execute(insert_stmt, parameters={"ID": id, "Name": row[1], "Version": row[2], "Date": dateTime, "Action": "DELETE"})
            db_conn.commit()
            pool.dispose()
            
            return 200 # package is deleted

    return 404 # matching package not found

# POST /package
def upload_package(name, version, content, url, jsprogram):
    pool = authenticate()
    with pool.connect() as db_conn:
        print('searching for exisiting package with same URL/content')
        contentHash = hash(content) # calculate hash for each package based on its content
        
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ContentHash = :contenthash"), 
                                       parameters={"contenthash": contentHash}) # search for package by content hash
        db_conn.commit()

        for row in package_data:
            pool.dispose()
            print('package content already existed')
            return 409 # package exists with same content
        
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE URL = :url"), 
                                       parameters={"url": url}) # search for package by URL
        db_conn.commit()

        for row in package_data:
            pool.dispose()
            print('package url already existed')
            return 409 # package exists with same URL
        
        # new package will be uploaded, create new ID for package
        print('uploading a new package')
        new_id = name + version

        # insert data into table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (ID, Name, Version, URL, JSProgram, ContentHash) VALUES (:ID, :Name, :Version, :URL, :JSProgram, :ContentHash)",)
        db_conn.execute(insert_stmt, parameters={"ID": new_id, "Name": name, "Version": version, "URL": url, "JSProgram": jsprogram, "ContentHash": contentHash})
        db_conn.commit()
        write_blob(new_id, content) # create new blob for content

        # update package version history with a new download entry
        insert_stmt = sqlalchemy.text(
            "INSERT INTO package_versions (ID, Name, Version, Date, Action) VALUES (:ID, :Name, :Version, :Date, :Action)",)
        dateTime = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ") # get current date and time
        db_conn.execute(insert_stmt, parameters={"ID": new_id, "Name": name, "Version": version, "Date": dateTime, "Action": "CREATE"})
        db_conn.commit()

    # build response JSON
    package = {}
    content_str = chopString(content)
    if content and url: # both URL and content
        package = {
            'metadata': {
                'Name': name,
                'Version': version,
                'ID': new_id
            },
            'data': {
                'Content': content_str,
                'URL': url,
                'JSProgram': jsprogram
            }
        }
    else: # only content
        package = {
            'metadata': {
                'Name': name,
                'Version': version,
                'ID': new_id
            },
            'data': {
                'Content': content_str,
                'JSProrgam': jsprogram
            }
        }

    return package

# GET /package/byName/{name}
def get_package_history(name):
    pool = authenticate()
    with pool.connect() as db_conn:
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM package_versions WHERE Name = :name_value"), 
                                       parameters={"name_value": name}) # search for package version history
        db_conn.commit()

        package_versions = [] # build response with all package version histories
        for row in package_data:
            package = {
                "Date": row[3],
                "PackageMetadata": {
                    "Name": row[1],
                    "Version": row[2],
                    "ID": row[0]
                },
                "Action": row[4]
            }
            package_versions.insert(0, package) # insert at beginning of list

    if package_versions == []:
        return 404  # no package found return 404
    
    return json.dumps(package_versions) # convert the list of dictionaries to JSON format and return it

# DELETE /package/byName/{name}
def delete_history(name):
    pool = authenticate()
    with pool.connect() as db_conn:
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM package_versions WHERE Name = :name_value"), 
                                       parameters={"name_value": name}) # search for package version history
        db_conn.commit()

        package_found = 0 # flag for if a package history is found
        for row in package_data:
            delete_package(row[0]) # delete package from database

            db_conn.execute(sqlalchemy.text("DELETE FROM package_versions WHERE ID = :id_value"), 
                                        parameters={"id_value": row[0]}) # delete package
            db_conn.commit()
            package_found = 1 # package history is found, set flag
        
        if package_found:
            return 200 # package history is deleted
    
    pool.dispose()
    return 404 # package does not exist

# function for truncating extra characters off of content, so as to not return content too big
def chopString(data):
    if len(data) > 32000000-100: # max of ~32 MB
        content_str = str(data[:3000000])
    else:
        content_str =  str(data)
    
    return content_str
    
# create a new bucket for content storage
def create_bucket():
    storage_client = storage.Client() # instantiates a client
    storage_client.create_bucket("ece461bucket") # creates the new bucket

# delete a bucket 
def delete_bucket():
    storage_client = storage.Client() # instantiates a client
    blobs = storage_client.list_blobs("ece461bucket") # get list of all blobs
    for blob in blobs:
        blob.delete() # delete each blob
    bucket = storage_client.get_bucket("ece461bucket") # get the bucket itself
    bucket.delete(force=True) # delete the bucket

# create a new blob for a new package's content
def write_blob(blob_name, content):
    try: # encode the content if possible
        content = content.encode()
    except:
        pass
    storage_client = storage.Client() # instantiates a client
    bucket = storage_client.bucket("ece461bucket")
    blob = bucket.blob(blob_name)

    with blob.open("wb") as f:
        f.write(content) # write content to the blob

# read content from a blob
def read_blob(blob_name):
    storage_client = storage.Client() # instantiates a client
    bucket = storage_client.bucket("ece461bucket")
    blob = bucket.blob(blob_name)

    with blob.open("rb") as f:
        content = f.read() # read content from the blob
    
    return content

# delete a blob and its content
def delete_blob(blob_name):
    storage_client = storage.Client() # instantiates a client
    bucket = storage_client.bucket("ece461bucket")
    blob = bucket.blob(blob_name) 
    generation_match_precondition = None

    # set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match the precondition
    blob.reload()  # fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition) # delete blob