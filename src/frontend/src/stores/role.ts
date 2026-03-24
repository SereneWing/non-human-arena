import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { Role, RoleCreate, RoleUpdate } from '@/types'

export const useRoleStore = defineStore('role', () => {
  const roles = ref<Role[]>([])
  const currentRole = ref<Role | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const roleCount = computed(() => roles.value.length)

  async function fetchRoles(skip = 0, limit = 100) {
    loading.value = true
    error.value = null
    try {
      roles.value = await api.getRoles(skip, limit)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch roles'
    } finally {
      loading.value = false
    }
  }

  async function fetchRole(id: string) {
    loading.value = true
    error.value = null
    try {
      currentRole.value = await api.getRole(id)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch role'
    } finally {
      loading.value = false
    }
  }

  async function createRole(data: RoleCreate) {
    loading.value = true
    error.value = null
    try {
      const role = await api.createRole(data)
      roles.value.unshift(role)
      return role
    } catch (e: any) {
      error.value = e.message || 'Failed to create role'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateRole(id: string, data: RoleUpdate) {
    loading.value = true
    error.value = null
    try {
      const role = await api.updateRole(id, data)
      const index = roles.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        roles.value[index] = role
      }
      if (currentRole.value?.id === id) {
        currentRole.value = role
      }
      return role
    } catch (e: any) {
      error.value = e.message || 'Failed to update role'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteRole(id: string) {
    loading.value = true
    error.value = null
    try {
      await api.deleteRole(id)
      roles.value = roles.value.filter((r) => r.id !== id)
      if (currentRole.value?.id === id) {
        currentRole.value = null
      }
    } catch (e: any) {
      error.value = e.message || 'Failed to delete role'
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    roles,
    currentRole,
    loading,
    error,
    roleCount,
    fetchRoles,
    fetchRole,
    createRole,
    updateRole,
    deleteRole,
    clearError,
  }
})
