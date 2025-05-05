<template>
  <div class="bg-white rounded-lg p-3 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
    <div class="flex justify-between items-start mb-2">
      <div class="flex items-center">
        <div class="p-1.5 bg-blue-50 rounded-md mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
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
      <!-- 价格水平规则 -->
      <template v-if="ruleType === 'price_level'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">阈值:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.threshold }}</span>
        </div>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">连续K线:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.consecutive_bars || 1 }}</span>
        </div>
      </template>
      
      <!-- 价格突破规则 -->
      <template v-else-if="ruleType === 'price_breakout'">
        <!-- 使用单一阈值的情况 -->
        <div v-if="ruleConfig.threshold" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">
            {{ ruleConfig.is_buy_strategy ? '买入阈值:' : 
               ruleConfig.is_sell_strategy ? '卖出阈值:' : '阈值:' }}
          </span>
          <span class="font-medium text-gray-800">{{ ruleConfig.threshold }}</span>
        </div>
        
        <!-- 使用上下阈值的情况 -->
        <div v-if="ruleConfig.high_level" class="flex justify-between px-2 py-1 bg-green-50 rounded">
          <span class="text-green-600">上阈值:</span>
          <span class="font-medium text-green-800">{{ ruleConfig.high_level }}</span>
        </div>
        <div v-if="ruleConfig.low_level" class="flex justify-between px-2 py-1 bg-red-50 rounded">
          <span class="text-red-600">下阈值:</span>
          <span class="font-medium text-red-800">{{ ruleConfig.low_level }}</span>
        </div>
        
        <div v-if="ruleConfig.consecutive_bars && ruleConfig.consecutive_bars > 1" class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">连续K线:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.consecutive_bars }}</span>
        </div>
        
        <div v-if="ruleConfig.is_buy_strategy" class="flex justify-between px-2 py-1 bg-green-50 rounded">
          <span class="text-green-600">买入策略:</span>
          <span class="font-medium text-green-800">是</span>
        </div>
        <div v-if="ruleConfig.is_sell_strategy" class="flex justify-between px-2 py-1 bg-red-50 rounded">
          <span class="text-red-600">卖出策略:</span>
          <span class="font-medium text-red-800">是</span>
        </div>
      </template>
      
      <!-- 价格均线规则 -->
      <template v-else-if="ruleType === 'price_above'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">参考均线:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.ma_line }}</span>
        </div>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">连续周期:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.consecutive_bars || 1 }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PriceRuleCard',
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
        'price_level': '价格水平监控',
        'price_breakout': '价格阈值突破',
        'price_above': '价格均线位置'
      }
      
      // 对price_breakout规则进行更细致的命名
      if (type === 'price_breakout') {
        if (this.ruleConfig.is_buy_strategy) {
          return '价格上涨突破'
        } else if (this.ruleConfig.is_sell_strategy) {
          return '价格下跌突破'
        }
      }
      
      return typeMap[type] || type
    }
  }
}
</script> 