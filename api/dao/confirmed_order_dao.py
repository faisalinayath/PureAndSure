from models.confirmed_order import ConfirmedOrders
import sqlalchemy
from sqlalchemy import DateTime, create_engine, ForeignKey, Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_manager.generate_db_connection_string import DbConnectionString
import datetime
from db_manager.db_connection import DbConnection
from fastapi import HTTPException,status
from sqlalchemy.exc import SQLAlchemyError
from dao.product_info_dao import ProductInfoDao

class ConfirmedOrderDao:
    def __init__(self):
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_into_confirmed_order(self, confirm_order_obj):
        try:
            with self.session as session:
                # confirm_order_obj_details = ConfirmedOrders(
                #     user_id=confirm_order_obj.user_id,
                #     payment_id=confirm_order_obj.payment_id,
                #     product_id=confirm_order_obj.product_id,
                #     product_name=confirm_order_obj.product_name,
                #     total_product_price=confirm_order_obj.total_product_price,
                #     product_quantity=confirm_order_obj.product_quantity,
                #     deliver_to_name=confirm_order_obj.deliver_to_name,
                #     delivery_address=confirm_order_obj.delivery_address,
                #     delivery_contact_number=confirm_order_obj.delivery_contact_number
                # )

                session.add(confirm_order_obj)

                ProductInfoDao().update_quantity_left(product_id=confirm_order_obj.product_id,
                                                      quantity_ordered=confirm_order_obj.product_quantity)

                session.commit()
                return status.HTTP_200_OK

        except Exception as e:
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )

        finally:
            self.session.close()


    def fetch_all_placed_orders(self):
        try:
            with self.session as session:
                statuses = ["PENDING", "CONFIRMED", "OUT FOR DELIVERY"]
                placed_orders = session.query(ConfirmedOrders).filter(ConfirmedOrders.order_status.in_(statuses)).order_by(ConfirmedOrders.confirmed_order_id.asc()).all()
                return placed_orders
        except SQLAlchemyError as e:
                # Handle the error
                print(f"An error occurred: {e}")
                        

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )

        finally:
            self.session.close()


    def change_order_status(self,id:int,new_status:String):
        try:
            with self.session as session:
                confirmed_order_record=session.query(ConfirmedOrders).filter_by(confirmed_order_id=id).one()

                confirmed_order_record.order_status=new_status
                session.commit()

                return status.HTTP_200_OK
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )

        finally:
            self.session.close()


    async def  fetch_number_of_open_orders(self):
        try:
            with self.session as session:
                open_status_list=["PENDING","CONFIRMED","OUT FOR DELIVERY"]
                open_orders = session.query(ConfirmedOrders).filter(ConfirmedOrders.order_status.in_(open_status_list)).all()
                return len(open_orders)
        
        except SQLAlchemyError as e:
                # Handle the error
                print(f"An error occurred: {e}")
                raise e

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )
        finally:
            self.session.close()

    
    async def fetch_number_of_completed_orders(self):
        try:
            with self.session as session:
                completed_orders=session.query(ConfirmedOrders).filter_by(order_status="COMPLETED").all()
                return len(completed_orders)
        except SQLAlchemyError as se:
            raise se
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )
        finally:
            self.session.close()

    

    

    