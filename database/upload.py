from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import pathlib

# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            password=insert_password,
            db="ece461project2",
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
            "( id SERIAL NOT NULL, name VARCHAR(255) NOT NULL, "
            "rating INT, version FLOAT NOT NULL, "
            "package_zip LONGBLOB NOT NULL, "
            "PRIMARY KEY (id));"
            )
        )
    
    db_conn.commit() # commit transaction 

# upload a new package
def upload_package(name, rating, version, package_zip):
    pool = authenticate()
    with pool.connect() as db_conn:
        # insert data into table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO packages (name, rating, version, package_zip) VALUES (:name, :rating, :version, :package_zip)",
        )

        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"name": name, "rating": rating, "version": version, "package_zip": package_zip})

        # commit transactions
        db_conn.commit()

def download_package(download_location, id):
    pool = authenticate()
    with pool.connect() as db_conn:
        # query and fetch data
        name = db_conn.execute(sqlalchemy.text("SELECT name FROM packages")).fetchall()
        rating = db_conn.execute(sqlalchemy.text("SELECT rating FROM packages")).fetchall()
        version = db_conn.execute(sqlalchemy.text("SELECT version FROM packages")).fetchall()
        package_zip = db_conn.execute(sqlalchemy.text("SELECT package_zip FROM packages")).fetchall()

        # show results
        print(name[id])
        print(rating[id])
        print(version[id])

        with open(download_location, "wb") as f:
            f.write(package_zip[id][0])

'''
name = "package1"
rating = 4
version = 1.4
package_zip = pathlib.Path("C:\\Users\joshc\Desktop\\testupload.zip").read_bytes()

#create_table()
#upload_package(name, rating, version, package_zip)
#download_package("C:\\Users\joshc\Desktop\\testupload2.zip", 0)
'''