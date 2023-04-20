from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import json
import os

# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            password=os.environ['DBPW'],
            db="packages_database",
            timeout=60,
            ip_type=IPTypes.PUBLIC # public IP
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
            "Content LONGBLOB, "
            "URL VARCHAR(255), "
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
        if row[3] and row[4]: # both URL and content
            package = {
                'metadata': {
                    'Name': row[1],
                    'Version': row[2],
                    'ID': row[0]
                },
                'data': {
                    'Content': row[3],
                    'URL': row[4],
                }
            }
        elif row[4]: # only URL
            package = {
                'metadata': {
                    'Name': row[1],
                    'Version': row[2],
                    'ID': row[0]
                },
                'data': {
                    'URL': row[4],
                }
            }
        else: # only content
            package = {
                'metadata': {
                    'Name': row[1],
                    'Version': row[2],
                    'ID': row[0]
                },
                'data': {
                    'Content': row[3],
                }
            }

    if package == {}: # no package found
        return 404
    return package

# PUT /package/{id}
def update_package(name, version, id, new_content, new_url):
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE ID = :id_value"), 
                                       parameters={"id_value": id})
        db_conn.commit()

        # if package exists and matches update its content
        for row in package_data:
            if row[1] == name and row[2] == version:
                db_conn.execute(sqlalchemy.text("UPDATE packages SET Content = :new_content, URL = :new_URL WHERE ID = :id"), 
                                parameters={"new_content": new_content, "new_URL": new_url, "id": id})
                db_conn.commit()
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
            pool.dispose()
            return 200 # package is deleted
    pool.dispose() # dispose connection

    return 404 # matching package not found

# POST /package
def upload_package(name, version, id, content, url):
    pool = authenticate()
    with pool.connect() as db_conn:
        # search for package by content
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE Content = :content"), 
                                       parameters={"content": content})
        db_conn.commit()
        for row in package_data:
            pool.dispose()
            return 409 # package exists with same content
        
        # search for package by URL
        package_data = db_conn.execute(sqlalchemy.text("SELECT * FROM packages WHERE URL = :url"), 
                                       parameters={"url": url})
        db_conn.commit()
        for row in package_data:
            pool.dispose()
            return 409 # package exists with same URL
        
        # insert data into table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (ID, Name, Version, Content, URL) VALUES (:ID, :Name, :Version, :Content, :URL)",)

        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"ID": id, "Name": name, "Version": version, "Content": content, "URL": url})
        
        db_conn.commit() # commit transactions
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
            }
        }
    elif url: # only URL
        package = {
            'metadata': {
                'Name': name,
                'Version': version,
                'ID': id
            },
            'data': {
                'URL': url,
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
            }
        }

    return package

'''
reset_database()
upload_package("NewPackage", "1.2.3", "newpackage", None, "testurl")
upload_package("AidanCaputi", "1.2.4", "aidancaputi", "testcontent", None)
upload_package("Zane", "1.2.5", "zane", "bothcontent", "bothurl")
'''