import akshare as ak
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AKShareClient:
    def search_fund(self, keyword: str) -> List[dict]:
        try:
            df = ak.fund_open_fund_rank_em()
            if df is None or df.empty:
                return []
            mask = df['基金代码'].astype(str).str.contains(keyword, na=False) | df['基金简称'].str.contains(keyword, na=False)
            matched = df[mask].head(50)
            results = []
            for _, row in matched.iterrows():
                code = str(row['基金代码'])
                name = str(row['基金简称'])
                ftype = str(row.get('基金类型', ''))
                if code and name:
                    results.append({'fund_code': code, 'fund_name': name, 'fund_type': ftype})
            return results
        except Exception as e:
            logger.error(f'Search fund failed: {e}')
            return []

    def get_fund_detail(self, fund_code: str) -> Optional[dict]:
        try:
            info_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
            if info_df is None or info_df.empty:
                return None
            basic = {}
            for _, row in info_df.iterrows():
                key = str(row.iloc[0])
                val = str(row.iloc[1])
                basic[key] = val
            fund_type = basic.get('基金类型', '')
            manager = basic.get('基金经理', '')
            size = basic.get('最新规模', '')
            rating = basic.get('评级', '')
            return {
                'fund_code': fund_code,
                'fund_name': basic.get('基金全称', basic.get('基金名称', fund_code)),
                'fund_type': fund_type,
                'manager': manager,
                'size': size,
                'rating': rating,
            }
        except Exception as e:
            logger.error(f'Get fund detail failed {fund_code}: {e}')
            return None

    def get_fund_history(self, fund_code: str, start_date: str = None, end_date: str = None) -> List[dict]:
        try:
            df = ak.fund_open_fund_info_em(symbol=fund_code, indicator='单位净值走势')
            if df is None or df.empty:
                return []
            df['净值日期'] = pd.to_datetime(df['净值日期'])
            if start_date:
                sd = pd.to_datetime(start_date)
                df = df[df['净值日期'] >= sd]
            if end_date:
                ed = pd.to_datetime(end_date)
                df = df[df['净值日期'] <= ed]
            results = []
            for _, row in df.iterrows():
                date_str = row['净值日期'].strftime('%Y-%m-%d')
                nav = float(row['单位净值']) if pd.notna(row['单位净值']) else 0
                daily = 0
                if pd.notna(row.get('日增长率', None)):
                    daily = float(row['日增长率'])
                results.append({'date': date_str, 'nav': round(nav, 4), 'acc_nav': None, 'daily_change': round(daily, 2) if daily else None})
            results.sort(key=lambda x: x['date'])
            return results
        except Exception as e:
            logger.error(f'Get fund history failed {fund_code}: {e}')
            return []
