/**
 * NonHumanArena - 前端主逻辑
 */

// 状态管理
const state = {
    config: {
        apiKeySet: false,
        llmReady: false
    },
    conversation: null,
    currentTurn: 'agent1',
    mode: 'manual', // 'manual' or 'auto'
    autoInterval: 3,
    autoTimer: null,
    eventSource: null
};

// ============ API 调用 ============

async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============ 配置相关 ============

async function loadConfig() {
    try {
        const config = await fetchAPI('/api/config');
        state.config = config;
        updateConfigUI(config);
        return config;
    } catch (error) {
        showStatus('加载配置失败: ' + error.message, 'error');
    }
}

function updateConfigUI(config) {
    document.getElementById('apiKeyDisplay').textContent = config.api_key_set ? '已设置' : '未设置';
    document.getElementById('modelSelect').value = config.model;
    document.getElementById('temperature').value = config.temperature;
    document.getElementById('maxTokens').value = config.max_tokens;
    document.getElementById('autoInterval').value = config.auto_interval;
    
    if (!config.api_key_set) {
        document.getElementById('apiKeyInput').focus();
    }
}

async function saveConfig() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const model = document.getElementById('modelSelect').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    const autoInterval = parseInt(document.getElementById('autoInterval').value);
    
    if (!apiKey) {
        showStatus('请输入API Key', 'error');
        return;
    }
    
    try {
        await fetchAPI('/api/config', {
            method: 'POST',
            body: JSON.stringify({
                api_key: apiKey,
                model: model,
                base_url: 'https://api.minimax.chat/v1',
                temperature: temperature,
                max_tokens: maxTokens,
                auto_interval: autoInterval
            })
        });
        
        state.config.apiKeySet = true;
        state.config.llmReady = true;
        state.autoInterval = autoInterval;
        
        document.getElementById('apiKeyDisplay').textContent = '已设置';
        document.getElementById('apiKeyInput').value = '';
        
        showStatus('配置已保存', 'success');
    } catch (error) {
        showStatus('保存配置失败: ' + error.message, 'error');
    }
}

// ============ 对话相关 ============

async function startConversation() {
    if (!state.config.api_key_set) {
        showStatus('请先配置API Key', 'error');
        return;
    }
    
    const agent1Name = document.getElementById('agent1Name').value.trim() || '小明';
    const agent1Personality = document.getElementById('agent1Personality').value.trim() || '理性、冷静、逻辑清晰';
    const agent1Desc = document.getElementById('agent1Desc').value.trim();
    
    const agent2Name = document.getElementById('agent2Name').value.trim() || '小红';
    const agent2Personality = document.getElementById('agent2Personality').value.trim() || '感性、热情、表达生动';
    const agent2Desc = document.getElementById('agent2Desc').value.trim();
    
    try {
        const conversation = await fetchAPI('/api/conversation', {
            method: 'POST',
            body: JSON.stringify({
                agent1: {
                    name: agent1Name,
                    personality: agent1Personality,
                    description: agent1Desc
                },
                agent2: {
                    name: agent2Name,
                    personality: agent2Personality,
                    description: agent2Desc
                }
            })
        });
        
        state.conversation = conversation;
        state.currentTurn = 'agent1';
        
        clearMessages();
        showStatus('对话已创建，开始聊天吧！', 'success');
        updateButtons();
        
        // 如果是自动模式，开始自动对话
        if (state.mode === 'auto') {
            startAutoMode();
        }
    } catch (error) {
        showStatus('创建对话失败: ' + error.message, 'error');
    }
}

async function generateResponse(agentId) {
    if (!state.conversation) {
        showStatus('请先创建对话', 'error');
        return;
    }
    
    const agent = agentId === state.conversation.agent1.id ? 
        state.conversation.agent1 : state.conversation.agent2;
    
    // 显示正在输入状态
    const messageId = showTyping(agent.name, agentId);
    
    try {
        // 使用流式API
        await streamGenerate(agentId, messageId);
        
        // 刷新对话状态
        await refreshConversation();
    } catch (error) {
        removeTyping(messageId);
        showStatus('生成回复失败: ' + error.message, 'error');
    }
}

async function streamGenerate(agentId, messageId) {
    return new Promise((resolve, reject) => {
        const url = `/api/conversation/${state.conversation.id}/stream/${agentId}`;
        
        state.eventSource = new EventSource(url);
        const messageElement = document.getElementById(messageId);
        
        state.eventSource.addEventListener('chunk', (event) => {
            const data = JSON.parse(event.data);
            messageElement.querySelector('.content').textContent += data.content;
        });
        
        state.eventSource.addEventListener('done', (event) => {
            const data = JSON.parse(event.data);
            state.eventSource.close();
            state.eventSource = null;
            
            // 更新消息ID
            messageElement.id = data.id;
            
            // 添加到对话
            state.conversation.messages.push({
                id: data.id,
                agent_id: agentId,
                agent_name: data.agent_name || agentId,
                content: data.content,
                is_user: false
            });
            
            // 切换轮次
            state.currentTurn = agentId === state.conversation.agent1.id ? 'agent2' : 'agent1';
            updateButtons();
            
            resolve();
        });
        
        state.eventSource.addEventListener('error', (event) => {
            state.eventSource.close();
            state.eventSource = null;
            removeTyping(messageId);
            reject(new Error('流式请求失败'));
        });
    });
}

