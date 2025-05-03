<template>
  <div class="bg-white rounded-lg shadow-md p-4">
    <h2 class="text-xl font-semibold mb-4">🔔 告警历史</h2>
    
    <div v-if="!alerts || alerts.length === 0" class="py-8 text-center text-gray-500">
      暂无告警历史记录
    </div>
    
    <div v-else class="space-y-4">
      <div v-for="(alert, index) in alerts" :key="index" 
           class="border-l-4 p-4 rounded-md shadow-sm"
           :class="getAlertClass(alert.signal_type)">
        <div class="flex justify-between">
          <span class="font-medium">{{ alert.stock_name || alert.stock_code }}</span>
          <span class="text-sm text-gray-500">{{ formatDate(alert.timestamp) }}</span>
        </div>
        <p class="mt-1">{{ alert.message }}</p>
        <div class="mt-2 flex gap-2">
          <span class="px-2 py-0.5 rounded-full text-xs"
                :class="getSignalClass(alert.signal_type)">
            {{ alert.signal_type }}
          </span>
          <span v-if="alert.price" class="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs">
            价格: {{ alert.price }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlertHistoryPanel',
  props: {
    alerts: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const formatDate = (timestamp) => {
      if (!timestamp) return ''
      
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const getAlertClass = (type) => {
      if (!type) return 'border-gray-300'
      
      if (type.includes('buy') || type.includes('上涨')) {
        return 'border-red-500 bg-red-50'
      } else if (type.includes('sell') || type.includes('下跌')) {
        return 'border-green-500 bg-green-50'
      } else {
        return 'border-blue-500 bg-blue-50'
      }
    }
    
    const getSignalClass = (type) => {
      if (!type) return 'bg-gray-100 text-gray-700'
      
      if (type.includes('buy') || type.includes('上涨')) {
        return 'bg-red-100 text-red-800'
      } else if (type.includes('sell') || type.includes('下跌')) {
        return 'bg-green-100 text-green-800'
      } else {
        return 'bg-blue-100 text-blue-800'
      }
    }
    
    return {
      formatDate,
      getAlertClass,
      getSignalClass
    }
  }
}
</script> 