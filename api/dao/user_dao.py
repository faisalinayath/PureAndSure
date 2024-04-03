
from http.client import UNPROCESSABLE_ENTITY
import logging
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from db_manager.db_connection import DbConnection
from models.user_registration import UserRegistration
from helpers.constants import Constants
from sqlalchemy.exc import SQLAlchemyError

class UserDao:
    def __init__(self):
        
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        

    def insert_into_table(self, user_registration_object):
        
        try:            
            user = UserRegistration(
                
                mobile_number=user_registration_object.mobile_number,
                full_name=user_registration_object.full_name,
                password=user_registration_object.password,
                date_of_registration=user_registration_object.date_of_registration,
                date_of_birth=user_registration_object.date_of_birth,
                country=user_registration_object.country,
                state=user_registration_object.state,
                city=user_registration_object.city
            )

            self.session.add(user)
            self.session.commit()

            return status.HTTP_200_OK

        except IntegrityError as e:
                # Handle IntegrityError separately
                # Log the error for debugging purposes
                print(f"IntegrityError: {e}")
                # Raise an HTTPException with an appropriate status code and message
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IntegrityError: Mobile number already exists"
                )
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Value Error: Error in the entered value."
            )

        except Exception as e:
            print(f"Failed to insert into cart table: {e}")
                # Raise an HTTPException with an appropriate status code and message
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add to database"
                )
        finally:
            self.session.close()



    def fetch_user_details_from_db(self, user_id):
            try:
                user_details = self.session.query(UserRegistration).filter_by(user_id=user_id).first()
                if user_details:
                    return {"status": "success", "user_details": user_details, "message": Constants.SUCCESSULLY_FETCHED_RECORD_FROM_TABLE}
                else:
                    return {"status": "error", "message": "User not found"}
            except Exception as e:
                return {"status": "error", "message": Constants.ERROR_FETCHING_RECORD_FROM_TABLE , "detail": str(e)}



    def update_user_record(self,user_record_to_be_updated):
        try:
            # Retrieve the user record to be updated
            user = self.session.query(UserRegistration).filter_by(user_id=user_record_to_be_updated.user_id).one()

            # Modify the attributes of the retrieved user object
            user.mobile_number = user_record_to_be_updated.mobile_number
            user.full_name = user_record_to_be_updated.full_name
            user.password = user_record_to_be_updated.password
            user.date_of_registration = user_record_to_be_updated.date_of_registration
            user.date_of_birth = user_record_to_be_updated.date_of_birth
            user.country = user_record_to_be_updated.country
            user.state = user_record_to_be_updated.state
            user.city = user_record_to_be_updated.city

            # Commit the changes to the database
            self.session.commit()

            return {"status": "success",  "message": Constants.SUCCESSULLY_UPDATED_RECORD}
        
        except IntegrityError as e:
            self.session.rollback()
            return {"status": "error", "message": "IntegrityError", "detail": str(e)}
        except Exception as e:
            return {"status": "error", "message": Constants.ERROR_FETCHING_RECORD_FROM_TABLE, "detail": str(e)}
        

    async def fetch_users_onboarded_count(self):
        try:
            with self.session as session:
                users_onboarded_count=session.query(UserRegistration).all()
                return len(users_onboarded_count)
        except SQLAlchemyError as se:
            raise HTTPException(status_code=500, detail=f"Database error: {se}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
        
