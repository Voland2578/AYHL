import sqlalchemy as db
username="yfurman"
dbname="hockeystats"
databasename="{username}${dbname}".format(username=username, dbname=dbname)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=username,
    password="Voland1234",
    hostname="yfurman.mysql.pythonanywhere-services.com",
    databasename=databasename
)
try:
    engine = db.create_engine(SQLALCHEMY_DATABASE_URI)
    engine.connect()
finally:
    print("DISPOSING")
    engine.dispose()

