import datetime
import logging
from sqlalchemy.exc import IntegrityError

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException,status
from db_manager.db_connection import DbConnection
from models.user_cart import UserCart
from helpers.constants import Constants
from models.successfull_payment import SuccessfullPayment
from sqlalchemy.exc import SQLAlchemyError


class PaymentGateway:
    def __init__(self):
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_successfull_payments_to_db(self,payment_details):
        payment_obj = SuccessfullPayment(
        total_cart_amount=payment_details.total_cart_amount,
        user_name=payment_details.user_name,
        user_email=payment_details.user_email,
        contact_number=payment_details.contact_number,
        user_address=payment_details.user_address,
        unique_razorpay_order_id=payment_details.unique_razorpay_order_id,
        razorpay_payment_id=payment_details.razorpay_payment_id,
        razorpay_signature=payment_details.razorpay_signature,
        razorpay_order_id_after_payment=payment_details.razorpay_order_id_after_payment
    )
        try:

            self.session.add(payment_obj)
            self.session.commit()
            print(payment_obj.payment_id)

            return {"response":status.HTTP_200_OK,
                    "payment_id":payment_obj.payment_id            }
        
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add to database"
                )
    
    async def fetch_sales_till_date(self):
        try:
            with self.session as session:
                sales_till_date = session.query(SuccessfullPayment.total_cart_amount).all()
                sum_sales_till_date=sum([sale[0] for sale in sales_till_date])
                return sum_sales_till_date
        except SQLAlchemyError as se:
            raise se
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )
        finally:
            self.session.close()
