"""规则评估器模块"""

import logging
import time
import pandas as pd
from typing import Dict, Any, List, Tuple
from .base_rule import BaseRule
from .rule_factory import RuleFactory


class RuleEvaluator:
    """规则评估器，用于评估一组规则"""
    
    def __init__(self, logger=None):
        """
        初始化规则评估器
        
        Args:
            logger: 日志记录器，如果为None则创建新的
        """
        self.logger = logger or logging.getLogger("monitor")
    
    def evaluate_stock_rules(self, 
                             stock_code: str, 
                             stock_name: str, 
                             daily_data: pd.DataFrame,
                             minute_data: pd.DataFrame, 
                             strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        评估单个股票的所有策略和规则
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            daily_data: 日线数据
            minute_data: 分钟线数据
            strategies: 策略配置列表
            
        Returns:
            List[Dict]: 触发的告警信息列表
        """
        self.logger.info(f"开始评估股票 {stock_name}({stock_code}) 的策略")
        print(f"\n开始评估股票 {stock_name}({stock_code}) 的策略")
        
        alerts = []
        
        # 检查数据有效性
        if daily_data is None or daily_data.empty:
            self.logger.warning(f"股票 {stock_code} 日线数据无效")
            print(f"股票 {stock_code} 日线数据无效")
            return alerts
        
        # 处理所有策略
        for strategy_idx, strategy in enumerate(strategies):
            strategy_name = strategy.get("strategy_name", f"策略{strategy_idx+1}")
            strategy_type = strategy.get("strategy_type", "未知")
            
            self.logger.info(
                f"评估策略 [{strategy_idx+1}/{len(strategies)}]: "
                f"{strategy_name}({strategy_type})"
            )
            print(f"\n{'*'*30}")
            print(
                f"评估策略: {strategy_name}({strategy_type}) "
                f"[{strategy_idx+1}/{len(strategies)}]"
            )
            print(f"{'*'*30}")
            
            # 使用工厂创建规则
            rules = RuleFactory.create_rules_from_config(strategy)
            
            if not rules:
                self.logger.warning(f"策略 {strategy_name} 没有有效规则配置")
                print(f"策略 {strategy_name} 没有有效规则配置")
                continue
            
            # 评估策略的所有规则
            alert = self._evaluate_strategy_rules(
                stock_code, stock_name, daily_data, minute_data, 
                strategy_name, strategy_type, rules
            )
            
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _evaluate_strategy_rules(self, 
                                stock_code: str, 
                                stock_name: str,
                                daily_data: pd.DataFrame, 
                                minute_data: pd.DataFrame,
                                strategy_name: str, 
                                strategy_type: str, 
                                rules: List[BaseRule]) -> Dict[str, Any]:
        """
        评估单个策略的所有规则
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            daily_data: 日线数据
            minute_data: 分钟线数据
            strategy_name: 策略名称
            strategy_type: 策略类型
            rules: 规则列表
            
        Returns:
            Dict: 如果规则触发，返回告警信息字典，否则返回None
        """
        triggered = False
        trigger_reasons = []
        daily_conditions_met = []
        minute_conditions_met = []
        details = {}
        
        self.logger.info(f"开始评估 {stock_code} 策略 {strategy_name} 的监控条件")
        print(f"\n-----监控条件评估开始-----")
        
        for rule in rules:
            rule_name = rule.get_rule_name()
            
            self.logger.debug(f"评估规则: {rule_name}")
            print(f"\n🔍 评估规则: {rule_name}")
            
            start_time = time.time()
            is_triggered, reason, result = rule.check(daily_data, minute_data)
            check_time = time.time() - start_time
            
            # 记录规则评估结果
            rule_details = result.get("details", {})
            rule_conditions = result.get("conditions_met", [])
            
            # 添加到详细结果
            details[rule_name] = rule_details
            
            # 如果规则触发，添加触发原因
            if is_triggered:
                triggered = True
                trigger_reasons.append(reason)
                
                # 根据条件类型分类
                for condition in rule_conditions:
                    if condition.endswith('_daily'):
                        daily_conditions_met.append(condition)
                    elif condition.endswith('_minute'):
                        minute_conditions_met.append(condition)
                    else:
                        daily_conditions_met.append(condition)
                
                self.logger.info(f"规则 {rule_name} 触发: {reason}, 耗时: {check_time:.4f}秒")
                print(f"  ✓ 规则触发: {reason}")
            else:
                self.logger.debug(f"规则 {rule_name} 未触发, 耗时: {check_time:.4f}秒")
                print(f"  ✗ 规则未触发")
            
            # 输出规则评估详情
            description = rule_details.get("description", "")
            if description:
                for line in description.split("\n"):
                    print(f"    - {line}")
        
        # 根据规则评估结果生成告警信息
        if triggered:
            # 确定信号类型
            if any("macd" in r for r in daily_conditions_met) or any("ma_cross" in r for r in daily_conditions_met):
                if "金叉" in " ".join(trigger_reasons):
                    action = "buy"
                elif "死叉" in " ".join(trigger_reasons):
                    action = "sell"
                else:
                    action = "alert"
            elif any("price" in r for r in daily_conditions_met) or any("volume" in r for r in daily_conditions_met):
                action = "buy"
            elif any("rsi_cross" in r for r in daily_conditions_met):
                if "超买" in " ".join(trigger_reasons):
                    action = "sell"
                elif "超卖" in " ".join(trigger_reasons):
                    action = "buy"
                else:
                    action = "alert"
            else:
                action = "alert"
            
            # 根据策略类型调整动作类型
            if "建仓" in strategy_type:
                action_display = "建仓"
            elif "加仓" in strategy_type:
                action_display = "加仓"
            elif "减仓" in strategy_type:
                action_display = "减仓"
            elif "清仓" in strategy_type:
                action_display = "清仓"
            else:
                action_display = "监控"
            
            # 获取当前价格
            if daily_data is not None and 'close' in daily_data.columns and not daily_data.empty:
                current_price = daily_data['close'].iloc[-1]
            elif minute_data is not None and 'close' in minute_data.columns and not minute_data.empty:
                current_price = minute_data['close'].iloc[-1]
            else:
                current_price = 0
            
            # 生成告警消息
            message = (
                f"{stock_name}({stock_code}) [{strategy_name}-{action_display}] "
                f"当前价: {current_price:.2f}，触发条件: {', '.join(trigger_reasons)}"
            )
            
            self.logger.info(f"触发告警: {message}")
            print(f"\n✅ 触发告警: {message}")
            
            # 生成告警信息字典
            return {
                "code": stock_code,
                "name": stock_name,
                "price": current_price,
                "action": action,
                "action_display": action_display,
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "message": message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reasons": trigger_reasons,
                "details": details
            }
        else:
            self.logger.info(f"未触发告警: {stock_code}")
            print(f"\n❌ 未触发任何告警条件")
            return None 