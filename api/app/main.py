import asyncio
from decimal import Decimal
import uuid
from fastapi import FastAPI, HTTPException,status
from models.confirmed_order import ConfirmedOrders
from pydantic import BaseModel
from models.user_registration import UserRegistration
from dao.user_dao import UserDao
from dao.user_cart_dao import CartDao
import razorpay
import hmac
import hashlib
from dao.payment_gateway_dao import PaymentGateway
from dao.confirmed_order_dao import ConfirmedOrderDao
from dao.delivery_agent_dao import DeliveryAgentDao
from dao.product_info_dao import ProductInfoDao
from typing import List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

import logging


#logging.basicConfig(level=logging.DEBUG)                    #to set debugging level

logging.basicConfig(filename='admin.log',
                    level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()


class UserRegistrationRequest(BaseModel):
    
    mobile_number: str
    full_name: str
    password:str
    date_of_registration: str
    date_of_birth: str
    country: str
    state: str
    city: str

class UserUpdate(BaseModel):
    user_id:int
    mobile_number: str
    full_name: str
    password:str
    date_of_registration: str
    date_of_birth: str
    country: str
    state: str
    city: str

@app.post("/user/register/")
async def user_registration(user_registration: UserRegistrationRequest):
    try:  
        response = UserDao().insert_into_table(user_registration)  
        return {"response": response}
    except HTTPException as http_exception:
        # Catch HTTP exceptions raised by the CartDao and re-raise them
        raise http_exception
    except Exception as e:
        # Catch any other exceptions raised by the CartDao and raise an internal server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

   

@app.get("/user/{user_id}")
async def fetch_user_details(user_id:int):
    user_details=UserDao().fetch_user_details_from_db(user_id)
    return {"response":user_details}


@app.put("/user/update_user_information/")
async def update_user_information(user_data:UserUpdate):
    response=UserDao().update_user_record(user_data)
    return {"response":response}



class CartItems(BaseModel):
    user_id: int
    product_id: int
    product_name: str
    product_price: int
    product_quantity: float

@app.post("/user/add_to_cart/")
async def add_product_to_cart(cart_items: CartItems):
    try:
        product_info_dao = ProductInfoDao()
        cart_dao = CartDao()

        # Check product availability
        if product_info_dao.check_product_availability(product_id=cart_items.product_id,
                                                       product_quantity=cart_items.product_quantity):
            # Insert into cart table
            response_status = cart_dao.insert_into_cart_table(cart_item=cart_items)
            print("Successfully inserted into table")

            return {"status":200,"response": "Successfully inserted to cart but failed to update product quantity left"}

        return {"status":404,"response": "Product not available"}
    except HTTPException as http_exception:
        # Catch HTTP exceptions raised by the CartDao and re-raise them
        print(http_exception)
        raise http_exception
    except Exception as e:
        # Catch any other exceptions raised by the CartDao and raise an internal server error
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

  

@app.get("/user/fetch_user_cart/{user_id}")
async def fetch_user_cart(user_id:int):
    try:
        cart_records=CartDao().fetch_user_cart_contents(user_id)
        return {"response":cart_records}
    
    except HTTPException as http_exception:
        return http_exception
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
        
@app.delete("/user/delete_cart_item/{cart_item_id}")
async def delete_cart_item(cart_item_id:int):
    try:
        response=CartDao().delete_cart_item(cart_item_id)
        return {"response":response}
    
    except HTTPException as http_exception:
        return http_exception
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
    
@app.delete("/user/reset_cart_after_payment/{user_id}")
async def reset_cart(user_id:int):
    try:
        response=CartDao().reset_cart_after_payment(user_id=user_id)
        return {"response":response}
    
    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )


#----------------------------------------------------------------------------------------------------------
                                #payment gateway


@app.post("/generate_order_id/{total_cart_value}")
async def generate_order_id(total_cart_value:int):
    global payment
    
    client = razorpay.Client(auth=("rzp_test_OC0LcZTmw2iTmg", "pOrc43kX8xyBUckCRq6BuqgZ"))

    receipt_id = str(uuid.uuid4())
    data = { "amount": total_cart_value*100, "currency": "INR", "receipt": receipt_id }
    payment = client.order.create(data=data)
    return {"response":payment}

class UserCartItems(BaseModel):
    product_id:int
    product_price:float
    product_name :str
    cart_id :int
    user_id :int
    product_quantity:float


class PaymentSignature(BaseModel):

    total_cart_amount:str
    user_name:str
    user_email:str
    contact_number:str
    user_address:str
    unique_razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    razorpay_order_id_after_payment:str
    user_cart_items_to_payment_gateway:List[UserCartItems]

