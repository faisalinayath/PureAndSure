from .generate_db_connection_string import DbConnectionString
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class DbConnection:
    def __init__(self):
        
        connection_string = DbConnectionString().initialize_connection_string()
       
        self.engine = create_engine(connection_string)

    def get_engine(self):
        
        return self.engine
        
