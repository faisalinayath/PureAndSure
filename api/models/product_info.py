from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductInfo(Base):
    __tablename__ = 'product_info'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    minimum_product_quantity=Column(Float,nullable=True)
    quantity_measurement_unit = Column(String(50), nullable=False)
    product_price = Column(Float, nullable=False)
    product_description = Column(Text, nullable=True)
    available_quantity=Column(Float,nullable=True)
    quantity_left=Column(Float,nullable=True)

    def __init__(self, product_name,minimum_product_quantity, quantity_measurement_unit, product_price, product_description,quantity_left):
        self.product_name = product_name
        self.minimum_product_quantity=minimum_product_quantity
        self.quantity_measurement_unit = quantity_measurement_unit
        self.product_price = product_price
        self.product_description = product_description
        self.quantity_left=quantity_left