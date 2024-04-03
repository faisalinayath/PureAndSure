import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db_manager.db_connection import DbConnection

Base = sqlalchemy.orm.declarative_base()

class DeliveryAgentDetails(Base):
    __tablename__ = 'delivery_agent_details'

    delivery_agent_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    mobile_number = Column(String)
    address = Column(String)
    sex = Column(String)
    availability = Column(String, default="AVAILABLE")

    def __init__(self, name, mobile_number, address, sex):
        self.name = name
        self.mobile_number = mobile_number
        self.address = address
        self.sex = sex

engine = DbConnection().get_engine()
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

try:
    with Session() as session:
        print("Session created successfully")
        # Use the session object for database operations
except Exception as e:
    print(f"An error occurred: {e}")
