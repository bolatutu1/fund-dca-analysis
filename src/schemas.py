from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ========== 用户认证 ==========

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str


# ========== 基金数据 ==========

class FundInfo(BaseModel):
    fund_code: str
    fund_name: str
    fund_type: str
    manager: Optional[str] = None
    size: Optional[str] = None
    rating: Optional[str] = None


class NetValuePoint(BaseModel):
    date: str
    nav: float  # 单位净值
    acc_nav: Optional[float] = None  # 累计净值
    daily_change: Optional[float] = None  # 日增长率


class FundDetail(FundInfo):
    history: List[NetValuePoint] = []


# ========== 定投分析 ==========

class Frequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class InvestmentRequest(BaseModel):
    fund_code: str
    amount: float = Field(..., gt=0, description="每期定投金额（元）")
    frequency: Frequency = Field(default=Frequency.MONTHLY)
    start_date: datetime = Field(..., description="定投起始日期")
    end_date: Optional[datetime] = None  # 默认为今天


class InvestmentResult(BaseModel):
    fund_code: str
    fund_name: str
    total_invested: float  # 累计投入
    current_value: float  # 当前市值
    profit: float  # 收益
    profit_rate: float  # 收益率（%）
    annualized_return: Optional[float] = None  # 年化收益率
    max_drawdown: Optional[float] = None  # 最大回撤
    investment_days: int  # 投资天数
    times: int  # 定投次数
    avg_cost: Optional[float] = None  # 平均成本
    chart_data: List[dict] = []  # 用于图表的数据


# ========== 自选基金 ==========

class WatchlistItemResponse(BaseModel):
    fund_code: str
    fund_name: str
    current_nav: Optional[float] = None
    daily_change: Optional[float] = None
    added_at: Optional[datetime] = None


# ========== 搜索结果 ==========

class SearchResult(BaseModel):
    fund_code: str
    fund_name: str
    fund_type: str