@app.post("/verify_payment_signature/")
async def verify_payment_signature(payment_signature: PaymentSignature):
    
    
    razorpay_secret="pOrc43kX8xyBUckCRq6BuqgZ"

    # Define the hmac_sha256 function
    def hmac_sha256(data, key):
        return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()

    # Calculate the HMAC-SHA256 signature
    generated_signature = hmac_sha256(payment_signature.unique_razorpay_order_id + "|" + payment_signature.razorpay_payment_id, razorpay_secret)

    # Compare the generated signature with the provided signature
    if generated_signature == payment_signature.razorpay_signature:
        try:
            response=PaymentGateway().insert_successfull_payments_to_db(payment_signature)
            payment_id=response["payment_id"]
            
            user_id=None

            for individual_product in payment_signature.user_cart_items_to_payment_gateway:
                
                confirm_order_obj = ConfirmedOrders(
                    user_id=individual_product.user_id,
                    payment_id=payment_id,
                    product_id=individual_product.product_id,
                    product_name=individual_product.product_name,
                    total_product_price=float(payment_signature.total_cart_amount),
                    product_quantity=float(individual_product.product_quantity),
                    deliver_to_name=payment_signature.user_name,
                    delivery_address=payment_signature.user_address,
                    delivery_contact_number=payment_signature.contact_number
                )
                user_id=individual_product.user_id
                final_response=ConfirmedOrderDao().insert_into_confirmed_order(confirm_order_obj)
                
            #reset the cart after processing all the orders
            response=CartDao().reset_cart_after_payment(user_id=user_id)

            return {"response":"successfully inserted into all the table"}


        except HTTPException as http_exception: 
            print(http_exception)    
            raise http_exception
        except Exception as e:
            print(e)
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
            )

    else:
        return {"response":"False"}


#------------------------------------- ADMIN ------------------------------------------------------------------
    
@app.get("/admin/get_all_current_orders")
async def fetch_all_placed_orders():
    try:
        logging.info("orders being fetched")
        active_orders=ConfirmedOrderDao().fetch_all_placed_orders()
        return {"response":active_orders}
    
    except HTTPException as http_exception:     
        raise http_exception
    
    except Exception as e:            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
            )
    

@app.put("/admin/change_order_status/{new_status}/{confirmed_order_id}")
async def change_order_status(new_status:str,confirmed_order_id:int):
    try:
        response=ConfirmedOrderDao().change_order_status(confirmed_order_id,new_status)
        return response
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
            )
    

class DeliveryAgentDetailsFromUser(BaseModel):
    name:str
    mobile_number:str
    address:str
    sex:str

@app.post("/admin/add_new_delivery_agents")
async def add_new_delivery_agents(delivery_agent_details: DeliveryAgentDetailsFromUser):
    try: 
        response = DeliveryAgentDao().add_new_delivery_partner(delivery_agent_details)
        return response
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

@app.get("/admin/fetch_delivery_agents/")
async def fetch_delivery_agents():
    try:
        response=DeliveryAgentDao().fetch_delivery_agents_info()
        return response
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
    except SQLAlchemyError as se:
        raise



async def get_stats() :
    tasks = [
        ConfirmedOrderDao().fetch_number_of_open_orders(),
        ConfirmedOrderDao().fetch_number_of_completed_orders(),
        PaymentGateway().fetch_sales_till_date(),
        UserDao().fetch_users_onboarded_count(),
    ]

    try:
        results = await asyncio.gather(*tasks)
        headings = ["number_of_open_orders", "number_of_completed_orders", "sales_till_date", "users_onboarded_count"]
        return zip(headings, results)
    except SQLAlchemyError as se:
        raise HTTPException(status_code=500, detail=f"Database error: {se}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/admin/get_stats/")
async def admin_stats():
    try:
        return await get_stats()
    except HTTPException as http_exception:
        raise http_exception

    
@app.get("/admin/get_product_details/")
async def get_product_info():
    try:
        return ProductInfoDao().fetch_product_info()
    except SQLAlchemyError as se:
        raise HTTPException(status_code=500, detail=f"Database error: {se}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/admin/manage_product_availability/{product_id}/{available_quantity}")
async def update_product_availability_quantity(product_id:int,available_quantity:int):
    try:
        response=ProductInfoDao().update_available_product_quantity(product_id=product_id,quantity_to_be_updated=available_quantity)
        return response
    except SQLAlchemyError as se:
        print(se)
        raise HTTPException(status_code=500, detail=f"Database error: {se}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    

    
    

@app.post("/admin/assign_delivery_agent/{confirmed_order_id}/{available_delivery_agent_id}")
async def assign_delivery_agent(confirmed_order_id:int):
    return True
    


