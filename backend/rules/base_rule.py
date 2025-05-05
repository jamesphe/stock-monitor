from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Tuple, Any, List


class BaseRule(ABC):
    """规则基类，所有具体规则都应该继承这个类"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化规则
        
        Args:
            params: 规则所需的参数字典
        """
        self.params = params or {}
    
    @abstractmethod
    def check(self, daily_data: pd.DataFrame, 
              minute_data: pd.DataFrame = None) -> Tuple[bool, str, Dict]:
        """
        检查规则是否满足
        
        Args:
            daily_data: 日线数据DataFrame
            minute_data: 分钟线数据DataFrame (可选)
            
        Returns:
            Tuple[bool, str, Dict]: (是否触发, 触发原因描述, 详细结果字典)
        """
        pass
    
    @abstractmethod
    def get_rule_name(self) -> str:
        """获取规则名称"""
        pass
    
    def validate_params(self) -> bool:
        """验证参数是否有效"""
        return True
    
    def get_description(self) -> str:
        """获取规则描述"""
        return f"规则: {self.get_rule_name()}"


class RuleResult:
    """规则检查结果类"""
    
    def __init__(self, triggered: bool = False, description: str = "", 
                 details: Dict[str, Any] = None, 
                 conditions_met: List[str] = None):
        self.triggered = triggered  # 是否触发
        self.description = description  # 描述信息
        self.details = details or {}  # 详细结果
        self.conditions_met = conditions_met or []  # 满足的条件 