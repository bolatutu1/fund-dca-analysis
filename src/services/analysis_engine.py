from datetime import datetime, timedelta
from typing import List, Optional
import math


def calculate_dca(invest_amount: float, frequency: str,
                  start_date: datetime, end_date: datetime,
                  nav_history: List[dict]) -> dict:
    """
    计算定投收益

    Args:
        invest_amount: 每期定投金额
        frequency: weekly / biweekly / monthly
        start_date: 起始日期
        end_date: 结束日期
        nav_history: 历史净值 [{date, nav, ...}]

    Returns:
        定投分析结果
    """
    # 生成定投日期列表
    invest_dates = _generate_invest_dates(start_date, end_date, frequency)

    # 按日期建立净值查找表
    nav_map = {h["date"]: h["nav"] for h in nav_history}

    total_invested = 0.0
    units_held = 0.0
    records = []

    for d in invest_dates:
        date_str = d.strftime("%Y-%m-%d")
        nav = nav_map.get(date_str)
        if nav and nav > 0:
            invested = invest_amount
            units_bought = invested / nav
            total_invested += invested
            units_held += units_bought
            records.append({
                "date": date_str,
                "nav": nav,
                "amount": invested,
                "units": units_bought,
                "cum_invested": total_invested,
                "cum_units": units_held,
            })

    if not records:
        return {
            "total_invested": 0,
            "current_value": 0,
            "profit": 0,
            "profit_rate": 0,
            "annualized_return": None,
            "max_drawdown": None,
            "investment_days": 0,
            "times": 0,
            "avg_cost": None,
            "chart_data": [],
        }

    # 当前净值（最后一天）
    last_nav = nav_history[-1]["nav"] if nav_history else 0
    current_value = units_held * last_nav
    profit = current_value - total_invested
    profit_rate = (profit / total_invested * 100) if total_invested > 0 else 0

    # 平均成本
    avg_cost = total_invested / units_held if units_held > 0 else 0

    # 年化收益率
    investment_days = (end_date - start_date).days
    years = investment_days / 365.0
    annualized_return = None
    if years > 0 and total_invested > 0:
        # 定投年化: (终值/本金)^(1/年数) - 1 简化计算
        annualized_return = (math.pow(current_value / total_invested, 1 / years) - 1) * 100 \
            if current_value > 0 else 0

    # 最大回撤（基于累计净值曲线）
    max_drawdown = _calculate_max_drawdown(records, last_nav)

    # 构建图表数据（每日持仓市值）
    chart_data = _build_chart_data(records, nav_history, last_nav, end_date)

    return {
        "total_invested": round(total_invested, 2),
        "current_value": round(current_value, 2),
        "profit": round(profit, 2),
        "profit_rate": round(profit_rate, 2),
        "annualized_return": round(annualized_return, 2) if annualized_return is not None else None,
        "max_drawdown": round(max_drawdown, 2) if max_drawdown is not None else None,
        "investment_days": investment_days,
        "times": len(records),
        "avg_cost": round(avg_cost, 4),
        "chart_data": chart_data,
    }


def _generate_invest_dates(start: datetime, end: datetime,
                           frequency: str) -> List[datetime]:
    """生成定投日期列表"""
    dates = []
    current = start

    if frequency == "weekly":
        delta = timedelta(weeks=1)
    elif frequency == "biweekly":
        delta = timedelta(weeks=2)
    else:  # monthly
        delta = None
        while current <= end:
            dates.append(current)
            # 下个月同一天
            month = current.month + 1
            year = current.year
            if month > 12:
                month = 1
                year += 1
            try:
                current = current.replace(year=year, month=month)
            except ValueError:
                # 处理月末日期（如1月31日 -> 2月28日）
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                day = min(current.day, last_day)
                current = current.replace(year=year, month=month, day=day)
        return dates

    while current <= end:
        dates.append(current)
        current += delta
    return dates


def _calculate_max_drawdown(records: List[dict], current_nav: float) -> Optional[float]:
    """计算最大回撤"""
    if not records:
        return None

    # 计算每天的持仓市值
    nav_map = {r["date"]: r["nav"] for r in records}
    values = []
    for h in records:
        val = h["cum_units"] * h["nav"]
        values.append({"date": h["date"], "value": val, "invested": h["cum_invested"]})

    # 加入最后一天（用当前净值）
    last_val = records[-1]["cum_units"] * current_nav
    values.append({
        "date": (records[-1]["date"] if records else ""),
        "value": last_val,
        "invested": records[-1]["cum_invested"] if records else 0,
    })

    peak = values[0]["value"]
    max_dd = 0.0
    for v in values:
        if v["value"] > peak:
            peak = v["value"]
        dd = (peak - v["value"]) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd

    return max_dd


def _build_chart_data(records: List[dict], nav_history: List[dict],
                      current_nav: float, end_date: datetime) -> List[dict]:
    """构建图表数据"""
    nav_map = {h["date"]: h["nav"] for h in nav_history}

    chart = []
    for r in records:
        cum_units = r["cum_units"]
        nav = r["nav"]
        value = cum_units * nav
        invested = r["cum_invested"]
        profit = value - invested
        profit_rate = (profit / invested * 100) if invested > 0 else 0
        chart.append({
            "date": r["date"],
            "value": round(value, 2),
            "invested": round(invested, 2),
            "profit": round(profit, 2),
            "profit_rate": round(profit_rate, 2),
        })

    # 补充最后一段无交易的日期（用当前净值更新市值）
    if records:
        last_record_date = records[-1]["date"]
        last_cum_units = records[-1]["cum_units"]
        last_invested = records[-1]["cum_invested"]

        # 找到最后一条记录在nav_history中的位置
        last_idx = -1
        for i, h in enumerate(nav_history):
            if h["date"] == last_record_date:
                last_idx = i

        if last_idx >= 0:
            for h in nav_history[last_idx + 1:]:
                value = last_cum_units * h["nav"]
                profit = value - last_invested
                profit_rate = (profit / last_invested * 100) if last_invested > 0 else 0
                chart.append({
                    "date": h["date"],
                    "value": round(value, 2),
                    "invested": round(last_invested, 2),
                    "profit": round(profit, 2),
                    "profit_rate": round(profit_rate, 2),
                })

            # 用当前净值补充到今天
            if current_nav > 0:
                value = last_cum_units * current_nav
                profit = value - last_invested
                profit_rate = (profit / last_invested * 100) if last_invested > 0 else 0
                chart.append({
                    "date": end_date.strftime("%Y-%m-%d"),
                    "value": round(value, 2),
                    "invested": round(last_invested, 2),
                    "profit": round(profit, 2),
                    "profit_rate": round(profit_rate, 2),
                })

    return chart
