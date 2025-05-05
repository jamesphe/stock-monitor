"""价格相关规则实现"""

import pandas as pd
from typing import Dict, Tuple, Any
from .base_rule import BaseRule


class PriceAboveRule(BaseRule):
    """
    价格连续高于指定水平的规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.price_level = float(self.params.get("price_level", 0))
        self.consecutive_bars = int(self.params.get("consecutive_bars", 1))
    
    def get_rule_name(self) -> str:
        return "价格突破规则"
    
    def validate_params(self) -> bool:
        return self.price_level > 0
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查价格是否连续若干个周期高于指定水平
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if (daily_data is not None and 'close' in daily_data.columns 
                and len(daily_data) >= self.consecutive_bars):
            price_above = self._check_price_above(daily_data)
            recent_prices = [
                str(round(p, 2)) 
                for p in daily_data['close'].tail(self.consecutive_bars).values
            ]
            
            details["pass"] = price_above
            details["description"] = (
                f"日线最近{self.consecutive_bars}日收盘价: "
                f"{', '.join(recent_prices)}, 需突破: {self.price_level}"
            )
            
            if price_above:
                is_triggered = True
                trigger_reason = (
                    f"价格连续{self.consecutive_bars}日收盘价高于{self.price_level}"
                )
                conditions_met.append("price_daily")
                return is_triggered, trigger_reason, {
                    "details": details,
                    "conditions_met": conditions_met
                }
        
        # 分钟线检查（仅当日线未触发时检查）
        if (minute_data is not None and 'close' in minute_data.columns 
                and len(minute_data) >= self.consecutive_bars):
            price_above = self._check_price_above(minute_data)
            recent_prices = [
                str(round(p, 2)) 
                for p in minute_data['close'].tail(self.consecutive_bars).values
            ]
            
            if not details["pass"]:  # 只有当日线未通过时才覆盖结果
                details["pass"] = price_above
                minute_desc = (
                    f"5分钟最近{self.consecutive_bars}个周期收盘价: "
                    f"{', '.join(recent_prices)}, 需突破: {self.price_level}"
                )
                
                if details["description"]:
                    details["description"] += f"\n{minute_desc}"
                else:
                    details["description"] = minute_desc
            
            if price_above:
                is_triggered = True
                trigger_reason = (
                    f"价格连续{self.consecutive_bars}个5分钟收盘价高于{self.price_level}"
                )
                conditions_met.append("price_minute")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_price_above(self, df: pd.DataFrame) -> bool:
        """检查价格是否连续若干个周期高于指定水平"""
        if df is None or df.empty or len(df) < self.consecutive_bars:
            return False
        
        # 获取最近N个周期的收盘价
        recent_closes = df['close'].tail(self.consecutive_bars)
        # 检查是否所有收盘价都高于指定价格
        return all(recent_closes > self.price_level)


class PriceBreakoutRule(BaseRule):
    """
    价格突破指定高点或低点的规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        # 处理前端传入的threshold参数
        threshold = self.params.get("threshold")
        
        self.high_level = self.params.get("high_level")
        if self.high_level is not None:
            self.high_level = float(self.high_level)
        elif threshold is not None and (
                self.params.get("is_buy_strategy", False) or 
                not self.params.get("is_sell_strategy", False)):
            # 如果提供了threshold参数并且是买入策略或未指定策略类型，则用作high_level
            self.high_level = float(threshold)
            
        self.low_level = self.params.get("low_level")
        if self.low_level is not None:
            self.low_level = float(self.low_level)
        elif threshold is not None and self.params.get("is_sell_strategy", False):
            # 如果提供了threshold参数并且是卖出策略，则用作low_level
            self.low_level = float(threshold)
            
        self.consecutive_bars = int(self.params.get("consecutive_bars", 1))
        self.is_buy_strategy = self.params.get("is_buy_strategy", False)
        self.is_sell_strategy = self.params.get(
            "is_sell_strategy", False
        )
    
    def get_rule_name(self) -> str:
        if self.is_buy_strategy:
            return "价格上涨突破规则"
        elif self.is_sell_strategy:
            return "价格下跌突破规则"
        return "价格阈值突破规则"
    
    def validate_params(self) -> bool:
        return self.high_level is not None or self.low_level is not None
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查价格是否突破指定高点或低点
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 检查使用哪个阈值
        high_level = self.high_level
        low_level = self.low_level
        
        # 根据策略类型决定使用哪个阈值
        if self.is_buy_strategy:
            # 加仓策略只检查上突破
            low_level = None
        elif self.is_sell_strategy:
            # 减仓策略只检查下突破
            high_level = None
        
        # 日线检查
        if (daily_data is not None and 'close' in daily_data.columns 
                and len(daily_data) >= self.consecutive_bars):
            threshold_met, desc = self._check_breakout(daily_data, high_level, low_level)
            
            details["pass"] = threshold_met
            
            if desc:
                details["description"] = desc
            else:
                current_price = daily_data['close'].iloc[-1]
                if self.is_buy_strategy:
                    threshold_str = "未设置" if high_level is None else f"{high_level:.2f}"
                    details["description"] = (
                        f"日线最近价格: {current_price:.2f}, 目标买入价: {threshold_str}"
                    )
                elif self.is_sell_strategy:
                    threshold_str = "未设置" if low_level is None else f"{low_level:.2f}"
                    details["description"] = (
                        f"日线最近价格: {current_price:.2f}, 目标卖出价: {threshold_str}"
                    )
                else:
                    high_str = "未设置" if high_level is None else f"{high_level:.2f}"
                    low_str = "未设置" if low_level is None else f"{low_level:.2f}"
                    details["description"] = (
                        f"日线最近价格: {current_price:.2f}, 上阈值: {high_str}, 下阈值: {low_str}"
                    )
            
            if threshold_met:
                is_triggered = True
                if self.is_buy_strategy:
                    trigger_reason = f"价格突破加仓阈值{high_level}"
                elif self.is_sell_strategy:
                    trigger_reason = f"价格跌破减仓阈值{low_level}"
                else:
                    trigger_reason = f"价格触发阈值{high_level or low_level}"
                
                conditions_met.append("price_threshold_daily")
                return is_triggered, trigger_reason, {
                    "details": details,
                    "conditions_met": conditions_met
                }
        
        # 分钟线检查（仅当日线未触发时检查）
        if (minute_data is not None and 'close' in minute_data.columns 
                and len(minute_data) >= self.consecutive_bars):
            threshold_met, desc = self._check_breakout(
                minute_data, high_level, low_level
            )
            
            if not details["pass"]:  # 只有当日线未通过时才覆盖结果
                details["pass"] = threshold_met
                
                if desc:
                    if not details["description"]:
                        details["description"] = desc
                    else:
                        details["description"] += f"\n{desc}"
                else:
                    current_price = minute_data['close'].iloc[-1]
                    minute_desc = ""
                    if self.is_buy_strategy:
                        threshold_str = "未设置" if high_level is None else f"{high_level:.2f}"
                        minute_desc = (
                            f"5分钟最近价格: {current_price:.2f}, 目标买入价: {threshold_str}"
                        )
                    elif self.is_sell_strategy:
                        threshold_str = "未设置" if low_level is None else f"{low_level:.2f}"
                        minute_desc = (
                            f"5分钟最近价格: {current_price:.2f}, 目标卖出价: {threshold_str}"
                        )
                    else:
                        high_str = "未设置" if high_level is None else f"{high_level:.2f}"
                        low_str = "未设置" if low_level is None else f"{low_level:.2f}"
                        minute_desc = (
                            f"5分钟最近价格: {current_price:.2f}, 上阈值: {high_str}, 下阈值: {low_str}"
                        )
                    
                    if not details["description"]:
                        details["description"] = minute_desc
                    else:
                        details["description"] += f"\n{minute_desc}"
            
            if threshold_met:
                is_triggered = True
                if self.is_buy_strategy:
                    trigger_reason = f"价格突破加仓阈值{high_level} (5分钟)"
                elif self.is_sell_strategy:
                    trigger_reason = f"价格跌破减仓阈值{low_level} (5分钟)"
                else:
                    trigger_reason = f"价格触发阈值{high_level or low_level} (5分钟)"
                
                conditions_met.append("price_threshold_minute")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_breakout(self, df: pd.DataFrame, high_level: float = None, 
                        low_level: float = None) -> Tuple[bool, str]:
        """检查价格是否突破指定高点或低点"""
        if df is None or df.empty or len(df) < self.consecutive_bars:
            return False, None
        
        # 获取最近n根K线的收盘价
        recent_closes = df['close'].iloc[-self.consecutive_bars:].values
        current_price = recent_closes[-1]  # 最新价格
        
        # 生成价格列表字符串
        prices_str = ', '.join([f'{c:.2f}' for c in recent_closes])
        
        # 检查突破高点
        if high_level is not None:
            # 检查最近n根K线是否全部收盘价高于指定高点
            if all(close > high_level for close in recent_closes):
                msg = (
                    f"价格突破上阈值{high_level:.2f}，"
                    f"连续{self.consecutive_bars}周期 "
                    f"收盘价为{prices_str}"
                )
                return True, msg
        
        # 检查突破低点
        if low_level is not None:
            # 检查最近n根K线是否全部收盘价低于指定低点
            if all(close < low_level for close in recent_closes):
                msg = (
                    f"价格跌破下阈值{low_level:.2f}，"
                    f"连续{self.consecutive_bars}周期 "
                    f"收盘价为{prices_str}"
                )
                return True, msg
        
        # 未触发条件时，返回详细的价格信息
        if high_level is not None and low_level is not None:
            high_status = "已突破" if current_price > high_level else "未突破"
            low_status = "已跌破" if current_price < low_level else "未跌破"
            msg = (
                f"当前价格: {current_price:.2f}, "
                f"上阈值: {high_level:.2f} ({high_status}), "
                f"下阈值: {low_level:.2f} ({low_status})"
            )
            return False, msg
        elif high_level is not None:
            status = "已突破" if current_price > high_level else "未突破"
            msg = f"当前价格: {current_price:.2f}, 上阈值: {high_level:.2f} ({status})"
            return False, msg
        elif low_level is not None:
            status = "已跌破" if current_price < low_level else "未跌破"
            msg = f"当前价格: {current_price:.2f}, 下阈值: {low_level:.2f} ({status})"
            return False, msg
        
        return False, None 