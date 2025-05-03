<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div 
      class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-y-auto"
    >
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium">监控结果</h3>
          <button 
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="!results || Object.keys(results).length === 0" class="py-8 text-center text-gray-500">
          暂无监控结果数据
        </div>
        
        <div v-else>
          <!-- 监控统计信息 -->
          <div class="mb-6 bg-blue-50 p-4 rounded-md">
            <h4 class="font-medium text-blue-700 mb-2">监控统计</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-white p-3 rounded shadow-sm">
                <div class="text-sm text-gray-500">监控股票数</div>
                <div class="text-xl font-bold">{{ results.stats?.total_stocks || 0 }}</div>
              </div>
              <div class="bg-white p-3 rounded shadow-sm">
                <div class="text-sm text-gray-500">触发告警数</div>
                <div class="text-xl font-bold">{{ results.stats?.alert_count || 0 }}</div>
              </div>
              <div class="bg-white p-3 rounded shadow-sm">
                <div class="text-sm text-gray-500">执行耗时</div>
                <div class="text-xl font-bold">{{ results.stats?.execution_time || 0 }}秒</div>
              </div>
              <div class="bg-white p-3 rounded shadow-sm">
                <div class="text-sm text-gray-500">执行时间</div>
                <div class="text-sm">{{ formatRunTime(results.stats?.run_time) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 告警列表 -->
          <div v-if="results.alerts && results.alerts.length > 0" class="mb-6">
            <h4 class="font-medium mb-2">告警信息</h4>
            <div class="space-y-2">
              <div v-for="(alert, index) in results.alerts" :key="index" 
                   class="border-l-4 p-3 rounded-md shadow-sm"
                   :class="getAlertClass(alert.signal_type)">
                <div class="flex justify-between">
                  <span class="font-medium">{{ alert.stock_name || alert.stock_code }}</span>
                  <span class="text-sm text-gray-500">{{ formatDate(alert.timestamp) }}</span>
                </div>
                <p class="mt-1">{{ alert.message }}</p>
              </div>
            </div>
          </div>
          
          <!-- 执行详情 -->
          <div v-if="results.details && results.details.length > 0" class="mb-6">
            <h4 class="font-medium mb-2">执行详情</h4>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                    <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">监控类型</th>
                    <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">结果</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(detail, index) in results.details" :key="index">
                    <td class="px-3 py-2 whitespace-nowrap text-sm">
                      {{ detail.stock_name || detail.stock_code }}
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm">
                      {{ detail.monitor_type }}
                    </td>
                    <td class="px-3 py-2 whitespace-nowrap text-sm">
                      <span 
                        class="px-2 py-0.5 rounded-full text-xs"
                        :class="detail.triggered ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
                      >
                        {{ detail.triggered ? '已触发' : '未触发' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex justify-end">
          <button 
            @click="$emit('close')"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'

export default {
  name: 'MonitorResultsModal',
  props: {
    results: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    // 点击外部关闭模态窗
    const handleOutsideClick = (event) => {
      const modalContent = document.querySelector('.bg-white.rounded-lg')
      if (modalContent && !modalContent.contains(event.target)) {
        emit('close')
      }
    }
    
    onMounted(() => {
      document.addEventListener('mousedown', handleOutsideClick)
    })
    
    onUnmounted(() => {
      document.removeEventListener('mousedown', handleOutsideClick)
    })
    
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
    
    const formatRunTime = (timestamp) => {
      if (!timestamp) return ''
      
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN')
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
    
    return {
      formatDate,
      formatRunTime,
      getAlertClass
    }
  }
}
</script> 