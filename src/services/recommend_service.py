import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# 模拟数据（当 AKShare 不可用时使用）
_SIMULATED_FUNDS = [
    {"fund_code": "110011", "fund_name": "易方达中小盘混合", "fund_type": "混合型", "nav": 5.832, "weekly_growth": 3.21},
    {"fund_code": "161725", "fund_name": "招商中证白酒指数", "fund_type": "股票型", "nav": 1.456, "weekly_growth": 2.87},
    {"fund_code": "005827", "fund_name": "易方达蓝筹精选混合", "fund_type": "混合型", "nav": 2.341, "weekly_growth": 2.54},
    {"fund_code": "001410", "fund_name": "华夏能源革新股票", "fund_type": "股票型", "nav": 3.128, "weekly_growth": 2.39},
    {"fund_code": "003834", "fund_name": "中欧时代先锋股票A", "fund_type": "股票型", "nav": 2.876, "weekly_growth": 2.15},
    {"fund_code": "007119", "fund_name": "景顺长城绩优成长混合", "fund_type": "混合型", "nav": 1.654, "weekly_growth": 1.98},
    {"fund_code": "010423", "fund_name": "汇添富科技创新混合C", "fund_type": "混合型", "nav": 1.432, "weekly_growth": 1.76},
    {"fund_code": "006781", "fund_name": "兴全合润混合", "fund_type": "混合型", "nav": 2.567, "weekly_growth": 1.65},
    {"fund_code": "011602", "fund_name": "广发聚安混合A", "fund_type": "混合型", "nav": 1.893, "weekly_growth": 1.52},
    {"fund_code": "012092", "fund_name": "富国天惠成长混合LOF", "fund_type": "混合型", "nav": 4.321, "weekly_growth": 1.43},
]

_SIMULATED_STOCKS = [
    {"stock_code": "600519", "stock_name": "贵州茅台", "price": 1685.00, "change_pct": 2.34},
    {"stock_code": "000858", "stock_name": "五粮液", "price": 152.60, "change_pct": 1.87},
    {"stock_code": "601318", "stock_name": "中国平安", "price": 48.92, "change_pct": 1.56},
    {"stock_code": "000333", "stock_name": "美的集团", "price": 63.25, "change_pct": 1.42},
    {"stock_code": "600036", "stock_name": "招商银行", "price": 33.18, "change_pct": 1.28},
    {"stock_code": "300750", "stock_name": "宁德时代", "price": 195.40, "change_pct": 1.15},
    {"stock_code": "601888", "stock_name": "中国中免", "price": 82.30, "change_pct": 0.98},
    {"stock_code": "002594", "stock_name": "比亚迪", "price": 275.60, "change_pct": 0.87},
    {"stock_code": "600900", "stock_name": "长江电力", "price": 28.45, "change_pct": 0.76},
    {"stock_code": "300059", "stock_name": "东方财富", "price": 18.92, "change_pct": 0.65},
]


def get_recommend_funds(limit: int = 20) -> List[Dict]:
    """获取推荐基金（按近1周涨幅排序），失败时返回模拟数据"""
    try:
        import akshare as ak
        import pandas as pd
        df = ak.fund_open_fund_rank_em()
        if df is not None and not df.empty:
            df = df.sort_values('近1周', ascending=False).head(limit)
            results = []
            for _, row in df.iterrows():
                results.append({
                    'fund_code': str(row['基金代码']),
                    'fund_name': str(row['基金简称']),
                    'fund_type': str(row.get('基金类型', '')),
                    'nav': float(row['单位净值']) if pd.notna(row['单位净值']) else 0,
                    'weekly_growth': float(row['近1周']) if pd.notna(row['近1周']) else 0,
                })
            return results
    except Exception as e:
        logger.warning(f'获取推荐基金失败，使用模拟数据: {e}')
    
    return _SIMULATED_FUNDS[:limit]


def get_hot_stocks(limit: int = 20) -> List[Dict]:
    """获取热门股票（东方财富热榜），失败时返回模拟数据"""
    try:
        import akshare as ak
        import pandas as pd
        df = ak.stock_hot_rank_em()
        if df is not None and not df.empty:
            df = df.head(limit)
            results = []
            for _, row in df.iterrows():
                results.append({
                    'stock_code': str(row['代码']),
                    'stock_name': str(row['股票名称']),
                    'price': float(row['最新价']) if pd.notna(row['最新价']) else 0,
                    'change_pct': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                })
            return results
    except Exception as e:
        logger.warning(f'获取热门股票失败，使用模拟数据: {e}')
    
    return _SIMULATED_STOCKS[:limit]
