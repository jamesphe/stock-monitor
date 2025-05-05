<template>
  <div class="bg-white rounded-lg p-3 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
    <div class="flex justify-between items-start mb-2">
      <div class="flex items-center">
        <div class="p-1.5 bg-purple-50 rounded-md mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <span class="font-medium text-gray-700">
          {{ getRuleTypeDisplay(ruleType) }}
        </span>
      </div>
      <span class="text-xs px-2 py-1 rounded-full" 
        :class="ruleConfig.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'">
        {{ ruleConfig.enabled ? '已启用' : '未启用' }}
      </span>
    </div>
    
    <div class="mt-2 space-y-2 text-sm">
      <!-- RSI规则 -->
      <template v-if="ruleType === 'rsi_check' || ruleType === 'rsi_cross'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">超买值:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.overbought || 70 }}</span>
        </div>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">超卖值:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.oversold || 30 }}</span>
        </div>
        <div v-if="ruleConfig.rising !== undefined" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">上升趋势:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.rising ? '是' : '否' }}</span>
        </div>
        <div v-if="ruleConfig.min !== undefined" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">最小值:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.min }}</span>
        </div>
        <div v-if="ruleConfig.max !== undefined" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">最大值:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.max }}</span>
        </div>
      </template>
      
      <!-- 均线交叉规则 -->
      <template v-else-if="ruleType === 'ma_cross'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">快速均线:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.fast_ma }}</span>
        </div>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">慢速均线:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.slow_ma }}</span>
        </div>
      </template>
      
      <!-- MACD规则 -->
      <template v-else-if="ruleType === 'macd_check' || ruleType === 'macd_cross'">
        <div v-if="ruleConfig.golden_cross !== undefined" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">金叉检测:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.golden_cross ? '是' : '否' }}</span>
        </div>
        <div v-else class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">MACD检测:</span>
          <span class="font-medium text-gray-800">启用</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndicatorRuleCard',
  props: {
    ruleType: {
      type: String,
      required: true
    },
    ruleConfig: {
      type: Object,
      required: true
    }
  },
  methods: {
    getRuleTypeDisplay(type) {
      const typeMap = {
        'rsi_check': 'RSI指标监控',
        'rsi_cross': 'RSI交叉信号',
        'ma_cross': '均线交叉信号',
        'macd_check': 'MACD指标监控',
        'macd_cross': 'MACD交叉信号'
      }
      return typeMap[type] || type
    }
  }
}
</script> 