# 前端组件库

## 一、通用组件

```typescript
// components/BaseButton.vue
<template>
  <el-button
    :type="type"
    :size="size"
    :disabled="disabled"
    :loading="loading"
    @click="handleClick"
  >
    <slot />
  </el-button>
</template>

<script setup lang="ts">
defineProps<{
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'large' | 'medium' | 'small'
  disabled?: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>
```

```typescript
// components/SessionCard.vue
<template>
  <el-card class="session-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">{{ session.name }}</span>
        <el-tag :type="getStateType(session.state)">
          {{ getStateLabel(session.state) }}
        </el-tag>
      </div>
    </template>
    
    <div class="card-body">
      <div class="info-row">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDate(session.createdAt) }}</span>
      </div>
      <div class="info-row">
        <el-icon><User /></el-icon>
        <span>{{ session.participantCount }} 参与者</span>
      </div>
    </div>
    
    <template #footer>
      <div class="card-actions">
        <el-button size="small" @click="$emit('view', session)">
          查看
        </el-button>
        <el-button size="small" type="primary" @click="$emit('enter', session)">
          进入
        </el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import type { Session } from '@/types'

defineProps<{
  session: Session
}>()

defineEmits<{
  view: [session: Session]
  enter: [session: Session]
}>()

const getStateType = (state: string) => {
  const types: Record<string, string> = {
    waiting: 'info',
    running: 'success',
    paused: 'warning',
    completed: '',
    error: 'danger'
  }
  return types[state] || ''
}

const getStateLabel = (state: string) => {
  const labels: Record<string, string> = {
    waiting: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    error: '错误'
  }
  return labels[state] || state
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}
</script>
```

## 二、消息组件

```typescript
// components/MessageBubble.vue
<template>
  <div :class="['message-bubble', message.role, message.type]">
    <div class="bubble-header">
      <span class="sender">{{ message.participantName }}</span>
      <el-tag v-if="message.type === 'mental'" size="small" type="info">
        心理活动
      </el-tag>
    </div>
    
    <div class="bubble-content">
      <div v-if="message.type === 'text'" class="text-content">
        {{ message.content }}
      </div>
      
      <div v-else-if="message.type === 'action'" class="action-content">
        *{{ message.content }}*
      </div>
      
      <div v-else-if="message.type === 'mental'" class="mental-content">
        💭 {{ message.content }}
      </div>
    </div>
    
    <div class="bubble-footer">
      <span class="time">{{ formatTime(message.timestamp) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/types'

defineProps<{
  message: Message
}>()

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}
</script>

<style scoped>
.message-bubble {
  max-width: 70%;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.message-bubble.user {
  background: #e6f7ff;
  margin-left: auto;
}

.message-bubble.assistant {
  background: #f5f5f5;
  margin-right: auto;
}

.message-bubble.system {
  background: #fff7e6;
  margin: 0 auto;
  text-align: center;
}
</style>
```

## 三、表单组件

```typescript
// components/RoleForm.vue
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="100px"
  >
    <el-form-item label="角色名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入角色名称" />
    </el-form-item>
    
    <el-form-item label="角色类别" prop="category">
      <el-select v-model="formData.category" placeholder="请选择">
        <el-option
          v-for="cat in categories"
          :key="cat.value"
          :label="cat.label"
          :value="cat.value"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="描述" prop="description">
      <el-input
        v-model="formData.description"
        type="textarea"
        :rows="3"
      />
    </el-form-item>
    
    <el-form-item label="系统提示词" prop="systemPrompt">
      <el-input
        v-model="formData.systemPrompt"
        type="textarea"
        :rows="6"
        placeholder="定义角色的行为和特征..."
      />
    </el-form-item>
    
    <el-form-item label="发言风格">
      <div class="style-config">
        <el-slider v-model="formData.speakingStyle.formality" :min="0" :max="1" />
        <span>正式程度: {{ formData.speakingStyle.formality }}</span>
      </div>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="submit">
        {{ submitText }}
      </el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

const props = withDefaults(defineProps<{
  initialData?: Partial<RoleFormData>
  submitText?: string
}>(), {
  submitText: '提交'
})

const emit = defineEmits<{
  submit: [data: RoleFormData]
  cancel: []
}>()

const formRef = ref<FormInstance>()

const categories = [
  { label: '辩手', value: 'debater' },
  { label: '调解员', value: 'mediator' },
  { label: '旁白', value: 'narrator' },
  { label: '裁判', value: 'judge' },
  { label: '游戏玩家', value: 'player' },
  { label: '自定义', value: 'custom' }
]

const formData = reactive<RoleFormData>({
  name: props.initialData?.name || '',
  category: props.initialData?.category || 'custom',
  description: props.initialData?.description || '',
  systemPrompt: props.initialData?.systemPrompt || '',
  speakingStyle: {
    formality: 0.5,
    lengthPreference: 'medium',
    tone: 'neutral',
    useEmoji: false
  }
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择角色类别', trigger: 'change' }
  ]
}

const submit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      emit('submit', { ...formData })
    }
  })
}
</script>

interface RoleFormData {
  name: string
  category: string
  description: string
  systemPrompt: string
  speakingStyle: {
    formality: number
    lengthPreference: string
    tone: string
    useEmoji: boolean
  }
}
```

## 四、对话组件

```typescript
// components/ChatInput.vue
<template>
  <div class="chat-input">
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        :placeholder="placeholder"
        :disabled="disabled"
        resize="none"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.ctrl="handleSend"
      />
    </div>
    
    <div class="input-actions">
      <div class="left-actions">
        <el-tooltip content="上传文件">
          <el-button :icon="Upload" circle />
        </el-tooltip>
        <el-tooltip content="插入图片">
          <el-button :icon="Picture" circle />
        </el-tooltip>
      </div>
      
      <div class="right-actions">
        <span class="char-count">{{ inputText.length }} / {{ maxLength }}</span>
        <el-button
          type="primary"
          :disabled="!canSend"
          :loading="sending"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = withDefaults(defineProps<{
  placeholder?: string
  maxLength?: number
  disabled?: boolean
}>(), {
  placeholder: '输入消息...',
  maxLength: 2000,
  disabled: false
})

const emit = defineEmits<{
  send: [content: string]
}>()

const inputText = ref('')
const sending = ref(false)

const canSend = computed(() => {
  return inputText.value.trim().length > 0 &&
         inputText.value.length <= props.maxLength &&
         !props.disabled &&
         !sending.value
})

const handleSend = async () => {
  if (!canSend.value) return
  
  sending.value = true
  try {
    emit('send', inputText.value.trim())
    inputText.value = ''
  } finally {
    sending.value = false
  }
}
</script>
```
