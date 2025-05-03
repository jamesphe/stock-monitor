<template>
  <div class="bg-white rounded-lg shadow-md p-4">
    <h2 class="text-xl font-semibold mb-4">📋 添加监控</h2>
    
    <form @submit.prevent="addStock">
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700">
          股票代码
          <div class="mt-1">
            <input 
              type="text" 
              v-model="stockForm.code"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" 
              placeholder="如: 000001 或 sh000001" 
              required
            >
          </div>
          <p class="mt-1 text-xs text-gray-500">输入股票代码，可选添加sh/sz前缀</p>
        </label>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700">
          股票名称
          <div class="mt-1">
            <input 
              type="text" 
              v-model="stockForm.name"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" 
              placeholder="可选，如: 平安银行" 
            >
          </div>
        </label>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700">
          监控类型
          <div class="mt-1">
            <select 
              v-model="stockForm.monitor_type"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="rsi_cross">RSI交叉</option>
              <option value="ma_cross">均线交叉</option>
              <option value="macd_cross">MACD交叉</option>
              <option value="price_breakout">价格突破</option>
              <option value="volume_price_divergence">量价背离</option>
            </select>
          </div>
        </label>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700">
          价格线
          <div class="mt-1">
            <input 
              type="number" 
              v-model.number="stockForm.price_level"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" 
              placeholder="如: 10.5" 
              step="0.01"
            >
          </div>
          <p class="mt-1 text-xs text-gray-500">对于价格相关监控，设置关注的价格线</p>
        </label>
      </div>
      
      <div class="flex justify-end">
        <button 
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          添加监控
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { reactive } from 'vue'

export default {
  name: 'AddMonitorPanel',
  props: {
    stocks: {
      type: Array,
      required: true
    }
  },
  emits: ['add-stock'],
  setup(props, { emit }) {
    const stockForm = reactive({
      code: '',
      name: '',
      monitor_type: 'rsi_cross',
      price_level: '',
      parameters: {}
    })

    const addStock = () => {
      // 构建股票配置对象
      const newStock = {
        code: stockForm.code,
        name: stockForm.name || stockForm.code,
        monitor_type: stockForm.monitor_type,
        parameters: { ...stockForm.parameters }
      }
      
      // 对于需要价格线的监控类型，添加价格参数
      if (['price_breakout'].includes(stockForm.monitor_type) && stockForm.price_level) {
        newStock.parameters.price_level = stockForm.price_level
      }
      
      emit('add-stock', newStock)
      
      // 重置表单
      stockForm.code = ''
      stockForm.name = ''
      stockForm.price_level = ''
    }

    return {
      stockForm,
      addStock
    }
  }
}
</script> 