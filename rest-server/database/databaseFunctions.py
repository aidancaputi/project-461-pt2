from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import json
import bucketFunctions
import base64
import os
# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            #password=os.environ['DBPW'],
            password='461isSUPERcool!',
            db="packages_database",
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

# establish table format
def create_table():
    pool = authenticate()
    with pool.connect() as db_conn:
        db_conn.execute(
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

        db_conn.commit() # commit transaction 
    pool.dispose() # dispose connection


# POST /packages
def get_all_packages():
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        result = db_conn.execute(sqlalchemy.text('SELECT Version, Name, ID FROM packages')).fetchall()
        db_conn.commit() # commit transaction 

    # convert the results to a list of dictionaries
    packages = []
    for row in result:
        package = {
            'Version': row[0],
            'Name': row[1],
            'ID': row[2]
        }
        packages.append(package)
    pool.dispose() # dispose connection
    return json.dumps(packages) # convert the list of dictionaries to JSON format and return it

# DELETE /reset
def reset_database():
    pool = authenticate()
    with pool.connect() as db_conn:
        # delete old database
        db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS packages'))

        db_conn.commit() # commit transaction 
    pool.dispose() # dispose connection

    # reset content buckets
    bucketFunctions.delete_bucket()
    bucketFunctions.create_bucket()

    create_table()

    return 200

# GET /package/{id}
def get_package(id):
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id})
        db_conn.commit()
    pool.dispose() # dispose connection

    package = {}
    for row in package_data:
        if row[4]: # URL
            content = bucketFunctions.read_blob(id)
            package = {
                'metadata': {
                    'Name': row[1],
                    'Version': row[2],
                    'ID': row[0]
                },
                'data': {
                    'Content': content,
                    'URL': row[4],
                    'JSProgram': row[5]
                }
            }
        else: # only content
            content = bucketFunctions.read_blob(id)
            package = {
                'metadata': {
                    'Name': row[1],
                    'Version': row[2],
                    'ID': row[0]
                },
                'data': {
                    'Content': content,
                    'JSProgram': row[5]
                }
            }

    if package == {}: # no package found
        return 404
    return package

# PUT /package/{id}
def update_package(name, version, id, new_content, new_url, new_jsprogram):
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id})
        db_conn.commit()

        # if package exists and matches update its content and hash
        for row in package_data:
            if row[1] == name and row[2] == version:
                new_hash = hash(new_content) # calculate new hash
                db_conn.execute(sqlalchemy.text("UPDATE packages SET URL = :new_URL, JSProgram = :new_JSProgram, ContentHash = :new_hash WHERE ID = :id"), 
                                parameters={"new_URL": new_url, "new_JSProgram": new_jsprogram, "new_hash": new_hash, "id": id})
                db_conn.commit()
                # update content bucket
                bucketFunctions.delete_blob(id)
                bucketFunctions.write_blob(id)
                pool.dispose()
                return 200
            
    pool.dispose() # dispose connection

    return 404 # matching package not found

# DELETE /package/{id}
def delete_package(id):
    pool = authenticate()
    with pool.connect() as db_conn:
        # search for package
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id})
        db_conn.commit()
        for row in package_data:
            # delete package
            db_conn.execute(sqlalchemy.text("DELETE FROM packages WHERE ID = :id_value"), 
                                        parameters={"id_value": id})
            db_conn.commit()
            bucketFunctions.delete_blob(id) # delete content
            pool.dispose()
            return 200 # package is deleted
    pool.dispose() # dispose connection

    return 404 # matching package not found

# POST /package
def upload_package(name, version, content, url, jsprogram):
    pool = authenticate()
    print('authenticated')
    with pool.connect() as db_conn:
        print('searching')
         # calculate hash for each package based on its content
        contentHash = hash(content)
        
        # search for package by content hash
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ContentHash = :contenthash"), 
                                       parameters={"contenthash": contentHash})
        print('search success 1')
        db_conn.commit()
        print('commit success 1')
        for row in package_data:
            pool.dispose()
            print('package content already existed')
            return 409 # package exists with same content
        print('package content didnt exist already')
        # search for package by URL
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE URL = :url"), 
                                       parameters={"url": url})
        print('search success 2')
        db_conn.commit()
        print('commit success 2')
        for row in package_data:
            pool.dispose()
            print('package url already existed')
            return 409 # package exists with same URL
        
        # new package will be uploaded
        # create new ID for package
        print('uploading a new package')
        id, extranums = '', ''
        for x in range(len(name)):
            if (name[x].isupper()):
                extranums = extranums + str(x)
                id = id + name[x].lower()
            else:
                id = id + name[x]
        id = id + extranums

        # insert data into table
        print('about to insert data into table')
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (ID, Name, Version, URL, JSProgram, ContentHash) VALUES (:ID, :Name, :Version, :URL, :JSProgram, :ContentHash)",)

        print('inserted')
        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"ID": id, "Name": name, "Version": version, "URL": url, "JSProgram": jsprogram, "ContentHash": contentHash})
        
        db_conn.commit() # commit transactions
        bucketFunctions.write_blob(id, content)

        print('finish up')
    pool.dispose() # dispose connection

    # build response JSON
    package = {}
    if content and url: # both URL and content
        package = {
            'metadata': {
                'Name': name,
                'Version': version,
                'ID': id
            },
            'data': {
                'Content': content,
                'URL': id,
                'JSProgram': jsprogram
            }
        }
    else: # only content
        package = {
            'metadata': {
                'Name': name,
                'Version': version,
                'ID': id
            },
            'data': {
                'Content': content,
                'JSProrgam': jsprogram
            }
        }

    print('returning')
    return package

'''
with open("test_zips/cloudinary_npm-master.zip", "rb") as file1:
    encoded_cloudinary = base64.b64encode(file1.read())
with open("test_zips/axios-1.x.zip", "rb") as file2:
    encoded_axios = base64.b64encode(file2.read())

reset_database()
upload_package("NewPackage", "1.2.3", encoded_cloudinary, "testurl", "jsscript is super cool")
upload_package("AidanCaputi", "1.2.4", encoded_axios, None, "this jsscript is useless")
#upload_package("Zane", "1.2.5", content3, "bothurl", "maybe this jssript does something")

result = get_package('zane0')
print(result)

upload_package("lodash", "1.2.5", encoded_cloudinary, None, "jsscript")
print(get_all_packages())
'''