async function refreshConversation() {
    if (!state.conversation) return;
    
    try {
        const conversation = await fetchAPI(`/api/conversation/${state.conversation.id}`);
        state.conversation = conversation;
        updateMessages();
    } catch (error) {
        console.error('刷新对话失败:', error);
    }
}

// ============ 自动模式 ============

function startAutoMode() {
    if (!state.conversation) {
        showStatus('请先创建对话', 'error');
        return;
    }
    
    state.mode = 'auto';
    document.getElementById('modeAuto').checked = true;
    
    autoNextTurn();
}

function autoNextTurn() {
    if (!state.conversation || state.mode !== 'auto') return;
    
    const agentId = state.currentTurn === 'agent1' ? 
        state.conversation.agent1.id : state.conversation.agent2.id;
    
    generateResponse(agentId).then(() => {
        // 设置定时器，自动生成下一条
        state.autoTimer = setTimeout(autoNextTurn, state.autoInterval * 1000);
    });
}

function stopAutoMode() {
    state.mode = 'manual';
    document.getElementById('modeManual').checked = true;
    
    if (state.autoTimer) {
        clearTimeout(state.autoTimer);
        state.autoTimer = null;
    }
    
    if (state.eventSource) {
        state.eventSource.close();
        state.eventSource = null;
    }
    
    showStatus('自动模式已停止', 'info');
    updateButtons();
}

// ============ UI 更新 ============

function clearMessages() {
    document.getElementById('messagesContainer').innerHTML = '';
}

function updateMessages() {
    if (!state.conversation) return;
    
    const container = document.getElementById('messagesContainer');
    container.innerHTML = '';
    
    state.conversation.messages.forEach(msg => {
        addMessage(msg.agent_name, msg.content, msg.agent_id, msg.is_user);
    });
    
    // 滚动到底部
    container.scrollTop = container.scrollHeight;
}

function addMessage(sender, content, agentId, isUser = false) {
    const container = document.getElementById('messagesContainer');
    
    let className = 'message';
    if (isUser) {
        className += ' user';
    } else if (agentId === state.conversation?.agent1.id) {
        className += ' agent1';
    } else {
        className += ' agent2';
    }
    
    const messageHtml = `
        <div class="${className}">
            <div class="sender">${sender}</div>
            <div class="content">${escapeHtml(content)}</div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    container.scrollTop = container.scrollHeight;
}

function showTyping(sender, agentId) {
    const container = document.getElementById('messagesContainer');
    const messageId = 'typing-' + Date.now();
    
    let className = 'message typing';
    if (agentId === state.conversation?.agent1.id) {
        className += ' agent1';
    } else {
        className += ' agent2';
    }
    
    const messageHtml = `
        <div id="${messageId}" class="${className}">
            <div class="sender">${sender} 正在思考...</div>
            <div class="content"></div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    container.scrollTop = container.scrollHeight;
    
    return messageId;
}

function removeTyping(messageId) {
    const element = document.getElementById(messageId);
    if (element) {
        element.remove();
    }
}

function updateButtons() {
    const hasConversation = state.conversation !== null;
    const isAutoMode = state.mode === 'auto';
    
    document.getElementById('btnGenerate1').disabled = !hasConversation || isAutoMode;
    document.getElementById('btnGenerate2').disabled = !hasConversation || isAutoMode;
    document.getElementById('btnStartAuto').disabled = !hasConversation || isAutoMode;
    document.getElementById('btnStopAuto').disabled = !isAutoMode;
}

function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    statusEl.className = `status ${type}`;
    statusEl.textContent = message;
    statusEl.style.display = 'block';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ 事件绑定 ============

document.addEventListener('DOMContentLoaded', async () => {
    // 加载配置
    await loadConfig();
    
    // 保存配置按钮
    document.getElementById('btnSaveConfig').addEventListener('click', saveConfig);
    
    // 模式切换
    document.getElementById('modeManual').addEventListener('change', () => {
        if (state.mode === 'auto') {
            stopAutoMode();
        }
    });
    
    document.getElementById('modeAuto').addEventListener('change', () => {
        state.mode = 'auto';
        if (state.conversation) {
            startAutoMode();
        }
    });
    
    // 创建对话
    document.getElementById('btnStartConversation').addEventListener('click', startConversation);
    
    // Agent1 发言
    document.getElementById('btnGenerate1').addEventListener('click', () => {
        if (state.conversation) {
            generateResponse(state.conversation.agent1.id);
        }
    });
    
    // Agent2 发言
    document.getElementById('btnGenerate2').addEventListener('click', () => {
        if (state.conversation) {
            generateResponse(state.conversation.agent2.id);
        }
    });
    
    // 自动模式
    document.getElementById('btnStartAuto').addEventListener('click', startAutoMode);
    document.getElementById('btnStopAuto').addEventListener('click', stopAutoMode);
    
    // 清空对话
    document.getElementById('btnClear').addEventListener('click', () => {
        if (confirm('确定要清空所有消息吗？')) {
            clearMessages();
            state.conversation = null;
            state.currentTurn = 'agent1';
            updateButtons();
            showStatus('对话已清空', 'info');
        }
    });
    
    // 更新按钮状态
    updateButtons();
});
