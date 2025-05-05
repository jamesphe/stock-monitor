<template>
  <div class="mb-4 p-5 rounded-xl bg-white border border-gray-200 shadow-lg hover:shadow-xl transition-shadow duration-300">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-bold text-gray-800 flex items-center">
        <span class="p-2 bg-indigo-100 text-indigo-700 rounded-lg mr-3 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
        <span class="text-lg">{{ getRuleTitle() }}</span>
      </h3>
      <div class="px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-300"
        :class="priceData.pass ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-yellow-100 text-yellow-700 border border-yellow-200'">
        {{ priceData.pass ? '已满足' : '未满足' }}
      </div>
    </div>
    
    <div class="grid grid-cols-1 gap-4 mb-4" :class="{'grid-cols-2': !hasMultipleThresholds}">
      <!-- 单一目标价格 -->
      <div v-if="!hasMultipleThresholds" class="p-4 bg-gray-50 rounded-lg border border-gray-100 hover:border-blue-200 transition-colors duration-200">
        <div class="text-sm text-gray-500 mb-1.5">{{ getThresholdLabel() }}</div>
        <div class="text-xl font-bold text-blue-600 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          {{ priceData.target_level }}
        </div>
      </div>
      
      <!-- 上下阈值 -->
      <template v-if="hasMultipleThresholds">
        <div v-if="priceData.high_level" class="p-4 bg-green-50 rounded-lg border border-green-100 hover:border-green-300 transition-colors duration-200">
          <div class="text-sm text-gray-500 mb-1.5">上阈值</div>
          <div class="text-xl font-bold text-green-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
            {{ priceData.high_level }}
          </div>
        </div>
        
        <div v-if="priceData.low_level" class="p-4 bg-red-50 rounded-lg border border-red-100 hover:border-red-300 transition-colors duration-200">
          <div class="text-sm text-gray-500 mb-1.5">下阈值</div>
          <div class="text-xl font-bold text-red-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            {{ priceData.low_level }}
          </div>
        </div>
      </template>
      
      <!-- 当前价格 -->
      <div class="p-4 bg-gray-50 rounded-lg border border-gray-100 hover:border-green-200 transition-colors duration-200">
        <div class="text-sm text-gray-500 mb-1.5">当前价格</div>
        <div class="text-xl font-bold flex items-center"
          :class="priceData.pass ? 'text-green-600' : 'text-red-600'">
          <svg v-if="priceData.pass" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {{ priceData.daily_price }}
        </div>
      </div>
    </div>
    
    <div class="p-4 bg-gray-50 rounded-lg mb-4 hover:bg-gray-100 transition-colors duration-200">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-700">价格对比</span>
        <span class="text-sm px-3 py-1 rounded-full" 
          :class="priceDifferencePercent >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
          {{ priceDifferencePercent >= 0 ? '高于' : '低于' }} {{ Math.abs(priceDifferencePercent).toFixed(2) }}%
        </span>
      </div>
      
      <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all duration-500" 
          :class="priceDifferencePercent >= 0 ? 'bg-green-500' : 'bg-red-500'"
          :style="priceBarStyle">
        </div>
      </div>
    </div>
    
    <div class="p-4 bg-gray-50 rounded-lg text-sm text-gray-700 whitespace-pre-line border-l-4"
      :class="priceData.pass ? 'border-green-400' : 'border-yellow-400'">
      <div class="font-medium mb-1 text-gray-800">详细说明：</div>
      {{ priceData.description || '无详细描述' }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'PriceThresholdCard',
  props: {
    priceData: {
      type: Object,
      required: true
    }
  },
  computed: {
    priceDifferencePercent() {
      const currentPrice = parseFloat(this.priceData.daily_price);
      const targetPrice = parseFloat(this.priceData.target_level);
      if (!currentPrice || !targetPrice) return 0;
      
      return ((currentPrice - targetPrice) / targetPrice) * 100;
    },
    priceBarStyle() {
      const percent = Math.min(Math.abs(this.priceDifferencePercent), 20) * 5; // 最大20%差异显示为100%宽度
      return {
        width: `${percent}%`
      };
    },
    hasMultipleThresholds() {
      return this.priceData.high_level || this.priceData.low_level;
    }
  },
  methods: {
    getRuleTitle() {
      if (this.priceData.is_buy_strategy) {
        return '价格上涨突破条件';
      } else if (this.priceData.is_sell_strategy) {
        return '价格下跌突破条件';
      } else if (this.hasMultipleThresholds) {
        return '价格区间突破条件';
      } else {
        return '价格阈值条件';
      }
    },
    getThresholdLabel() {
      if (this.priceData.is_buy_strategy) {
        return '买入阈值';
      } else if (this.priceData.is_sell_strategy) {
        return '卖出阈值';
      } else {
        return '目标价格';
      }
    }
  }
}
</script>

<style scoped>
.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style> 