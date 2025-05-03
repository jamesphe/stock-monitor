<template>
  <div class="bg-gray-100 font-sans min-h-screen">
    <!-- 头部导航 -->
    <header class="bg-blue-600 text-white shadow-md">
      <div class="container mx-auto px-4 py-4">
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold">📈 股票信号监控系统</h1>
          <div class="flex items-center space-x-2">
            <span v-if="!akshareAvailable" class="bg-yellow-500 text-black px-2 py-1 rounded text-sm">
              ⚠️ AKshare未安装，使用备选数据源
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <router-view/>

    <!-- 底部 -->
    <footer class="bg-gray-800 text-white py-4">
      <div class="container mx-auto px-4 text-center text-sm">
        <p>📈 股票信号监控系统 | 基于Vue.js和TailwindCSS构建</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getApiStatus } from './api/status'

export default {
  name: 'App',
  setup() {
    const akshareAvailable = ref(true)

    onMounted(async () => {
      try {
        const status = await getApiStatus()
        akshareAvailable.value = status.akshare_available
      } catch (error) {
        console.error('获取API状态失败:', error)
        akshareAvailable.value = false
      }
    })

    return {
      akshareAvailable
    }
  }
}
</script>

<style>
/* 全局样式将通过TailwindCSS导入 */
</style> 