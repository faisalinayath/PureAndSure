from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_manager.generate_db_connection_string import DbConnectionString

Base = sqlalchemy.orm.declarative_base()

class UserRegistration(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    mobile_number = Column(String, unique=True)
    full_name = Column(String)
    password = Column(String)
    date_of_registration = Column(String)
    date_of_birth = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)

    def __init__(self, mobile_number, full_name, password, date_of_registration, date_of_birth, country, state, city):
        
        self.mobile_number = mobile_number
        self.full_name = full_name
        self.password = password
        self.date_of_registration = date_of_registration
        self.date_of_birth = date_of_birth
        self.country = country
        self.state = state
        self.city = city
    
   


