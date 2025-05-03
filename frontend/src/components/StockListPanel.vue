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
              <div class="flex items-center mb-3">
                <span class="px-3 py-1.5 text-xs leading-none font-bold rounded-full flex items-center" 
                  :class="getStrategyTypeClass(strategy.strategy_type)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  {{ strategy.strategy_type }}
                </span>
                <span class="ml-3 font-semibold text-gray-700">{{ strategy.strategy_name }}</span>
              </div>
              
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div v-for="(value, key) in strategy.rules" :key="key" 
                    class="text-sm p-2 bg-white rounded border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-200"
                  >
                    <span class="text-gray-500 font-medium">{{ formatRuleKey(key) }}:</span>
                    <span class="ml-1 text-gray-800" :class="{'text-green-600 font-medium': value === true, 'text-red-600 font-medium': value === false}">
                      {{ formatRuleValue(key, value) }}
                    </span>
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

export default {
  name: 'StockListPanel',
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
  emits: ['select-stock', 'delete-stock', 'run-monitoring', 'show-chart', 'set-chart-type'],
  setup(props, { emit }) {
    const expandedStocks = ref({})
    const activeTab = ref('candlestick')
    
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
      const keyMap = {
        'consecutive_bars': '连续K线',
        'fast_ma': '快速均线',
        'macd_check': 'MACD检查',
        'price_level': '价格水平',
        'rsi_check': 'RSI检查',
        'rsi_overbought': 'RSI超买',
        'rsi_oversold': 'RSI超卖',
        'slow_ma': '慢速均线',
        'consecutive_up_bars': '连续上涨',
        'volume_increase': '成交量增长',
        'price_above_ma': '价格高于均线',
        'macd_golden_cross': 'MACD金叉',
        'rsi_rising': 'RSI上升',
        'rsi_min': 'RSI最小值',
        'rsi_max': 'RSI最大值',
        'stop_loss_percent': '止损百分比',
        'price_threshold': '价格阈值',
        'volume_threshold': '成交量阈值',
        '价格阈值': '价格阈值',
        '成交量阈值': '成交量阈值'
      }
      return keyMap[key] || key
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
    
    return {
      expandedStocks,
      toggleExpand,
      getStrategyTypeClass,
      formatRuleKey,
      formatRuleValue,
      activeTab,
      showStockChart,
      setChartType
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