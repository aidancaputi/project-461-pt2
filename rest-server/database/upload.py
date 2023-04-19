from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
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
            timeout=120,
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
            "Version FLOAT NOT NULL, "
            "Zip LONGBLOB NOT NULL, "
            "PRIMARY KEY (id));"
            )
        )
    
    db_conn.commit() # commit transaction 

# upload a new package
def upload_package(name, id, version, package_zip):
    pool = authenticate()
    with pool.connect() as db_conn:
        # insert data into table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (ID, Name, Version, Zip) VALUES (:ID, :Name, :Version, :Zip)",
        )

        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"ID": id, "Name": name, "Version": version, "Zip": package_zip})

        # commit transactions
        db_conn.commit()

# download a package from its id
def download_package(id):
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        name = db_conn.execute(sqlalchemy.text("SELECT Name FROM packages")).fetchall()
        version = db_conn.execute(sqlalchemy.text("SELECT Version FROM packages")).fetchall()
        package_zip = db_conn.execute(sqlalchemy.text("SELECT package_zip FROM packages")).fetchall()

        return {version[id][0], name[id][0], id, package_zip[id][0]}

# reset database, delete all tables and go back to default state
def reset_database():
    pool = authenticate()
    with pool.connect() as db_conn:
        # delete old database
        db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS packages'))
        db_conn.commit() # commit transaction f
        
        create_table()