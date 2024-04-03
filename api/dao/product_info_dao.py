import datetime
import logging
from sqlalchemy.exc import IntegrityError

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException,status
from db_manager.db_connection import DbConnection
from helpers.constants import Constants
from models.successfull_payment import SuccessfullPayment
from sqlalchemy.exc import SQLAlchemyError
from models.product_info import ProductInfo

class ProductInfoDao:
    def __init__(self):
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    #to fetch the product information basically a table with six rows each specifying the product in the admin dashboard
    def fetch_product_info(self):
        try:
            with self.session as session:
                result = session.query(ProductInfo).order_by(ProductInfo.product_id.asc()).all()
                return result
        except SQLAlchemyError as se:
            self.logger.error(f"Database error: {se}")
            raise HTTPException(status_code=500, detail="Database error occurred.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    #to update the quantity offered each day[time] by the admin
    def update_available_product_quantity(self, product_id: int, quantity_to_be_updated: int) -> None:
        try:
            with self.session as session:
                result = session.query(ProductInfo).filter_by(product_id=product_id).first()
                if result is None:
                    raise ValueError(f"Product with ID {product_id} not found.")
                result.available_quantity = quantity_to_be_updated
                session.commit()
                return {"response":status.HTTP_200_OK,"message":"successfully updated the quantity" }
        except SQLAlchemyError as se:
            self.logger.error(f"Database error: {se}")
            raise HTTPException(status_code=500, detail="Database error occurred.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
    #this gets updated after susccessfull payment done by the user
    def update_quantity_left(self, product_id, quantity_ordered):
        try:
            with self.session as session:
                
                product_info = session.query(ProductInfo).filter_by(product_id=product_id).first()

                if product_info is None:
                    raise ValueError(f"Product with ID {product_id} not found")

                updated_quantity_left = product_info.available_quantity - quantity_ordered
                product_info.available_quantity = updated_quantity_left
                session.commit()
                print("successfully updated the table")
                return {"response": status.HTTP_200_OK, "message": "Successfully updated the quantity."}
                

        except SQLAlchemyError as se:
            raise HTTPException(status_code=500, detail=f"Database error occurred - {se}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred - {e}")

    #to check if the product quantity is available fr the particular ordered quantity
    def check_product_availability(self, product_id, product_quantity):
        try:
            with self.session as session:
                product_info = session.query(ProductInfo).filter_by(product_id=product_id).first()

                if product_info.available_quantity - product_quantity < 0:
                    return False
                else:
                    return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred - {e}")


        




                
