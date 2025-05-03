import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5001/api'

export const getApiStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/status`)
    return response.data
  } catch (error) {
    console.error('API状态请求失败:', error)
    throw error
  }
} 