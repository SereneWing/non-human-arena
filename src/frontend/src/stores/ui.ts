import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const modalOpen = ref(false)
  const modalComponent = ref<string | null>(null)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  function openModal(component: string) {
    modalComponent.value = component
    modalOpen.value = true
  }

  function closeModal() {
    modalOpen.value = false
    modalComponent.value = null
  }

  return {
    sidebarCollapsed,
    theme,
    modalOpen,
    modalComponent,
    toggleSidebar,
    setTheme,
    openModal,
    closeModal,
  }
})
