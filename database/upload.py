from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# Python Connector database creator function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            "ece-461-project-2-database:us-central1:ece-461-main-database", # Cloud SQL Instance Connection Name
            "pymysql",
            user="root",
            password=insert_password,
            db="ece461project2",
            timeout=60,
            ip_type=IPTypes.PUBLIC # public IP
        )
    return conn

# create SQLAlchemy connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# interact with Cloud SQL database using connection pool
with pool.connect() as db_conn:
    db_conn.execute(
        sqlalchemy.text(
        "CREATE TABLE IF NOT EXISTS ratings "
        "( id SERIAL NOT NULL, name VARCHAR(255) NOT NULL, "
        "origin VARCHAR(255) NOT NULL, rating FLOAT NOT NULL, "
        "PRIMARY KEY (id));"
        )
    )

    # commit transaction (SQLAlchemy v2.X.X is commit as you go)
    db_conn.commit()

    # insert data into our ratings table
    insert_stmt = sqlalchemy.text(
        "INSERT INTO ratings (name, origin, rating) VALUES (:name, :origin, :rating)",
    )

    # insert entries into table
    db_conn.execute(insert_stmt, parameters={"name": "HOTDOG", "origin": "Germany", "rating": 7.5})
    db_conn.execute(insert_stmt, parameters={"name": "BÀNH MÌ", "origin": "Vietnam", "rating": 9.1})
    db_conn.execute(insert_stmt, parameters={"name": "CROQUE MADAME", "origin": "France", "rating": 8.3})

    # commit transactions
    db_conn.commit()

    # query and fetch ratings table
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM ratings")).fetchall()

    # show results
    for row in results:
        print(row)