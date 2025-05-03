<template>
  <div class="bg-white rounded-lg shadow-md p-4">
    <h2 class="text-xl font-semibold mb-4">⚙️ 系统配置</h2>
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700">
        企业微信机器人Webhook
        <div class="mt-1 relative rounded-md shadow-sm">
          <input 
            type="password" 
            v-model="localConfig.wecom_webhook" 
            @change="updateConfig"
            class="block w-full pr-10 border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" 
            placeholder="填入企业微信机器人的Webhook地址" 
          >
        </div>
        <p class="mt-1 text-xs text-gray-500">填入企业微信机器人的Webhook地址，用于接收告警通知</p>
      </label>
    </div>
  </div>
</template>

<script>
import { reactive, watch } from 'vue'

export default {
  name: 'ConfigPanel',
  props: {
    config: {
      type: Object,
      required: true
    }
  },
  emits: ['save'],
  setup(props, { emit }) {
    const localConfig = reactive({
      wecom_webhook: ''
    })

    // 监听props变化，更新本地配置
    watch(() => props.config, (newConfig) => {
      localConfig.wecom_webhook = newConfig.wecom_webhook || ''
    }, { immediate: true, deep: true })

    const updateConfig = () => {
      emit('save', {
        ...props.config,
        wecom_webhook: localConfig.wecom_webhook
      })
    }

    return {
      localConfig,
      updateConfig
    }
  }
}
</script> 