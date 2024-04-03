import logging
from sqlalchemy.exc import IntegrityError

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException,status
from db_manager.db_connection import DbConnection
from models.user_cart import UserCart
from helpers.constants import Constants

class CartDao:
    def __init__(self):
        
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
                     

    def insert_into_cart_table(self, cart_item):
            try:
                
                existing_cart_item = self.session.query(UserCart).filter_by(
                            product_id=cart_item.product_id,
                            user_id=cart_item.user_id
                        ).one_or_none()                
                print(existing_cart_item)
                if existing_cart_item:
                    # Update existing item
                    current_product_quantity=float(existing_cart_item.product_quantity)
                    quantity_to_be_added=current_product_quantity+cart_item.product_quantity

                    current_product_price=float(existing_cart_item.product_price)
                    cart_item_product_price=cart_item.product_price*cart_item.product_quantity
                    price_to_be_added=current_product_price+cart_item_product_price

                    existing_cart_item.product_quantity=quantity_to_be_added
                    existing_cart_item.product_price=price_to_be_added
                    self.session.commit()
                    return status.HTTP_200_OK 
                else:
                    # Insert new item
                    product_price_final=cart_item.product_quantity*cart_item.product_price

                    cart_item_to_insert = UserCart(
                        user_id=cart_item.user_id,
                        product_id=cart_item.product_id,
                        product_name=cart_item.product_name,
                        product_price=product_price_final,
                        product_quantity=cart_item.product_quantity
                    )
                    self.session.add(cart_item_to_insert)
                    self.session.commit()
                    return status.HTTP_200_OK# Assuming you want to return a 200 OK status code

            except IntegrityError as e:
                # Handle IntegrityError separately
                # Log the error for debugging purposes
                print(f"IntegrityError: {e}")
                # Raise an HTTPException with an appropriate status code and message
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IntegrityError: Violation of database integrity constraints"
                )

            except Exception as e:
                # Log the error for debugging purposes
                print(f"Failed to insert into cart table: {e}")
                # Raise an HTTPException with an appropriate status code and message
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add to database"
                )

            finally:
                 self.session.close()

    def fetch_user_cart_contents(self, id):
        try:
            # Assuming self.session is already created and managed externally
            with self.session as session:
                cart_records = session.query(UserCart).filter_by(user_id=id).all()
                return cart_records

        except Exception as e:
            # Handle any exceptions that occur during the query
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"The following error has occurred: {e}"
            )

    def delete_cart_item(self,cart_item_id):
        try:
            with self.session as session:
                # Query for the UserCart object with the given cart_id
                cart_item = session.query(UserCart).filter_by(cart_id=cart_item_id).first()
                if cart_item:
                    # If the cart item exists, delete it from the database
                    session.delete(cart_item)
                    session.commit()
                    return f"Cart item with ID {cart_item_id} deleted successfully"
                else:
                    # Handle the case where the cart item does not exist
                    return f"Cart item with ID {cart_item_id} does not exist"
        except Exception as e:
            # Handle any exceptions that occur during the deletion
            return f"Error deleting cart item: {e}"

    def reset_cart_after_payment(self, user_id):
        try:
            with self.session as session:
                # Use a bulk delete operation to delete all cart items for the given user_id
                num_deleted = session.query(UserCart).filter_by(user_id=user_id).delete()
                
                session.commit()
                return status.HTTP_200_OK

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"The following error has occurred: {e}"
            )
