from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    path = Column(String(1000), nullable=False)
    level = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    children = relationship("Category", back_populates="parent", remote_side=[id])
    parent = relationship("Category", back_populates="children", remote_side=[parent_id])
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="client")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
