import datetime
import sqlalchemy
from sqlalchemy import DateTime, create_engine, ForeignKey, Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_manager.generate_db_connection_string import DbConnectionString
import datetime
Base = sqlalchemy.orm.declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    confirmed_orders = relationship("ConfirmedOrders", back_populates="user")

class Product(Base):
    __tablename__ = "product_info"
    product_id = Column(Integer, primary_key=True)
    confirmed_orders = relationship("ConfirmedOrders", back_populates="product")

class Payment(Base):
    __tablename__ = "successfull_payments"
    payment_id = Column(Integer, primary_key=True)
    confirmed_orders = relationship("ConfirmedOrders", back_populates="payment")

class ConfirmedOrders(Base):
    __tablename__ = 'confirmedorders'

    confirmed_order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    payment_id = Column(Integer, ForeignKey('successfull_payments.payment_id'))
    product_id = Column(Integer, ForeignKey('product_info.product_id'))
    product_name = Column(String)
    total_product_price = Column(Integer)
    product_quantity = Column(String)
    deliver_to_name = Column(String)
    delivery_address = Column(String)
    delivery_contact_number = Column(String)
    order_places_at = Column(DateTime, default=datetime.datetime.utcnow)
    order_status = Column(String, default="PENDING")

    user = relationship("User", back_populates="confirmed_orders")
    product = relationship("Product", back_populates="confirmed_orders")
    payment = relationship("Payment", back_populates="confirmed_orders")




    def __init__(self,user_id,payment_id,product_id,product_name,total_product_price,
                 product_quantity,deliver_to_name,delivery_address,delivery_contact_number):
        self.user_id = user_id
        self.payment_id = payment_id
        self.product_id = product_id
        self.product_name = product_name
        self.total_product_price = total_product_price
        self.product_quantity = product_quantity
        self.deliver_to_name = deliver_to_name
        self.delivery_address = delivery_address
        self.delivery_contact_number = delivery_contact_number
        




