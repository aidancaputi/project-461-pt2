from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import json
import time
from sqlalchemy.exc import OperationalError

# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            password='461isSUPERcool!',
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
    print('authenticated')
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
            "Zip LONGBLOB, "
            "PRIMARY KEY (id));"
            )
        )

        db_conn.commit() # commit transaction 
    pool.dispose() # dispose connection

# upload a new package
def upload_package(name, version, package_zip):
    pool = authenticate()
    with pool.connect() as db_conn:
        # create new ID for package
        id, extranums = '', ''
        for x in range(len(name)):
            if (name[x].isupper()):
                extranums = extranums + str(x)
                id = id + name[x].lower()
            else:
                id = id + name[x]
        id = id + extranums

        # insert data into table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (ID, Name, Version, Zip) VALUES (:ID, :Name, :Version, :Zip)",)

        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"ID": id, "Name": name, "Version": version, "Zip": package_zip})
        
        db_conn.commit() # commit transactions
    pool.dispose() # dispose connection

# download a package from its id
def download_package(id):
    pool = authenticate()
    retries = 3
    for i in range(retries):
        try:
            with pool.connect() as db_conn:
                # query and fetch data
                name = db_conn.execute(sqlalchemy.text("SELECT Name FROM packages")).fetchall()
                version = db_conn.execute(sqlalchemy.text("SELECT Version FROM packages")).fetchall()
                package_zip = db_conn.execute(sqlalchemy.text("SELECT package_zip FROM packages")).fetchall()
    
            pool.dispose() # dispose connection
        except OperationalError as e:
            if i < retries - 1:
                print(f'Error connecting to database: {str(e)}. Retrying in 5 seconds...')
                time.sleep(5)
            else:
                raise e

    return {version[id][0], name[id][0], id, package_zip[id][0]}

# reset database, delete all tables and go back to default state
def reset_database():
    pool = authenticate()
    with pool.connect() as db_conn:
        # delete old database
        db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS packages'))

        db_conn.commit() # commit transaction 
    pool.dispose() # dispose connection

    create_table()

def get_all_packages():
    pool = authenticate()
    with pool.connect() as db_conn:
        print('fetching packages')
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

'''
reset_database()
upload_package("NewPackage", "1.2.3", None)
upload_package("AidanCaputi", "1.2.4", None)
upload_package("Zane", "1.2.5", None)
result = get_all_packages()
downloaded = download_package('zane0')
print(downloaded)
print(result)
'''
