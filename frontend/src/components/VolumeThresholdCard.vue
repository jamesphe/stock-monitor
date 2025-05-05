<template>
  <div class="mb-3 p-4 rounded-lg bg-white border border-gray-200 shadow-md">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-bold text-gray-800 flex items-center">
        <span class="p-1.5 bg-orange-100 text-orange-700 rounded-md mr-2 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </span>
        成交量阈值条件
      </h3>
      <div class="px-2.5 py-1.5 rounded-full text-xs font-medium"
        :class="volumeData.pass ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
        {{ volumeData.pass ? '已满足' : '未满足' }}
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="p-3 bg-gray-50 rounded border border-gray-100">
        <div class="text-xs text-gray-500 mb-1">目标成交量</div>
        <div class="text-lg font-bold text-purple-600">
          {{ formatVolume(volumeData.target_threshold) }}
        </div>
      </div>
      <div class="p-3 bg-gray-50 rounded border border-gray-100">
        <div class="text-xs text-gray-500 mb-1">当前成交量</div>
        <div class="text-lg font-bold"
          :class="volumeData.pass ? 'text-green-600' : 'text-red-600'">
          {{ formatVolume(volumeData.current_volume) }}
        </div>
      </div>
    </div>
    
    <div class="p-3 bg-gray-50 rounded-lg mb-2">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">成交量对比</span>
        <span class="text-xs px-2 py-0.5 rounded" 
          :class="volumeDifferencePercent >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
          {{ volumeDifferencePercent >= 0 ? '高于' : '低于' }} {{ Math.abs(volumeDifferencePercent).toFixed(2) }}%
        </span>
      </div>
      
      <div class="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full" 
          :class="volumeDifferencePercent >= 0 ? 'bg-green-500' : 'bg-red-500'"
          :style="volumeBarStyle">
        </div>
      </div>
    </div>
    
    <div class="p-3 bg-gray-50 rounded text-sm text-gray-700 whitespace-pre-line">
      {{ volumeData.description || '无详细描述' }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'VolumeThresholdCard',
  props: {
    volumeData: {
      type: Object,
      required: true
    }
  },
  computed: {
    volumeDifferencePercent() {
      const currentVolume = parseFloat(this.volumeData.current_volume);
      const targetVolume = parseFloat(this.volumeData.target_threshold);
      if (!currentVolume || !targetVolume) return 0;
      
      return ((currentVolume - targetVolume) / targetVolume) * 100;
    },
    volumeBarStyle() {
      const percent = Math.min(Math.abs(this.volumeDifferencePercent), 100); // 限制最大显示为100%
      return {
        width: `${percent}%`
      };
    }
  },
  methods: {
    formatVolume(volume) {
      if (!volume && volume !== 0) return '-';
      
      const num = parseFloat(volume);
      if (num >= 100000000) {
        return (num / 100000000).toFixed(2) + '亿';
      } else if (num >= 10000) {
        return (num / 10000).toFixed(2) + '万';
      } else {
        return num.toFixed(0);
      }
    }
  }
}
</script> 