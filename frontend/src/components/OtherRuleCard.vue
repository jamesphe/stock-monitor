<template>
  <div class="bg-white rounded-lg p-3 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
    <div class="flex justify-between items-start mb-2">
      <div class="flex items-center">
        <div class="p-1.5 bg-yellow-50 rounded-md mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <span class="font-medium text-gray-700">
          {{ getRuleTypeDisplay(ruleType) }}
        </span>
      </div>
    </div>
    
    <div class="mt-2 space-y-2 text-sm">
      <!-- 止损止盈规则 -->
      <template v-if="ruleType === 'stop_loss_percent'">
        <div class="flex justify-between px-2 py-1 bg-red-50 rounded">
          <span class="text-red-600">止损比例:</span>
          <span class="font-medium text-red-800">{{ ruleValue }}%</span>
        </div>
      </template>
      
      <!-- 风控规则 -->
      <template v-else-if="ruleType === 'risk_management'">
        <div v-if="typeof ruleValue === 'object'">
          <div v-for="(value, key) in ruleValue" :key="key" class="flex justify-between px-2 py-1 bg-yellow-50 rounded mt-1">
            <span class="text-yellow-700">{{ formatKey(key) }}:</span>
            <span class="font-medium text-yellow-900">{{ formatValue(key, value) }}</span>
          </div>
        </div>
        <div v-else class="flex justify-between px-2 py-1 bg-yellow-50 rounded">
          <span class="text-yellow-700">{{ ruleType }}:</span>
          <span class="font-medium text-yellow-900">{{ ruleValue }}</span>
        </div>
      </template>
      
      <!-- 其他规则 -->
      <template v-else>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">{{ ruleType }}:</span>
          <span class="font-medium text-gray-800">{{ formatValue(ruleType, ruleValue) }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OtherRuleCard',
  props: {
    ruleType: {
      type: String,
      required: true
    },
    ruleValue: {
      type: [String, Number, Boolean, Object],
      required: true
    }
  },
  methods: {
    getRuleTypeDisplay(type) {
      const typeMap = {
        'stop_loss_percent': '止损控制',
        'risk_management': '风险管理',
        'consecutive_bars': '连续K线',
        'pattern': '形态识别'
      }
      return typeMap[type] || type
    },
    formatKey(key) {
      const keyMap = {
        'stop_loss_percent': '止损比例',
        'take_profit_percent': '止盈比例',
        'max_position': '最大仓位'
      }
      return keyMap[key] || key
    },
    formatValue(key, value) {
      if (typeof value === 'boolean') {
        return value ? '是' : '否'
      }
      
      if (key.includes('percent')) {
        return `${value}%`
      }
      
      return value
    }
  }
}
</script> 