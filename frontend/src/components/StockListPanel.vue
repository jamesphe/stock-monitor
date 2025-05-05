<template>
  <div>
    <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800 flex items-center">
          <span class="text-blue-600 mr-2">📊</span>
          <span>监控列表</span>
        </h2>
        <button 
          @click="$emit('run-monitoring')"
          class="bg-gradient-to-r from-green-500 to-green-600 text-white py-2.5 px-5 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          :disabled="isRunningMonitor"
          :class="{'opacity-60 cursor-not-allowed': isRunningMonitor}"
        >
          <span v-if="!isRunningMonitor" class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            立即执行监控
          </span>
          <span v-else class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            执行中...
          </span>
        </button>
      </div>
      
      <div v-if="stocks.length === 0" class="py-16 text-center">
        <div class="flex flex-col items-center justify-center">
          <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          <p class="text-gray-500 text-lg">暂无监控股票，请在左侧添加</p>
        </div>
      </div>
      
      <div v-else class="space-y-4">
        <div v-for="(stock, stockIndex) in stocks" :key="stockIndex" 
          class="border border-gray-200 rounded-xl overflow-hidden transition-all duration-200 hover:shadow-md">
          <div 
            class="bg-gradient-to-r from-gray-50 to-gray-100 p-4 flex justify-between items-center cursor-pointer" 
            @click="toggleExpand(stockIndex)"
          >
            <div class="flex items-center">
              <div class="p-2 bg-blue-50 rounded-lg mr-3 text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <div>
                <span class="font-bold text-gray-800">{{ stock.code }}</span>
                <span class="ml-2 text-gray-600 font-medium">{{ stock.name }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <button 
                @click.stop="showStockChart(stock)" 
                class="text-purple-600 hover:text-purple-800 hover:bg-purple-50 rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200"
              >
                <span class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  图表
                </span>
              </button>
              <button 
                @click.stop="$emit('select-stock', stock)" 
                class="text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200"
              >
                <span class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  编辑
                </span>
              </button>
              <button 
                @click.stop="$emit('delete-stock', stockIndex)" 
                class="text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200"
              >
                <span class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  删除
                </span>
              </button>
              <div 
                class="h-6 w-6 flex items-center justify-center rounded-full bg-gray-200 text-gray-600 transform transition-transform duration-300"
                :class="expandedStocks[stockIndex] ? 'rotate-180 bg-blue-100 text-blue-600' : ''"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
          
          <div 
            v-show="expandedStocks[stockIndex]" 
            class="p-4 bg-white border-t border-gray-200 transition-all duration-500 ease-in-out"
          >
            <div v-for="(strategy, strategyIndex) in stock.strategies" :key="strategyIndex" 
              class="mb-5 last:mb-0 bg-white rounded-lg"
            >
              <div class="flex justify-between items-center mb-3">
                <div class="flex items-center">
                  <span class="px-3 py-1.5 text-xs leading-none font-bold rounded-full flex items-center" 
                    :class="getStrategyTypeClass(strategy.strategy_type)">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    {{ strategy.strategy_type }}
                  </span>
                  <span class="ml-3 font-semibold text-gray-700">{{ strategy.strategy_name }}</span>
                </div>
                <button 
                  @click.stop="runStrategy(stock, strategy, stockIndex, strategyIndex)"
                  :disabled="isStrategyRunning(stockIndex, strategyIndex)"
                  :class="{'opacity-70 cursor-not-allowed': isStrategyRunning(stockIndex, strategyIndex)}"
                  class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-md px-3 py-1.5 text-sm font-medium shadow-sm hover:shadow-md transition-all duration-300 flex items-center"
                >
                  <svg v-if="!isStrategyRunning(stockIndex, strategyIndex)" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  </svg>
                  <svg v-else class="animate-spin h-4 w-4 mr-1.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ isStrategyRunning(stockIndex, strategyIndex) ? '执行中...' : '执行策略' }}
                </button>
              </div>
              
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <!-- 价格规则 -->
                  <PriceRuleCard 
                    v-for="(ruleConfig, ruleType) in getPriceRules(strategy.rules)" 
                    :key="ruleType"
                    :rule-type="ruleType"
                    :rule-config="ruleConfig"
                  />
                  
                  <!-- 成交量规则 -->
                  <VolumeRuleCard 
                    v-for="(ruleConfig, ruleType) in getVolumeRules(strategy.rules)" 
                    :key="ruleType"
                    :rule-type="ruleType"
                    :rule-config="ruleConfig"
                  />
                  
                  <!-- 技术指标规则 -->
                  <IndicatorRuleCard 
                    v-for="(ruleConfig, ruleType) in getIndicatorRules(strategy.rules)" 
                    :key="ruleType"
                    :rule-type="ruleType"
                    :rule-config="ruleConfig"
                  />
                  
                  <!-- 其他规则和参数 -->
                  <OtherRuleCard 
                    v-for="(ruleValue, ruleType) in getOtherRules(strategy.rules)" 
                    :key="ruleType"
                    :rule-type="ruleType"
                    :rule-value="ruleValue"
                  />
                </div>
              </div>
              
              <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`]" 
                class="mt-3 overflow-hidden transition-all duration-500 ease-in-out transform"
                :class="[
                  getResultBackgroundClass(strategyResults[`${stockIndex}-${strategyIndex}`].status),
                  {'scale-100 opacity-100 max-h-[1000px]': strategyResults[`${stockIndex}-${strategyIndex}`], 'scale-95 opacity-0 max-h-0': !strategyResults[`${stockIndex}-${strategyIndex}`]}
                ]"
              >
                <div class="p-3 rounded-lg border-2 shadow-sm" 
                  :class="getResultBorderClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)">
                  <div class="flex items-center">
                    <div class="p-2 rounded-full mr-2" :class="getResultIconClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)">
                      <svg v-if="strategyResults[`${stockIndex}-${strategyIndex}`].status === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <svg v-else-if="strategyResults[`${stockIndex}-${strategyIndex}`].status === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                    <span class="text-base font-bold" :class="getResultTextClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)">
                      {{ strategyResults[`${stockIndex}-${strategyIndex}`].message }}
                    </span>
                    <span 
                      v-if="strategyResults[`${stockIndex}-${strategyIndex}`].status !== 'success'" 
                      class="ml-auto text-sm underline cursor-pointer"
                      :class="getResultTextClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)"
                      @click="toggleDetails(`${stockIndex}-${strategyIndex}`)"
                    >
                      {{ showDetailKeys[`${stockIndex}-${strategyIndex}`] ? '收起详情' : '查看详情' }}
                    </span>
                  </div>
                  
                  <!-- 显示原因摘要 -->
                  <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`].status !== 'success' && !showDetailKeys[`${stockIndex}-${strategyIndex}`]"
                    class="mt-2 text-sm px-3 py-2 bg-gray-50 rounded-lg border-l-4 border-yellow-400">
                    <span class="font-medium text-gray-700">未满足原因: </span>
                    <span v-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.price?.description" 
                      class="text-gray-600 whitespace-pre-line">
                      {{ strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.price.description }}
                    </span>
                    <span v-else-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.macd_check?.description" 
                      class="text-gray-600 whitespace-pre-line">
                      {{ strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.macd_check.description }}
                    </span>
                    <span v-else-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.rsi_check?.description" 
                      class="text-gray-600 whitespace-pre-line">
                      {{ strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.rsi_check.description }}
                    </span>
                    <span v-else class="text-gray-600">
                      当前条件未达到策略要求
                    </span>
                  </div>
                  
                  <!-- 详情调试面板 -->
                  <div v-if="showDetailKeys[`${stockIndex}-${strategyIndex}`]" 
                    class="mt-3 pt-3 border-t border-gray-200">
                    
                    <!-- 价格阈值显示 -->
                    <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.price_threshold">
                      <PriceThresholdCard :price-data="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.price_threshold" />
                    </div>
                    
                    <!-- 成交量阈值显示 -->
                    <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.volume_threshold">
                      <VolumeThresholdCard :volume-data="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.volume_threshold" />
                    </div>
                    
                    <!-- MACD检查显示 -->
                    <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.macd_check">
                      <MacdCheckCard :macd-data="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.macd_check" />
                    </div>
                    
                    <!-- RSI检查显示 -->
                    <div v-if="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation?.details?.rsi_check">
                      <RsiCheckCard :rsi-data="strategyResults[`${stockIndex}-${strategyIndex}`].evaluation.details.rsi_check" />
                    </div>
                  </div>
                  
                  <!-- 详细结果部分 - 针对字符串类型的details -->
                  <div 
                    v-if="strategyResults[`${stockIndex}-${strategyIndex}`].details && showDetailKeys[`${stockIndex}-${strategyIndex}`] && typeof strategyResults[`${stockIndex}-${strategyIndex}`].details === 'string'" 
                    class="mt-3 pt-3 border-t text-sm whitespace-pre-line transition-all duration-500 ease-in-out"
                    :class="getResultBorderClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)"
                  >
                    <!-- 处理不同类型的详情数据 -->
                    <div class="space-y-3">
                      <!-- 直接显示详情，不再进行条件判断 -->
                      <template>
                        <div v-for="(line, lineIndex) in strategyResults[`${stockIndex}-${strategyIndex}`].details.split('\n')" :key="lineIndex">
                          <div class="flex items-start">
                            <div class="w-2 h-2 rounded-full mt-1.5 mr-1.5" :class="getResultBackgroundClass(strategyResults[`${stockIndex}-${strategyIndex}`].status)"></div>
                            <div>{{ line }}</div>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>

                  <!-- 执行时间戳 -->
                  <div v-if="!showDetailKeys[`${stockIndex}-${strategyIndex}`]" class="mt-3 pt-2 border-t text-xs text-right flex justify-end items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-gray-500">{{ formatTimestamp(strategyResults[`${stockIndex}-${strategyIndex}`].timestamp || Date.now()) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import MacdCheckCard from './MacdCheckCard.vue'
import RsiCheckCard from './RsiCheckCard.vue'
import PriceThresholdCard from './PriceThresholdCard.vue'
import VolumeThresholdCard from './VolumeThresholdCard.vue'
import PriceRuleCard from './PriceRuleCard.vue'
import VolumeRuleCard from './VolumeRuleCard.vue'
import IndicatorRuleCard from './IndicatorRuleCard.vue'
import OtherRuleCard from './OtherRuleCard.vue'

export default {
  name: 'StockListPanel',
  components: {
    MacdCheckCard,
    RsiCheckCard,
    PriceThresholdCard,
    VolumeThresholdCard,
    PriceRuleCard,
    VolumeRuleCard,
    IndicatorRuleCard,
    OtherRuleCard
  },
  props: {
    stocks: {
      type: Array,
      required: true
    },
    isRunningMonitor: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select-stock', 'delete-stock', 'run-monitoring', 'show-chart', 'set-chart-type', 'run-strategy'],
  setup(props, { emit }) {
    const expandedStocks = ref({})
    const activeTab = ref('candlestick')
    const runningStrategies = ref({})
    const strategyResults = ref({})
    const showDetailKeys = ref({})
    
    const toggleExpand = (index) => {
      expandedStocks.value[index] = !expandedStocks.value[index]
    }
    
    const showStockChart = (stock) => {
      emit('show-chart', stock)
    }
    
    const setChartType = (type) => {
      activeTab.value = type
      emit('set-chart-type', type)
    }
    
    const runStrategy = (stock, strategy, stockIndex, strategyIndex) => {
      const key = `${stockIndex}-${strategyIndex}`
      runningStrategies.value[key] = true
      
      // 发射事件到父组件处理策略执行
      emit('run-strategy', { stock, strategy, stockIndex, strategyIndex }, (result) => {
        // 回调处理执行结果
        strategyResults.value[key] = result
        runningStrategies.value[key] = false
      })
    }
    
    const isStrategyRunning = (stockIndex, strategyIndex) => {
      const key = `${stockIndex}-${strategyIndex}`
      return !!runningStrategies.value[key]
    }
    
    const getResultBackgroundClass = (status) => {
      const classes = {
        'success': 'bg-green-50',
        'warning': 'bg-yellow-50',
        'error': 'bg-red-50'
      }
      return classes[status] || 'bg-gray-50'
    }
    
    const getResultIconClass = (status) => {
      const classes = {
        'success': 'bg-green-100 text-green-600',
        'warning': 'bg-yellow-100 text-yellow-600',
        'error': 'bg-red-100 text-red-600'
      }
      return classes[status] || 'bg-gray-100 text-gray-600'
    }
    
    const getResultTextClass = (status) => {
      const classes = {
        'success': 'text-green-700',
        'warning': 'text-yellow-700',
        'error': 'text-red-700'
      }
      return classes[status] || 'text-gray-700'
    }
    
    const getResultBorderClass = (status) => {
      const classes = {
        'success': 'border-green-100',
        'warning': 'border-yellow-100',
        'error': 'border-red-100'
      }
      return classes[status] || 'border-gray-100'
    }
    
    const getStrategyTypeClass = (type) => {
      const classes = {
        '基础监控': 'bg-blue-100 text-blue-700',
        '买入策略': 'bg-green-100 text-green-700',
        '卖出策略': 'bg-red-100 text-red-700',
        '止损策略': 'bg-yellow-100 text-yellow-700'
      }
      return classes[type] || 'bg-gray-100 text-gray-700'
    }
    
    const formatRuleKey = (key) => {
      // 对嵌套键进行处理
      const lastPart = key.includes('.') ? key.split('.').pop() : key
      
      const keyMap = {
        'consecutive_bars': '连续K线',
        'fast_ma': '快速均线',
        'macd_check': 'MACD检查',
        'price_level': '价格水平',
        'rsi_check': 'RSI检查',
        'overbought': 'RSI超买',
        'oversold': 'RSI超卖',
        'slow_ma': '慢速均线',
        'consecutive_up_bars': '连续上涨',
        'multiple': '成交量倍数',
        'lookback': '回溯周期',
        'ma_line': '均线',
        'golden_cross': 'MACD金叉',
        'rising': 'RSI上升',
        'min': 'RSI最小值',
        'max': 'RSI最大值',
        'stop_loss_percent': '止损百分比',
        'threshold': '阈值',
        'value': '数值',
        'is_buy_strategy': '买入策略',
        'is_sell_strategy': '卖出策略'
      }
      
      return keyMap[lastPart] || lastPart
    }
    
    const formatRuleValue = (key, value) => {
      if (typeof value === 'boolean') {
        return value ? '是' : '否'
      }
      
      if (key.includes('percent')) {
        return `${value}%`
      }
      
      return value
    }
    
    const toggleDetails = (key) => {
      showDetailKeys.value[key] = !showDetailKeys.value[key]
      // 添加调试日志
      if (showDetailKeys.value[key] && strategyResults.value[key]) {
        console.log('详情数据结构:', JSON.stringify(strategyResults.value[key], null, 2))
        console.log('evaluation:', strategyResults.value[key].evaluation)
        console.log('details:', strategyResults.value[key].evaluation?.details)
      }
    }
    
    const formatTimestamp = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }
    
    // 格式化成交量函数
    const formatVolume = (volume) => {
      if (!volume && volume !== 0) return '-'
      
      if (volume >= 100000000) {
        return (volume / 100000000).toFixed(2) + '亿'
      } else if (volume >= 10000) {
        return (volume / 10000).toFixed(2) + '万'
      } else {
        return volume.toFixed(0)
      }
    }
    
    // 格式化时间函数
    const formatTime = (dateStr) => {
      if (!dateStr) return '-'
      
      // 处理纯数字索引的情况
      if (!isNaN(dateStr)) {
        return "数据索引 #" + dateStr;
      }
      
      try {
        const date = new Date(dateStr)
        return date.getHours().toString().padStart(2, '0') + ':' + 
               date.getMinutes().toString().padStart(2, '0')
      } catch (e) {
        return dateStr
      }
    }
    
    // 规则分类函数
    const getPriceRules = (rules) => {
      const priceRules = {}
      for (const [key, value] of Object.entries(rules)) {
        if (['price_level', 'price_above', 'price_breakout'].includes(key) && value && typeof value === 'object') {
          priceRules[key] = value
        }
      }
      return priceRules
    }
    
    const getVolumeRules = (rules) => {
      const volumeRules = {}
      for (const [key, value] of Object.entries(rules)) {
        if (['volume_above', 'volume_threshold'].includes(key) && value && typeof value === 'object') {
          volumeRules[key] = value
        }
      }
      return volumeRules
    }
    
    const getIndicatorRules = (rules) => {
      const indicatorRules = {}
      for (const [key, value] of Object.entries(rules)) {
        if (['rsi_check', 'rsi_cross', 'ma_cross', 'macd_check', 'macd_cross'].includes(key) && value && typeof value === 'object') {
          indicatorRules[key] = value
        }
      }
      return indicatorRules
    }
    
    const getOtherRules = (rules) => {
      const otherRules = {}
      for (const [key, value] of Object.entries(rules)) {
        if (!['price_level', 'price_above', 'price_breakout', 'volume_above', 'volume_threshold', 
              'rsi_check', 'rsi_cross', 'ma_cross', 'macd_check', 'macd_cross'].includes(key)) {
          otherRules[key] = value
        }
      }
      return otherRules
    }
    
    return {
      expandedStocks,
      toggleExpand,
      getStrategyTypeClass,
      formatRuleKey,
      formatRuleValue,
      getPriceRules,
      getVolumeRules,
      getIndicatorRules,
      getOtherRules,
      activeTab,
      showStockChart,
      setChartType,
      runStrategy,
      isStrategyRunning,
      strategyResults,
      getResultBackgroundClass,
      getResultIconClass,
      getResultTextClass,
      getResultBorderClass,
      showDetailKeys,
      toggleDetails,
      formatTimestamp,
      formatVolume,
      formatTime
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

* {
  font-family: 'Noto Sans SC', sans-serif;
}
</style>