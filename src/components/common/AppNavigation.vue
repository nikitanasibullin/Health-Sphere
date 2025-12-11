<template>
  <nav class="bg-white border-b shadow-sm sticky top-16 z-30">
    <div class="container mx-auto px-6">
      <div class="flex space-x-1 overflow-x-auto">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="$emit('tab-change', tab.id)"
          :class="[
            'px-6 py-4 font-semibold transition whitespace-nowrap', 
            activeTab === tab.id 
              ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
              : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
          ]"
        >
          <i :class="[tab.icon, 'mr-2']"></i>
          {{ tab.name }}
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AppNavigation',
  props: {
    tabs: {
      type: Array,
      required: true
    },
    activeTab: {
      type: String,
      required: true
    }
  },
  emits: ['tab-change']
}
</script>