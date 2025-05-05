<template>
  <div class="mb-3 p-4 rounded-lg bg-white border border-gray-200 shadow-md">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-bold text-gray-800 flex items-center">
        <span class="p-1.5 bg-purple-100 text-purple-700 rounded-md mr-2 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </span>
        RSI检查条件
      </h3>
      <div class="px-2.5 py-1.5 rounded-full text-xs font-medium"
        :class="rsiData.pass ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
        {{ rsiData.pass ? '已满足' : '未满足' }}
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="p-3 bg-gray-50 rounded-lg border border-gray-100">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-medium text-gray-500">日线RSI(14)</span>
          <span class="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">日线</span>
        </div>
        
        <div class="mt-1">
          <div class="flex justify-between mb-1">
            <span class="text-xs text-red-600">超买(70)</span>
            <span class="text-xs text-green-600">超卖(30)</span>
          </div>
          <div class="h-4 w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full relative">
            <div class="absolute top-0 left-0 right-0 h-full flex items-center justify-center">
              <div class="absolute w-full h-0.5 bg-gray-300"></div>
            </div>
            <div class="absolute h-full w-px bg-gray-500 top-0" style="left: 30%"></div>
            <div class="absolute h-full w-px bg-gray-500 top-0" style="left: 70%"></div>
            <div class="absolute top-0 h-full w-2 bg-blue-600 rounded-full transform -translate-x-1/2"
              :style="{left: `${dailyRsi}%`}">
            </div>
          </div>
          <div class="text-center mt-1.5">
            <span class="text-base font-bold"
              :class="[
                dailyRsi > 70 ? 'text-red-600' : 
                dailyRsi < 30 ? 'text-green-600' : 
                'text-gray-800'
              ]">
              {{ dailyRsi }}
            </span>
          </div>
        </div>
        
        <div class="mt-2 text-xs text-gray-600">
          <div>最近3个值: <span class="font-medium">{{ dailyRecentValues }}</span></div>
        </div>
      </div>
      
      <div class="p-3 bg-gray-50 rounded-lg border border-gray-100">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-medium text-gray-500">5分钟RSI(14)</span>
          <span class="text-xs px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full">5分钟</span>
        </div>
        
        <div class="mt-1">
          <div class="flex justify-between mb-1">
            <span class="text-xs text-red-600">超买(70)</span>
            <span class="text-xs text-green-600">超卖(30)</span>
          </div>
          <div class="h-4 w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full relative">
            <div class="absolute top-0 left-0 right-0 h-full flex items-center justify-center">
              <div class="absolute w-full h-0.5 bg-gray-300"></div>
            </div>
            <div class="absolute h-full w-px bg-gray-500 top-0" style="left: 30%"></div>
            <div class="absolute h-full w-px bg-gray-500 top-0" style="left: 70%"></div>
            <div class="absolute top-0 h-full w-2 bg-purple-600 rounded-full transform -translate-x-1/2"
              :style="{left: `${minuteRsi}%`}">
            </div>
          </div>
          <div class="text-center mt-1.5">
            <span class="text-base font-bold"
              :class="[
                minuteRsi > 70 ? 'text-red-600' : 
                minuteRsi < 30 ? 'text-green-600' : 
                'text-gray-800'
              ]">
              {{ minuteRsi }}
            </span>
          </div>
        </div>
        
        <div class="mt-2 text-xs text-gray-600">
          <div>最近3个值: <span class="font-medium">{{ minuteRecentValues }}</span></div>
        </div>
      </div>
    </div>

    <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>RSI值大于70被视为超买，RSI值小于30被视为超卖，这可能表示价格即将反转</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RsiCheckCard',
  props: {
    rsiData: {
      type: Object,
      required: true
    }
  },
  computed: {
    dailyRsi() {
      const parts = this.rsiData.description.split(',')[0].split(':');
      return parseFloat(parts[1]);
    },
    dailyRecentValues() {
      const text = this.rsiData.description.split(':')[2];
      return text.trim();
    },
    minuteRsi() {
      const parts = this.rsiData.description.split('\n')[1].split(',')[0].split(':');
      return parseFloat(parts[1]);
    },
    minuteRecentValues() {
      const text = this.rsiData.description.split('\n')[1].split(':')[2];
      return text.trim();
    }
  }
}
</script> 