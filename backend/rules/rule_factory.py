"""规则工厂模块"""

from typing import Dict, Any, Optional, List
from .base_rule import BaseRule
from .price_rule import PriceAboveRule, PriceBreakoutRule
from .volume_rule import VolumeAboveRule, VolumeThresholdRule
from .indicator_rule import RSICrossRule, MACrossRule, MACDRule


class RuleFactory:
    """规则工厂类，负责创建具体的规则实例"""
    
    @staticmethod
    def create_rule(rule_type: str, params: Dict[str, Any]) -> Optional[BaseRule]:
        """
        根据规则类型和参数创建具体的规则实例
        
        Args:
            rule_type: 规则类型名称
            params: 规则参数字典
            
        Returns:
            BaseRule: 创建的规则实例，如果类型不支持则返回None
        """
        rule_mapping = {
            "price_above": PriceAboveRule,
            "price_level": PriceAboveRule,  # 兼容旧命名
            "price_breakout": PriceBreakoutRule,
            "price_threshold": PriceBreakoutRule,  # 兼容旧命名
            "volume_above": VolumeAboveRule,
            "volume_multiple": VolumeAboveRule,  # 兼容旧命名
            "volume_threshold": VolumeThresholdRule,
            "rsi_cross": RSICrossRule,
            "rsi_check": RSICrossRule,  # 兼容旧命名
            "ma_cross": MACrossRule,
            "ma_check": MACrossRule,  # 兼容旧命名
            "macd_cross": MACDRule,
            "macd_check": MACDRule,  # 兼容旧命名
        }
        
        rule_class = rule_mapping.get(rule_type)
        if rule_class:
            return rule_class(params)
        return None
    
    @staticmethod
    def create_rules_from_config(config: Dict[str, Any]) -> List[BaseRule]:
        """
        从配置字典创建规则列表
        
        Args:
            config: 包含规则配置的字典
            
        Returns:
            List[BaseRule]: 创建的规则实例列表
        """
        rules = []
        
        # 从新配置格式创建规则
        if "rules" in config:
            rules_config = config["rules"]
            for rule_type, rule_value in rules_config.items():
                # 支持两种格式：
                # 1. 扁平化格式: "rule_type": true
                # 2. 对象格式: "rule_type": {"enabled": true, ...其他参数}
                enabled = False
                
                if isinstance(rule_value, bool):
                    # 扁平化格式，值直接表示是否启用
                    enabled = rule_value
                elif isinstance(rule_value, dict) and "enabled" in rule_value:
                    # 对象格式，通过enabled键表示是否启用
                    enabled = rule_value.get("enabled", False)
                    
                    # 将对象中的其他参数添加到配置中
                    for key, val in rule_value.items():
                        if key != "enabled":
                            # 添加参数名称前缀，适配现有代码
                            if key.startswith(rule_type + "_"):
                                config[key] = val
                            else:
                                config[rule_type + "_" + key] = val
                                config[key] = val  # 同时保留不带前缀的版本，提高兼容性
                
                if enabled and (enabled is True or str(enabled).lower() == 'true' or enabled == 1):
                    # 复制配置，确保不修改原始配置
                    params = config.copy()
                    # 创建规则实例
                    rule = RuleFactory.create_rule(rule_type, params)
                    if rule:
                        rules.append(rule)
        
        return rules 