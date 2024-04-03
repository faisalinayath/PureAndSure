
import sqlalchemy
from sqlalchemy import DateTime, create_engine, ForeignKey, Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_manager.generate_db_connection_string import DbConnectionString
import datetime

Base = sqlalchemy.orm.declarative_base()

class User(Base):
    __tablename__="users"
    user_id = Column(Integer, primary_key=True)
    carts = relationship("UserCart", back_populates="user")  # Define the relationship with UserCart

class UserCart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))  # Assuming 'users' is the table name and 'user_id' is the column name
    product_id=Column(Integer)
    product_name = Column(String)
    product_price = Column(String)
    product_quantity = Column(String)
    added_to_cart_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="carts")  # Use "carts" instead of "cart"

    def __init__(self,user_id,product_id,product_name,product_price,product_quantity):
        self.user_id=user_id,
        self.product_id=product_id,
        self.product_name=product_name
        self.product_price=product_price
        self.product_quantity=product_quantity

    def __repr__(self):
        return f"< user_id={self.user_id}, product_id={self.product_id},product_name={self.product_name}, product_price={self.product_price}, product_quantity={self.product_quantity}, >"


