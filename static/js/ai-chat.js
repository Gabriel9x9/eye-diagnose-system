/**
 * AI Q&A Chat Functionality
 * This script handles the AI chat functionality using DeepSeek API
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get current page path
    const currentPath = window.location.pathname;
    
    // Define the paths where the AI chat should be prominently displayed
    const targetPaths = [
        '/personal/',        // 单人诊断页面
        '/batch-diagnose/',  // 批量诊断页面
        '/records/',         // 诊断记录页面
    ];
    
    // Check if we're on one of the target pages
    const isTargetPage = targetPaths.some(path => currentPath.startsWith(path));
    
    // Always show the chat button, but make it more prominent on target pages
    const showAiChat = true;
    
    // Create the AI chat button
    const aiChatButton = document.createElement('div');
    aiChatButton.id = 'ai-chat-button';
    aiChatButton.innerHTML = '<i class="fas fa-robot"></i>';
    aiChatButton.title = '眼科AI助手';
    
    // Make the button more prominent on target pages
    if (isTargetPage) {
        aiChatButton.classList.add('ai-chat-button-prominent');
    }
    
    document.body.appendChild(aiChatButton);

    // Create the chat window
    const aiChatWindow = document.createElement('div');
    aiChatWindow.id = 'ai-chat-window';
    aiChatWindow.className = 'ai-chat-window-hidden';
    
    // Set a different welcome message based on the current page
    let welcomeMessage = '您好！我是您的眼科AI助手，可以回答关于眼科疾病的问题。请问有什么可以帮助您的吗？';
    
    if (currentPath.includes('/personal/')) {
        welcomeMessage = '您好！我是您的眼科AI助手。我可以回答关于眼科疾病诊断的问题。您可以询问关于眼底医学影像、诊断结果的解释或特定眼病的信息。';
    } else if (currentPath.includes('/batch-diagnose/')) {
        welcomeMessage = '您好！我是您的眼科AI助手。我可以帮助回答关于批量诊断的问题，包括影像批处理、批量分析结果等。有什么可以帮助您的吗？';
    } else if (currentPath.includes('/records/')) {
        welcomeMessage = '您好！我是您的眼科AI助手。我可以回答关于诊断记录的问题，帮助您理解每个记录的意义及后续建议。有什么可以帮助您的吗？';
    }
    
    aiChatWindow.innerHTML = `
        <div class="ai-chat-header">
            <div class="ai-chat-title">眼科AI助手</div>
            <div class="ai-chat-controls">
                <button id="ai-chat-minimize" title="最小化"><i class="fas fa-minus"></i></button>
                <button id="ai-chat-close" title="关闭"><i class="fas fa-times"></i></button>
            </div>
        </div>
        <div class="ai-chat-messages" id="ai-chat-messages">
            <div class="ai-message">
                <div class="ai-avatar"><i class="fas fa-robot"></i></div>
                <div class="ai-message-content">
                    <p>${welcomeMessage}</p>
                </div>
            </div>
        </div>
        <div class="ai-chat-input-container">
            <textarea id="ai-chat-input" placeholder="请输入您的问题..." rows="1"></textarea>
            <button id="ai-chat-send"><i class="fas fa-paper-plane"></i></button>
        </div>
    `;
    document.body.appendChild(aiChatWindow);

    // Event listeners
    aiChatButton.addEventListener('click', toggleChatWindow);
    document.getElementById('ai-chat-close').addEventListener('click', closeChatWindow);
    document.getElementById('ai-chat-minimize').addEventListener('click', minimizeChatWindow);
    document.getElementById('ai-chat-send').addEventListener('click', sendMessage);
    
    const chatInput = document.getElementById('ai-chat-input');
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
        
        // Auto-resize the textarea
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    chatInput.addEventListener('input', function() {
        // Auto-resize the textarea
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Functions
    function toggleChatWindow() {
        if (aiChatWindow.classList.contains('ai-chat-window-hidden')) {
            aiChatWindow.classList.remove('ai-chat-window-hidden');
            aiChatWindow.classList.add('ai-chat-window-visible');
            chatInput.focus();
        } else if (aiChatWindow.classList.contains('ai-chat-window-minimized')) {
            aiChatWindow.classList.remove('ai-chat-window-minimized');
            chatInput.focus();
        } else {
            minimizeChatWindow();
        }
    }

    function closeChatWindow() {
        aiChatWindow.classList.remove('ai-chat-window-visible');
        aiChatWindow.classList.remove('ai-chat-window-minimized');
        aiChatWindow.classList.add('ai-chat-window-hidden');
    }

    function minimizeChatWindow() {
        aiChatWindow.classList.add('ai-chat-window-minimized');
    }

    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        // Add user message to chat
        addMessage('user', messageText);
        
        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Set a timeout for the API request
        const timeoutDuration = 65000; // 65 seconds (slightly longer than server timeout)
        let timeoutId = setTimeout(() => {
            // If this executes, the request took too long
            removeTypingIndicator();
            addMessage('ai', '抱歉，响应时间过长。这可能是由于网络问题或者服务器并发请求过多。请稍后再试。');
            scrollToBottom();
        }, timeoutDuration);
        
        // Send to API
        fetch('/api/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: messageText
            })
        })
        .then(response => {
            // Clear the timeout since we got a response
            clearTimeout(timeoutId);
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI response
            if (data.error) {
                addMessage('ai', '抱歉，我遇到了问题：' + data.error);
            } else {
                addMessage('ai', data.response);
            }
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            // Clear the timeout since we got an error response
            clearTimeout(timeoutId);
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add more detailed error message
            let errorMsg = '抱歉，连接出现问题，请稍后再试。';
            
            // Add more specific error information if it's a timeout
            if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
                errorMsg = '抱歉，请求超时。这可能是由于网络问题或服务器负载过高。请稍后再尝试。';
            }
            
            addMessage('ai', errorMsg);
            console.error('Error:', error);
            
            // Scroll to bottom
            scrollToBottom();
        });
    }

    function addMessage(sender, content) {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const messageDiv = document.createElement('div');
        
        if (sender === 'user') {
            messageDiv.className = 'user-message';
            messageDiv.innerHTML = `
                <div class="user-message-content">
                    <p>${escapeHtml(content)}</p>
                </div>
                <div class="user-avatar"><i class="fas fa-user"></i></div>
            `;
        } else {
            messageDiv.className = 'ai-message';
            messageDiv.innerHTML = `
                <div class="ai-avatar"><i class="fas fa-robot"></i></div>
                <div class="ai-message-content">
                    <p>${content}</p>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'ai-message typing-indicator';
        indicatorDiv.id = 'typing-indicator';
        indicatorDiv.innerHTML = `
            <div class="ai-avatar"><i class="fas fa-robot"></i></div>
            <div class="ai-message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(indicatorDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function scrollToBottom() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
