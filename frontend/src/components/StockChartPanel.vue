<template>
  <div class="bg-white rounded-lg shadow-md p-4 relative">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">
        <span>{{ stock.name || stock.code }}</span> 数据图表
      </h2>
      
      <!-- 图表类型选择 -->
      <div class="flex space-x-2">
        <button 
          @click="setChartType('candlestick')" 
          class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-200"
          :class="chartType === 'candlestick' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          K线图
        </button>
        <button 
          @click="setChartType('realtime')" 
          class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-200"
          :class="chartType === 'realtime' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          分时走势图
        </button>
      </div>
    </div>
  
    
    <div v-show="!chartData || chartData.length === 0" class="h-80 flex items-center justify-center text-gray-500">
      暂无数据，或数据加载中...
    </div>
    <div v-show="loading" class="h-80 flex items-center justify-center">
      <div class="flex flex-col items-center">
        <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="mt-2 text-sm text-gray-500">加载图表中...</span>
      </div>
    </div>
    <div v-show="!loading && chartData && chartData.length > 0" class="h-80">
      <div ref="chartDom" class="w-full h-full min-h-[320px]" style="min-height:320px;"></div>
      
      <!-- 调试信息：显示遇到的错误 -->
      <div v-if="error" class="mt-4 p-2 bg-red-100 text-red-700 rounded">
        <p class="font-bold">错误信息:</p>
        <pre class="text-xs overflow-auto">{{ error }}</pre>
      </div>
      <!-- 自定义tooltip -->
      <div
        v-show="tooltip.visible"
        :style="{
          position: 'absolute',
          left: tooltip.left + 'px',
          top: tooltip.top + 'px',
          background: 'rgba(0,0,0,0.7)',
          color: '#fff',
          padding: '6px 10px',
          borderRadius: '4px',
          pointerEvents: 'none',
          zIndex: 10,
          fontSize: '12px',
          minWidth: '120px',
        }"
      >
        <template v-if="chartType === 'candlestick' && tooltip.data">
          <div>日期: {{ tooltip.data.time }}</div>
          <div>开盘: {{ tooltip.data.open }}</div>
          <div>收盘: {{ tooltip.data.close }}</div>
          <div>最高: {{ tooltip.data.high }}</div>
          <div>最低: {{ tooltip.data.low }}</div>
        </template>
        <template v-else-if="chartType === 'realtime' && tooltip.data">
          <div>日期: {{ tooltip.data.time }}</div>
          <div>价格: {{ tooltip.data.value }}</div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  stock: {
    type: Object,
    required: true
  },
  chartData: {
    type: Array,
    default: () => []
  },
  chartType: {
    type: String,
    default: 'candlestick'
  }
})
const emit = defineEmits(['update:chartType'])

const loading = ref(false)
const error = ref(null)
const chartDom = ref(null)
let chart = null
let series = null

const tooltip = ref({
  visible: false,
  left: 0,
  top: 0,
  data: null
})

function setChartType(type) {
  emit('update:chartType', type)
}

function clearChart() {
  if (chart) {
    chart.remove();
    chart = null;
    series = null;
  }
  if (chartDom.value) {
    chartDom.value.innerHTML = '';
  }
  tooltip.value.visible = false;
}

function subscribeTooltip(chart) {
  chart.subscribeCrosshairMove(param => {
    if (!param || !param.point || !param.time) {
      tooltip.value.visible = false
      return
    }
    // 用 param.time 在原始数据中查找
    const dataItem = props.chartData.find(item => item.date === param.time)
    if (!dataItem) {
      tooltip.value.visible = false
      return
    }
    tooltip.value.visible = true
    // 计算tooltip位置，防止溢出
    const chartRect = chartDom.value.getBoundingClientRect()
    let left = param.point.x + 20
    let top = param.point.y
    if (left > chartRect.width - 140) left = chartRect.width - 140
    if (top > chartRect.height - 100) top = chartRect.height - 100
    tooltip.value.left = left
    tooltip.value.top = top
    // K线和分时分别赋值
    if (props.chartType === 'candlestick') {
      tooltip.value.data = {
        time: dataItem.date,
        open: dataItem.open,
        close: dataItem.close,
        high: dataItem.high,
        low: dataItem.low
      }
    } else {
      tooltip.value.data = {
        time: dataItem.date,
        value: dataItem.close
      }
    }
  })
}

function renderChart() {
  clearChart()
  nextTick(() => {
    if (!chartDom.value) {
      console.warn('chartDom.value is null, skip renderChart')
      loading.value = false
      return
    }
    if (!props.chartData || props.chartData.length === 0) {
      loading.value = false
      return
    }
    loading.value = true
    error.value = null
    try {
      const width = chartDom.value.clientWidth || 600
      const height = chartDom.value.clientHeight || 320
      console.log('chartDom size:', width, height)
      console.log('chartData example:', props.chartData[0])
      chart = createChart(chartDom.value, {
        width,
        height,
        layout: { background: { type: 'solid', color: '#fff' } },
        grid: { vertLines: { color: '#eee' }, horzLines: { color: '#eee' } },
        timeScale: { timeVisible: true, secondsVisible: false },
        rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.1 } }
      })
      if (props.chartType === 'candlestick') {
        series = chart.addCandlestickSeries()
        // 转换数据格式
        const data = props.chartData.map(item => ({
          time: item.date,
          open: Number(item.open),
          high: Number(item.high),
          low: Number(item.low),
          close: Number(item.close)
        }))
        console.log('candlestick data:', data)
        series.setData(data)
      } else {
        series = chart.addLineSeries({ color: '#d81e06', lineWidth: 2 })
        const data = props.chartData.map(item => ({
          time: item.date,
          value: Number(item.close)
        }))
        console.log('line data:', data)
        series.setData(data)
      }
      subscribeTooltip(chart)
      // 只resize一次，避免多次重建
      window.addEventListener('resize', handleResize)
    } catch (e) {
      error.value = e.message
      console.error('图表渲染错误:', e)
    } finally {
      loading.value = false
    }
  })
}

function handleResize() {
  if (chart && chartDom.value) {
    chart.resize(chartDom.value.clientWidth, chartDom.value.clientHeight)
  }
}

watch(() => [props.chartData, props.chartType], renderChart, { deep: true })

onMounted(() => {
  renderChart()
})
onUnmounted(() => {
  clearChart()
  window.removeEventListener('resize', handleResize)
})
</script> 