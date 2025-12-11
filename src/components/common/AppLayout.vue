<template>
  <!-- Only render when user exists -->
  <div v-if="user" class="min-h-screen bg-gray-100">
    <!-- Header -->
    <AppHeader 
      :user="user"
      :notifications="notifications"
      @logout="$emit('logout')"
      @notification-click="$emit('notification-click', $event)"
      @clear-notifications="$emit('clear-notifications')"
    />
    
    <!-- Navigation -->
    <AppNavigation 
      :tabs="tabs"
      :active-tab="activeTab"
      @tab-change="$emit('tab-change', $event)"
    />
    
    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
      <slot></slot>
    </main>
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue'
import AppNavigation from './AppNavigation.vue'

export default {
  name: 'AppLayout',
  components: {
    AppHeader,
    AppNavigation
  },
  props: {
    user: {
      type: Object,
      default: null
    },
    notifications: {
      type: Array,
      default: () => []
    },
    tabs: {
      type: Array,
      required: true
    },
    activeTab: {
      type: String,
      required: true
    }
  },
  emits: ['logout', 'tab-change', 'notification-click', 'clear-notifications']
}
</script>