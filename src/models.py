from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    watchlist_items = relationship("WatchlistItem", back_populates="user")


class Fund(Base):
    """本地缓存的基金信息"""
    __tablename__ = "funds"

    fund_code = Column(String(20), primary_key=True, index=True)
    fund_name = Column(String(100), nullable=False)
    fund_type = Column(String(50))  # 股票型、混合型、债券型、指数型
    manager = Column(String(50))
    size = Column(String(20))  # 规模，字符串保持原始格式
    rating = Column(String(10))  # 评级
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WatchlistItem(Base):
    """用户自选基金"""
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fund_code = Column(String(20), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist_items")


class InvestmentRecord(Base):
    """定投记录（本地持久化）"""
    __tablename__ = "investment_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fund_code = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)  # 每期定投金额
    frequency = Column(String(20))  # weekly, biweekly, monthly
    start_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
