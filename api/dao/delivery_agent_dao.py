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
from models.delivery_agent_details import DeliveryAgentDetails
import requests
from datetime import datetime

class DeliveryAgentDao:
    def __init__(self):
        engine = DbConnection().get_engine()
        self.engine = engine

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    #to onboard new delivery agents 
    def add_new_delivery_partner(self, delivery_agent_details):
        try:
            with self.session as session:
                delivery_agent_details_object = DeliveryAgentDetails(
                    name=delivery_agent_details.name,
                    mobile_number=delivery_agent_details.mobile_number,
                    address=delivery_agent_details.address,
                    sex=delivery_agent_details.sex
                )

                session.add(delivery_agent_details_object)
                session.commit()
                return status.HTTP_200_OK
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to database: {e}"
            )

    #to fetch the details of all the onboarded delivery agents details
    def fetch_delivery_agents_info(self):
        try:
            with self.session as session:
                delivery_agents = session.query(DeliveryAgentDetails).all()
                return delivery_agents
        except Exception as e:
            return str(e)  # Convert the exception to a string for return

    def calculate_delivery_cost(self, distance):
            """Calculate the cost of delivery based on the distance."""
            base_delivery_charges = 40  # for initial 4 kms
            delivery_charge_per_km = 10

            total_charge = base_delivery_charges + max(0, (distance - 4)) * delivery_charge_per_km
            print(f"Delivery charge for {distance} km is {total_charge}")
            return total_charge

    def calculate_delivery_distance(self, destinations):
        """Calculate the delivery distance between the warehouse and the destination."""
        api_key = "Arqv7qEYQddR1P_UsOxb9JD80QfZdRQSWmIyYZuBETFsZWmS2tjHVSxhl9cnRhqi"
        origins = [{"latitude": 13.0011956, "longitude": 77.5963159}]  # the geolocation of the warehouse
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

        url = f"https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?key={api_key}"
        headers = {"Content-Type": "application/json"}

        data = {
            "origins": origins,
            "destinations": destinations,
            "travelMode": "driving",
            "startTime": current_time,
            "timeUnit": "minute"
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            response_data = response.json()
            travel_distance = response_data["resourceSets"][0]["resources"][0]["results"][0]["travelDistance"]

            total_delivery_cost = self.calculate_delivery_cost(distance=travel_distance)
            return total_delivery_cost
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during API request: {e}"
            )
        