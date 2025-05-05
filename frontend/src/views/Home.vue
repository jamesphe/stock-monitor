<template>
  <main class="container mx-auto px-4 py-6">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- 左侧边栏 -->
      <div class="w-full lg:w-1/3 space-y-6">
        <!-- 系统配置面板 -->
        <ConfigPanel :config="config" @save="saveConfig" />
        
        <!-- 添加监控面板 -->
        <AddMonitorPanel :stocks="config.stocks" @add-stock="addStock" />
      </div>

      <!-- 右侧主内容 -->
      <div class="w-full lg:w-2/3 space-y-6">
        <!-- 已监控股票列表 -->
        <StockListPanel 
          :stocks="config.stocks" 
          :isRunningMonitor="isRunningMonitor"
          @select-stock="selectStock"
          @delete-stock="deleteStock"
          @run-monitoring="runMonitoring"
          @show-chart="showStockChart"
          @set-chart-type="setChartType"
          @run-strategy="runSingleStrategy"
        />

        <!-- 股票图表区域 -->
        <StockChartPanel 
          v-if="selectedStock" 
          :stock="selectedStock" 
          :chartData="chartData" 
          :chartType="chartType"
        />

        <!-- 告警历史 -->
        <AlertHistoryPanel :alerts="alerts" />
      </div>
    </div>

    <!-- 监控结果模态窗口 -->
    <MonitorResultsModal 
      v-if="showMonitorResults" 
      :results="monitorResults"
      @close="showMonitorResults = false"
    />
  </main>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { 
  getConfig, 
  saveConfig as apiSaveConfig, 
  evaluateRules, 
  getStockData,
  evaluateSingleStrategy 
} from '../api/stock'
import ConfigPanel from '../components/ConfigPanel.vue'
import AddMonitorPanel from '../components/AddMonitorPanel.vue'
import StockListPanel from '../components/StockListPanel.vue'
import StockChartPanel from '../components/StockChartPanel.vue'
import AlertHistoryPanel from '../components/AlertHistoryPanel.vue'
import MonitorResultsModal from '../components/MonitorResultsModal.vue'

export default {
  name: 'HomePage',
  components: {
    ConfigPanel,
    AddMonitorPanel,
    StockListPanel,
    StockChartPanel,
    AlertHistoryPanel,
    MonitorResultsModal
  },
  setup() {
    const config = reactive({
      wecom_webhook: '',
      stocks: []
    })
    const selectedStock = ref(null)
    const chartData = ref([])
    const isRunningMonitor = ref(false)
    const showMonitorResults = ref(false)
    const monitorResults = ref([])
    const alerts = ref([])
    const chartType = ref('candlestick') // 默认K线图

    // 加载配置
    const loadConfig = async () => {
      try {
        const data = await getConfig()
        config.wecom_webhook = data.wecom_webhook || ''
        config.stocks = data.stocks || []
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    }

    // 保存配置
    const saveConfig = async () => {
      try {
        await apiSaveConfig(config)
      } catch (error) {
        console.error('保存配置失败:', error)
      }
    }

    // 添加股票
    const addStock = (stock) => {
      config.stocks.push(stock)
      saveConfig()
    }

    // 删除股票
    const deleteStock = (index) => {
      config.stocks.splice(index, 1)
      saveConfig()
    }

    // 选择股票
    const selectStock = async (stock) => {
      selectedStock.value = stock
      
      try {
        // 加载股票数据
        const data = await getStockData(stock.code)
        chartData.value = data
      } catch (error) {
        console.error('获取股票数据失败:', error)
        chartData.value = []
      }
    }
    
    // 显示股票图表
    const showStockChart = async (stock) => {
      selectedStock.value = stock
      
      try {
        // 加载股票数据
        const data = await getStockData(stock.code)
        chartData.value = data
      } catch (error) {
        console.error('获取股票数据失败:', error)
        chartData.value = []
      }
    }
    
    // 设置图表类型
    const setChartType = (type) => {
      chartType.value = type
    }

    // 执行监控
    const runMonitoring = async () => {
      if (isRunningMonitor.value) return
      
      isRunningMonitor.value = true
      try {
        const results = await evaluateRules(config)
        monitorResults.value = results
        showMonitorResults.value = true
        
        // 更新告警历史
        if (results && results.alerts) {
          alerts.value = [...results.alerts, ...alerts.value].slice(0, 50)
        }
      } catch (error) {
        console.error('监控执行失败:', error)
      } finally {
        isRunningMonitor.value = false
      }
    }
    
    // 执行单个策略
    const runSingleStrategy = async ({ stock, strategy }, callback) => {
      try {
        const result = await evaluateSingleStrategy({ stock, strategy })
        // 如果策略执行成功触发，添加到告警历史
        if (result.status === 'success') {
          const alertData = {
            stock_code: stock.code,
            stock_name: stock.name,
            strategy_name: strategy.strategy_name,
            strategy_type: strategy.strategy_type,
            trigger_time: new Date().toLocaleString(),
            trigger_reason: result.details || '策略条件满足'
          }
          alerts.value = [alertData, ...alerts.value].slice(0, 50)
        }
        // 调用回调函数返回结果
        if (typeof callback === 'function') {
          callback(result)
        }
        return result
      } catch (error) {
        console.error('执行单个策略失败:', error)
        const errorResult = {
          status: 'error',
          message: '执行策略失败',
          details: error.message || '网络错误或服务器异常'
        }
        if (typeof callback === 'function') {
          callback(errorResult)
        }
        return errorResult
      }
    }

    onMounted(() => {
      loadConfig()
    })

    return {
      config,
      selectedStock,
      chartData,
      chartType,
      isRunningMonitor,
      showMonitorResults,
      monitorResults,
      alerts,
      saveConfig,
      addStock,
      deleteStock,
      selectStock,
      showStockChart,
      setChartType,
      runMonitoring,
      runSingleStrategy
    }
  }
}
</script> 