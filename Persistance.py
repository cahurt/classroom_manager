from datetime import datetime, date
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, mapped_column, Mapped, configure_mappers

# Create the base class for our ORM models
Base = sqlalchemy.orm.declarative_base()

# Connect to the MySQL database
connection_string = 'mysql+mysqlconnector://cahurt:Lafiel1622@localhost/classroom_manager'
engine = create_engine(connection_string)
configure_mappers()

# Create the tables if they don't exist
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# session.close()
