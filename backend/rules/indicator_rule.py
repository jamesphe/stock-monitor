"""技术指标相关规则实现"""

import pandas as pd
import pandas_ta as ta
from typing import Dict, Tuple, Any
from .base_rule import BaseRule


class RSICrossRule(BaseRule):
    """
    RSI交叉规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.overbought = float(self.params.get("rsi_overbought", 70))
        self.oversold = float(self.params.get("rsi_oversold", 30))
    
    def get_rule_name(self) -> str:
        return "RSI交叉规则"
    
    def validate_params(self) -> bool:
        return 0 <= self.oversold < self.overbought <= 100
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查RSI是否发生金叉或死叉
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if daily_data is not None:
            # 确保计算RSI
            if 'rsi' not in daily_data.columns:
                daily_data['rsi'] = ta.rsi(daily_data['close'], length=14)
            
            if 'rsi' in daily_data.columns:
                rsi_value = daily_data['rsi'].iloc[-1]
                recent_rsi = [f'{v:.2f}' for v in daily_data['rsi'].tail(3).values]
                
                details["description"] = (
                    f"日线RSI(14)当前值: {rsi_value:.2f}, 最近3个值: {', '.join(recent_rsi)}"
                )
                
                crossed, cross_type = self._check_rsi_cross(daily_data)
                
                details["pass"] = crossed
                if crossed:
                    details["description"] += (
                        f"\n日线RSI指标{cross_type}: 超买区 > {self.overbought}, "
                        f"超卖区 < {self.oversold}"
                    )
                    is_triggered = True
                    trigger_reason = f"日线RSI {cross_type}"
                    conditions_met.append("rsi_cross_daily")
                    return is_triggered, trigger_reason, {
                        "details": details,
                        "conditions_met": conditions_met
                    }
        
        # 分钟线检查（仅当日线未触发时检查）
        if minute_data is not None:
            # 确保计算RSI
            if 'rsi' not in minute_data.columns:
                minute_data['rsi'] = ta.rsi(minute_data['close'], length=14)
            
            if 'rsi' in minute_data.columns:
                rsi_value = minute_data['rsi'].iloc[-1]
                recent_rsi = [f'{v:.2f}' for v in minute_data['rsi'].tail(3).values]
                
                minute_desc = (
                    f"5分钟RSI(14)当前值: {rsi_value:.2f}, 最近3个值: {', '.join(recent_rsi)}"
                )
                
                if details["description"]:
                    details["description"] += f"\n{minute_desc}"
                else:
                    details["description"] = minute_desc
                
                crossed, cross_type = self._check_rsi_cross(minute_data)
                
                if not details["pass"]:  # 只有当日线未通过时才覆盖结果
                    details["pass"] = crossed
                    if crossed:
                        details["description"] += (
                            f"\n5分钟RSI指标{cross_type}: 超买区 > {self.overbought}, "
                            f"超卖区 < {self.oversold}"
                        )
                
                if crossed and cross_type:
                    is_triggered = True
                    trigger_reason = f"5分钟RSI {cross_type}"
                    conditions_met.append("rsi_cross_minute")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_rsi_cross(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """检查RSI是否发生金叉或死叉"""
        if df is None or df.empty or len(df) < 3:
            return False, None
        
        # 检查是否有效的RSI值
        if 'rsi' not in df.columns or df['rsi'].isnull().any():
            return False, None
        
        # 获取最近三个RSI值
        rsi_values = df['rsi'].tail(3).values
        
        # 检查金叉（从超卖区向上穿越）
        if (rsi_values[0] < self.oversold and 
            rsi_values[1] < self.oversold and 
            rsi_values[2] > self.oversold):
            return True, "金叉(超卖区域向上突破)"
        
        # 检查死叉（从超买区向下穿越）
        if (rsi_values[0] > self.overbought and 
            rsi_values[1] > self.overbought and 
            rsi_values[2] < self.overbought):
            return True, "死叉(超买区域向下突破)"
        
        return False, None


class MACrossRule(BaseRule):
    """
    均线交叉规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.fast_ma = self.params.get("fast_ma", "ma5")
        self.slow_ma = self.params.get("slow_ma", "ma20")
    
    def get_rule_name(self) -> str:
        return "均线交叉规则"
    
    def validate_params(self) -> bool:
        return bool(self.fast_ma) and bool(self.slow_ma)
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查均线交叉
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if daily_data is not None:
            # 确保计算均线
            for ma in [5, 10, 20, 60]:
                ma_col = f"ma{ma}"
                if ma_col not in daily_data.columns and len(daily_data) >= ma:
                    daily_data[ma_col] = daily_data['close'].rolling(window=ma).mean()
            
            fast_val = daily_data[self.fast_ma].iloc[-1] if self.fast_ma in daily_data.columns else None
            slow_val = daily_data[self.slow_ma].iloc[-1] if self.slow_ma in daily_data.columns else None
            
            if fast_val is not None and slow_val is not None:
                details["description"] = (
                    f"日线{self.fast_ma}当前值: {fast_val:.2f}, {self.slow_ma}当前值: {slow_val:.2f}"
                )
            else:
                details["description"] = "缺少日线均线数据"
            
            crossed, cross_type = self._check_ma_cross(daily_data)
            
            details["pass"] = crossed
            if crossed:
                details["description"] += f"\n日线{self.fast_ma}/{self.slow_ma}出现{cross_type}"
                is_triggered = True
                trigger_reason = f"日线{self.fast_ma}/{self.slow_ma} {cross_type}"
                conditions_met.append("ma_cross_daily")
                return is_triggered, trigger_reason, {
                    "details": details,
                    "conditions_met": conditions_met
                }
        
        # 分钟线检查（仅当日线未触发时检查）
        if minute_data is not None and not details["pass"]:
            # 确保计算均线
            for ma in [5, 10, 20, 60]:
                ma_col = f"ma{ma}"
                if ma_col not in minute_data.columns and len(minute_data) >= ma:
                    minute_data[ma_col] = minute_data['close'].rolling(window=ma).mean()
            
            fast_val = minute_data[self.fast_ma].iloc[-1] if self.fast_ma in minute_data.columns else None
            slow_val = minute_data[self.slow_ma].iloc[-1] if self.slow_ma in minute_data.columns else None
            
            if fast_val is not None and slow_val is not None:
                minute_desc = (
                    f"5分钟{self.fast_ma}当前值: {fast_val:.2f}, {self.slow_ma}当前值: {slow_val:.2f}"
                )
                if details["description"]:
                    details["description"] += f"\n{minute_desc}"
                else:
                    details["description"] = minute_desc
            else:
                if not details["description"]:
                    details["description"] = "缺少5分钟均线数据"
            
            crossed, cross_type = self._check_ma_cross(minute_data)
            
            if not details["pass"]:  # 只有当日线未通过时才覆盖结果
                details["pass"] = crossed
                if crossed:
                    details["description"] += f"\n5分钟{self.fast_ma}/{self.slow_ma}出现{cross_type}"
            
            if crossed and cross_type:
                is_triggered = True
                trigger_reason = f"5分钟{self.fast_ma}/{self.slow_ma} {cross_type}"
                conditions_met.append("ma_cross_minute")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_ma_cross(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """检查均线交叉"""
        if df is None or df.empty or len(df) < 3:
            return False, None
        
        # 检查均线列是否存在
        if self.fast_ma not in df.columns or self.slow_ma not in df.columns:
            return False, None
        
        # 获取最近3个周期的均线值
        fast_values = df[self.fast_ma].tail(3).values
        slow_values = df[self.slow_ma].tail(3).values
        
        # 检查是否有缺失值
        if any(pd.isna(fast_values)) or any(pd.isna(slow_values)):
            return False, None
        
        # 检查金叉（快线从下方穿过慢线）
        golden_cross = (fast_values[0] < slow_values[0] and 
                       fast_values[1] < slow_values[1] and 
                       fast_values[2] > slow_values[2])
        if golden_cross:
            cross_type = f"{self.fast_ma}/{self.slow_ma}金叉"
            description = "(快线向上穿越慢线)"
            return True, cross_type + description
        
        # 检查死叉（快线从上方穿过慢线）
        death_cross = (fast_values[0] > slow_values[0] and 
                      fast_values[1] > slow_values[1] and 
                      fast_values[2] < slow_values[2])
        if death_cross:
            cross_type = f"{self.fast_ma}/{self.slow_ma}死叉"
            description = "(快线向下穿越慢线)"
            return True, cross_type + description
        
        return False, None


class MACDRule(BaseRule):
    """
    MACD指标规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
    
    def get_rule_name(self) -> str:
        return "MACD指标规则"
    
    def validate_params(self) -> bool:
        return True
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查MACD指标是否发生金叉或死叉
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if daily_data is not None:
            # 确保计算MACD
            if ('macd' not in daily_data.columns or 
                'macd_signal' not in daily_data.columns or 
                'macd_histogram' not in daily_data.columns):
                macd_df = ta.macd(daily_data['close'])
                daily_data['macd'] = macd_df['MACD_12_26_9']
                daily_data['macd_signal'] = macd_df['MACDs_12_26_9']
                daily_data['macd_histogram'] = macd_df['MACDh_12_26_9']
            
            macd_value = daily_data['macd'].iloc[-1]
            signal_value = daily_data['macd_signal'].iloc[-1]
            histogram_value = daily_data['macd_histogram'].iloc[-1]
            
            details["description"] = (
                f"日线MACD: {macd_value:.4f}, 信号线: {signal_value:.4f}, "
                f"柱状图: {histogram_value:.4f}"
            )
            
            crossed, cross_type = self._check_macd_cross(daily_data)
            
            details["pass"] = crossed
            if crossed:
                details["description"] += f"\n日线MACD出现{cross_type}"
                is_triggered = True
                trigger_reason = f"日线MACD {cross_type}"
                conditions_met.append("macd_daily")
                return is_triggered, trigger_reason, {
                    "details": details,
                    "conditions_met": conditions_met
                }
        
        # 分钟线检查（仅当日线未触发时检查）
        if minute_data is not None and not details["pass"]:
            # 确保计算MACD
            if ('macd' not in minute_data.columns or 
                'macd_signal' not in minute_data.columns or 
                'macd_histogram' not in minute_data.columns):
                macd_df = ta.macd(minute_data['close'])
                minute_data['macd'] = macd_df['MACD_12_26_9']
                minute_data['macd_signal'] = macd_df['MACDs_12_26_9']
                minute_data['macd_histogram'] = macd_df['MACDh_12_26_9']
            
            macd_value = minute_data['macd'].iloc[-1]
            signal_value = minute_data['macd_signal'].iloc[-1]
            histogram_value = minute_data['macd_histogram'].iloc[-1]
            
            minute_desc = (
                f"5分钟MACD: {macd_value:.4f}, 信号线: {signal_value:.4f}, "
                f"柱状图: {histogram_value:.4f}"
            )
            
            if details["description"]:
                details["description"] += f"\n{minute_desc}"
            else:
                details["description"] = minute_desc
            
            crossed, cross_type = self._check_macd_cross(minute_data)
            
            if not details["pass"]:  # 只有当日线未通过时才覆盖结果
                details["pass"] = crossed
                if crossed:
                    details["description"] += f"\n5分钟MACD出现{cross_type}"
            
            if crossed and cross_type:
                is_triggered = True
                trigger_reason = f"5分钟MACD {cross_type}"
                conditions_met.append("macd_minute")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_macd_cross(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """检查MACD指标是否发生金叉或死叉"""
        if df is None or df.empty or len(df) < 3:
            return False, None
        
        # 检查MACD相关列是否存在
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            return False, None
        
        # 获取最近3个周期的MACD和信号线值
        macd_values = df['macd'].tail(3).values
        signal_values = df['macd_signal'].tail(3).values
        
        # 检查是否有缺失值
        if any(pd.isna(macd_values)) or any(pd.isna(signal_values)):
            return False, None
        
        # 检查金叉（MACD从下方穿过信号线）
        if (macd_values[0] < signal_values[0] and 
            macd_values[1] < signal_values[1] and 
            macd_values[2] > signal_values[2]):
            return True, "金叉(MACD线上穿信号线)"
        
        # 检查死叉（MACD从上方穿过信号线）
        if (macd_values[0] > signal_values[0] and 
            macd_values[1] > signal_values[1] and 
            macd_values[2] < signal_values[2]):
            return True, "死叉(MACD线下穿信号线)"
        
        return False, None 