<template>
  <div class="mb-3 p-4 rounded-lg bg-white border border-gray-200 shadow-md">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-bold text-gray-800 flex items-center">
        <span class="p-1.5 bg-blue-100 text-blue-700 rounded-md mr-2 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4" />
          </svg>
        </span>
        MACD检查条件
      </h3>
      <div class="px-2.5 py-1.5 rounded-full text-xs font-medium"
        :class="macdData.pass ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
        {{ macdData.pass ? '已满足' : '未满足' }}
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="p-3 bg-gray-50 rounded-lg border border-gray-100">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-medium text-gray-500">日线MACD</span>
          <span class="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">日线</span>
        </div>
        
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">MACD值:</span>
            <span class="font-medium" :class="dailyMacd >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ dailyMacd }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">信号线:</span>
            <span class="font-medium" :class="dailySignal >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ dailySignal }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">柱状图:</span>
            <span class="font-medium" :class="dailyHistogram >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ dailyHistogram }}
            </span>
          </div>
        </div>
        
        <div class="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div class="h-full" 
            :class="dailyHistogram >= 0 ? 'bg-green-500' : 'bg-red-500'"
            :style="{width: `${Math.min(Math.abs(dailyHistogram) * 100, 100)}%`}">
          </div>
        </div>
      </div>
      
      <div class="p-3 bg-gray-50 rounded-lg border border-gray-100">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-medium text-gray-500">分钟MACD</span>
          <span class="text-xs px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full">5分钟</span>
        </div>
        
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">MACD值:</span>
            <span class="font-medium" :class="minuteMacd >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ minuteMacd }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">信号线:</span>
            <span class="font-medium" :class="minuteSignal >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ minuteSignal }}
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">柱状图:</span>
            <span class="font-medium" :class="minuteHistogram >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ minuteHistogram }}
            </span>
          </div>
        </div>
        
        <div class="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div class="h-full" 
            :class="minuteHistogram >= 0 ? 'bg-green-500' : 'bg-red-500'"
            :style="{width: `${Math.min(Math.abs(minuteHistogram) * 100, 100)}%`}">
          </div>
        </div>
      </div>
    </div>

    <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>MACD指标中，柱状图由负转正可能表示上涨趋势，由正转负可能表示下跌趋势</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MacdCheckCard',
  props: {
    macdData: {
      type: Object,
      required: true
    }
  },
  computed: {
    dailyMacd() {
      const parts = this.macdData.description.split(',')[0].split(':');
      return parseFloat(parts[1]);
    },
    dailySignal() {
      const parts = this.macdData.description.split(',')[1].split(':');
      return parseFloat(parts[1]);
    },
    dailyHistogram() {
      const parts = this.macdData.description.split(',')[2].split(':');
      return parseFloat(parts[1]);
    },
    minuteMacd() {
      const parts = this.macdData.description.split('\n')[1].split(',')[0].split(':');
      return parseFloat(parts[1]);
    },
    minuteSignal() {
      const parts = this.macdData.description.split('\n')[1].split(',')[1].split(':');
      return parseFloat(parts[1]);
    },
    minuteHistogram() {
      const parts = this.macdData.description.split('\n')[1].split(',')[2].split(':');
      return parseFloat(parts[1]);
    }
  }
}
</script> 