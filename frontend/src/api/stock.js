import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5001/api'

// 获取股票数据
export const getStockData = async (code, period = 'daily', count = 120) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stock_data`, {
      params: { code, period, count }
    })
    return response.data
  } catch (error) {
    console.error('获取股票数据失败:', error)
    throw error
  }
}

// 获取配置
export const getConfig = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/config`)
    return response.data
  } catch (error) {
    console.error('获取配置失败:', error)
    throw error
  }
}

// 保存配置
export const saveConfig = async (config) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/config`, config)
    return response.data
  } catch (error) {
    console.error('保存配置失败:', error)
    throw error
  }
}

// 执行监控评估
export const evaluateRules = async (config) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/evaluate`, config)
    return response.data
  } catch (error) {
    console.error('规则评估失败:', error)
    throw error
  }
} 