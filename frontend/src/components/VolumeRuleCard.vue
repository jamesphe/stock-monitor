<template>
  <div class="bg-white rounded-lg p-3 border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
    <div class="flex justify-between items-start mb-2">
      <div class="flex items-center">
        <div class="p-1.5 bg-green-50 rounded-md mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
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
      <!-- 成交量放大规则 -->
      <template v-if="ruleType === 'volume_above'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">放大倍数:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.multiple }}倍</span>
        </div>
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">回溯周期:</span>
          <span class="font-medium text-gray-800">{{ ruleConfig.lookback || 5 }}天</span>
        </div>
      </template>
      
      <!-- 成交量阈值规则 -->
      <template v-else-if="ruleType === 'volume_threshold'">
        <div class="flex justify-between px-2 py-1 bg-gray-50 rounded">
          <span class="text-gray-600">阈值:</span>
          <span class="font-medium text-gray-800">{{ formatVolume(ruleConfig.value) }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VolumeRuleCard',
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
        'volume_above': '成交量放大监控',
        'volume_threshold': '成交量阈值监控'
      }
      return typeMap[type] || type
    },
    formatVolume(volume) {
      if (!volume && volume !== 0) return '-'
      
      if (volume >= 100000000) {
        return (volume / 100000000).toFixed(2) + '亿手'
      } else if (volume >= 10000) {
        return (volume / 10000).toFixed(2) + '万手'
      } else {
        return volume.toFixed(0) + '手'
      }
    }
  }
}
</script> 