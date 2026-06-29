from fastapi import APIRouter, HTTPException
from services import akshare_client
from services import analysis_engine
from schemas import InvestmentRequest, InvestmentResult, FundInfo
from datetime import datetime

router = APIRouter(tags=['定投分析'])

client = akshare_client.AKShareClient()


@router.post('/dca', response_model=InvestmentResult)
async def analyze_dca(req: InvestmentRequest):
    history = client.get_fund_history(
        req.fund_code,
        start_date=req.start_date.strftime('%Y%m%d'),
        end_date=(req.end_date or datetime.now()).strftime('%Y%m%d'),
    )
    if not history:
        raise HTTPException(status_code=404, detail='未获取到基金历史数据，请检查基金代码')

    detail = client.get_fund_detail(req.fund_code)
    fund_name = detail['fund_name'] if detail else req.fund_code

    result = analysis_engine.calculate_dca(
        invest_amount=req.amount,
        frequency=req.frequency.value,
        start_date=req.start_date,
        end_date=req.end_date or datetime.now(),
        nav_history=history,
    )

    return InvestmentResult(
        fund_code=req.fund_code,
        fund_name=fund_name,
        total_invested=result['total_invested'],
        current_value=result['current_value'],
        profit=result['profit'],
        profit_rate=result['profit_rate'],
        annualized_return=result['annualized_return'],
        max_drawdown=result['max_drawdown'],
        investment_days=result['investment_days'],
        times=result['times'],
        avg_cost=result['avg_cost'],
        chart_data=result['chart_data'],
    )
