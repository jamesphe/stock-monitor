"""成交量相关规则实现"""

import pandas as pd
from typing import Dict, Tuple, Any
from .base_rule import BaseRule


class VolumeAboveRule(BaseRule):
    """
    成交量放大规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.volume_multiple = float(self.params.get("volume_multiple", 1.5))
        self.lookback = int(self.params.get("volume_lookback", 5))
    
    def get_rule_name(self) -> str:
        return "成交量放大规则"
    
    def validate_params(self) -> bool:
        return self.volume_multiple > 1.0 and self.lookback > 0
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查当前成交量是否高于过去N日平均的M倍
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if daily_data is not None and 'volume' in daily_data.columns and len(daily_data) > self.lookback:
            current_volume = daily_data['volume'].iloc[-1]
            avg_volume = daily_data['volume'].iloc[-self.lookback-1:-1].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            volume_above = volume_ratio > self.volume_multiple
            
            details["pass"] = volume_above
            details["description"] = (
                f"当前成交量: {int(current_volume)}, 过去{self.lookback}日均量: "
                f"{int(avg_volume)}, 对比倍数: {volume_ratio:.2f}倍, "
                f"需大于: {self.volume_multiple}倍"
            )
            
            if volume_above:
                is_triggered = True
                trigger_reason = f"成交量为过去{self.lookback}日均值的{self.volume_multiple}倍以上"
                conditions_met.append("volume")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        }
    
    def _check_volume_above(self, df: pd.DataFrame) -> bool:
        """检查当前成交量是否高于过去N日平均的M倍"""
        if df is None or df.empty or len(df) <= self.lookback:
            return False
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-self.lookback-1:-1].mean()
        
        return current_volume > avg_volume * self.volume_multiple


class VolumeThresholdRule(BaseRule):
    """
    成交量阈值规则
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        super().__init__(params)
        self.volume_threshold = float(self.params.get("volume_threshold", 0))
    
    def get_rule_name(self) -> str:
        return "成交量阈值规则"
    
    def validate_params(self) -> bool:
        return self.volume_threshold > 0
    
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查当前成交量是否高于指定阈值
        """
        # 初始化结果
        is_triggered = False
        trigger_reason = ""
        details = {"pass": False, "description": ""}
        conditions_met = []
        
        # 日线检查
        if daily_data is not None and 'volume' in daily_data.columns:
            current_volume = daily_data['volume'].iloc[-1]
            volume_above = current_volume > self.volume_threshold
            
            details["pass"] = volume_above
            details["description"] = (
                f"当前成交量: {int(current_volume)}, 阈值: {int(self.volume_threshold)}"
            )
            
            if volume_above:
                is_triggered = True
                trigger_reason = f"成交量超过阈值{int(self.volume_threshold)}"
                conditions_met.append("volume_threshold")
        
        return is_triggered, trigger_reason, {
            "details": details,
            "conditions_met": conditions_met
        } 