import akshare as ak
import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_recommend_funds(limit: int = 20) -> List[Dict]:
    """获取推荐基金（按近1周涨幅排序）"""
    try:
        df = ak.fund_open_fund_rank_em()
        if df is None or df.empty:
            return []
        # 按近1周涨幅排序
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
        logger.error(f'获取推荐基金失败: {e}')
        return []


def get_hot_stocks(limit: int = 20) -> List[Dict]:
    """获取热门股票（东方财富热榜）"""
    try:
        df = ak.stock_hot_rank_em()
        if df is None or df.empty:
            return []
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
        logger.error(f'获取热门股票失败: {e}')
        return []
