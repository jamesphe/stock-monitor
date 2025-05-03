<template>
  <div class="container mx-auto px-4 py-8">
    <div class="bg-white rounded-lg shadow-md p-6">
      <h1 class="text-2xl font-bold mb-4">关于股票信号监控系统</h1>
      <p class="mb-4">股票信号监控系统是一个帮助投资者追踪股票价格和关键技术指标的工具。</p>
      <p class="mb-4">本系统使用Vue.js构建前端界面，后端采用Flask API提供数据服务。</p>
      <p class="mb-4">主要功能：</p>
      <ul class="list-disc pl-8 mb-4">
        <li>自定义股票监控列表</li>
        <li>支持多种技术指标：MA、MACD、RSI等</li>
        <li>价格突破、回调监控</li>
        <li>成交量异常提醒</li>
        <li>企业微信推送告警</li>
      </ul>
      <p class="mb-4">数据来源：优先使用AKshare获取实时行情，备选使用新浪财经API。</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script> 