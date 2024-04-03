
import sqlalchemy
from sqlalchemy import DateTime, create_engine, ForeignKey, Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_manager.generate_db_connection_string import DbConnectionString
import datetime

Base = sqlalchemy.orm.declarative_base()

class SuccessfullPayment(Base):
    
    __tablename__ = 'successfull_payments'
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    total_cart_amount = Column(Integer)
    user_name = Column(String)
    user_email = Column(String)
    contact_number = Column(String)
    user_address = Column(String)
    unique_razorpay_order_id = Column(String)
    razorpay_payment_id = Column(String)
    razorpay_signature = Column(String)
    razorpay_order_id_after_payment = Column(String)
    payment_made_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, total_cart_amount, user_name, user_email, contact_number,
                 user_address, unique_razorpay_order_id, razorpay_payment_id, razorpay_signature,
                 razorpay_order_id_after_payment):
        
        self.total_cart_amount = total_cart_amount
        self.user_name = user_name
        self.user_email = user_email
        self.contact_number = contact_number
        self.user_address = user_address
        self.unique_razorpay_order_id = unique_razorpay_order_id
        self.razorpay_payment_id = razorpay_payment_id
        self.razorpay_signature = razorpay_signature
        self.razorpay_order_id_after_payment = razorpay_order_id_after_payment


    def __repr__(self):
        return f"<SuccessfullPayment(payment_id={self.payment_id},  " \
               f"total_cart_amount={self.total_cart_amount}, user_name='{self.user_name}', user_email='{self.user_email}', " \
               f"contact_number='{self.contact_number}', user_address='{self.user_address}', " \
               f"unique_razorpay_order_id='{self.unique_razorpay_order_id}', " \
               f"razorpay_payment_id='{self.razorpay_payment_id}', razorpay_signature='{self.razorpay_signature}', " \
               f"razorpay_order_id_after_payment='{self.razorpay_order_id_after_payment}', )>"
