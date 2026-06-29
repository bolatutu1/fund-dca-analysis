from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, WatchlistItem, Fund
from services import akshare_client
from typing import Optional

router = APIRouter(tags=['自选基金'])

client = akshare_client.AKShareClient()


def require_login(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail='请先登录')
    return user_id


@router.get('/list')
async def get_list(request: Request, db: Session = Depends(get_db)):
    user_id = require_login(request)
    items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id
    ).order_by(WatchlistItem.added_at.desc()).all()

    result = []
    for item in items:
        history = client.get_fund_history(item.fund_code)
        current_nav = None
        daily_change = None
        fund_name = ''
        if history:
            latest = history[-1]
            current_nav = latest['nav']
            daily_change = latest.get('daily_change')
            detail = client.get_fund_detail(item.fund_code)
            if detail:
                fund_name = detail['fund_name']
        result.append({
            'fund_code': item.fund_code,
            'fund_name': fund_name or item.fund_code,
            'current_nav': current_nav,
            'daily_change': daily_change,
            'added_at': item.added_at.isoformat() if item.added_at else None,
        })
    return result


@router.post('/add')
async def add_item(
    request: Request,
    fund_code: str = Query(..., alias='fund_code'),
    db: Session = Depends(get_db),
):
    user_id = require_login(request)
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.fund_code == fund_code,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail='该基金已在自选列表中')

    detail = client.get_fund_detail(fund_code)
    if not detail:
        raise HTTPException(status_code=404, detail='未找到该基金')

    fund = db.query(Fund).filter(Fund.fund_code == fund_code).first()
    if not fund:
        fund = Fund(
            fund_code=fund_code,
            fund_name=detail['fund_name'],
            fund_type=detail.get('fund_type', ''),
        )
        db.add(fund)
    else:
        fund.fund_name = detail['fund_name']
        fund.fund_type = detail.get('fund_type', '')

    watchlist_item = WatchlistItem(
        user_id=user_id,
        fund_code=fund_code,
    )
    db.add(watchlist_item)
    db.commit()

    return {'message': f"已添加 {detail['fund_name']} 到自选"}


@router.delete('/remove')
async def remove_item(
    request: Request,
    fund_code: str = Query(...),
    db: Session = Depends(get_db),
):
    user_id = require_login(request)
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.fund_code == fund_code,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail='该基金不在自选列表中')

    db.delete(item)
    db.commit()
    return {'message': f'已移除 {fund_code}'}
