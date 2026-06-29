from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services import akshare_client
from services.recommend_service import get_recommend_funds, get_hot_stocks

router = APIRouter(tags=['基金'])

client = akshare_client.AKShareClient()


@router.get('/search')
async def search_fund(keyword: str = Query(..., min_length=1, max_length=20)):
    results = client.search_fund(keyword)
    return {'results': results, 'count': len(results)}


@router.get('/detail/{fund_code}')
async def get_fund_detail(fund_code: str):
    detail = client.get_fund_detail(fund_code)
    if not detail:
        raise HTTPException(status_code=404, detail='未找到该基金')
    return detail


@router.get('/history/{fund_code}')
async def get_fund_history(fund_code: str,
                           start_date: Optional[str] = Query(None),
                           end_date: Optional[str] = Query(None)):
    history = client.get_fund_history(fund_code, start_date, end_date)
    if not history:
        raise HTTPException(status_code=404, detail='未获取到历史数据')
    return {'fund_code': fund_code, 'history': history, 'count': len(history)}


@router.get('/recommend')
async def get_recommend():
    """获取推荐基金和热门股票"""
    funds = get_recommend_funds(limit=20)
    stocks = get_hot_stocks(limit=20)
    return {
        'funds': funds,
        'stocks': stocks,
    }
