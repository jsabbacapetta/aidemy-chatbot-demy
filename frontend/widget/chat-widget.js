/**
 * Aidemy Chat Widget
 * Interactive chatbot for aidemy.it
 */

(function() {
    'use strict';

    class AidemyChatWidget {
        constructor(config) {
            this.config = config;
            this.sessionId = this.getOrCreateSessionId();
            this.conversationHistory = this.loadConversationHistory();
            this.isOpen = false;
            this.isTyping = false;

            this.init();
        }

        init() {
            this.chatButton = document.getElementById('chat-button');
            this.chatWindow = document.getElementById('chat-window');
            this.closeButton = document.getElementById('close-chat');
            this.chatForm = document.getElementById('chat-form');
            this.chatInput = document.getElementById('chat-input');
            this.chatMessages = document.getElementById('chat-messages');
            this.quickRepliesContainer = document.getElementById('quick-replies');

            this.attachEventListeners();
            this.showWelcomeMessage();

            if (this.config.debug) {
                console.log('Aidemy Chat Widget initialized', {
                    sessionId: this.sessionId,
                    historyLength: this.conversationHistory.length
                });
            }
        }

        attachEventListeners() {
            // Open/close chat
            this.chatButton.addEventListener('click', () => this.toggleChat());
            this.closeButton.addEventListener('click', () => this.toggleChat());

            // Send message
            this.chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });

            // Quick replies
            const quickReplyButtons = document.querySelectorAll('.quick-reply-btn');
            quickReplyButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const message = btn.getAttribute('data-message');
                    this.chatInput.value = message;
                    this.sendMessage();
                    this.hideQuickReplies();
                });
            });
        }

        toggleChat() {
            this.isOpen = !this.isOpen;

            if (this.isOpen) {
                this.chatWindow.classList.remove('hidden');
                this.chatButton.style.display = 'none';
                this.chatInput.focus();
                this.hideNotificationBadge();
            } else {
                this.chatWindow.classList.add('hidden');
                this.chatButton.style.display = 'flex';
            }
        }

        getOrCreateSessionId() {
            let sessionId = localStorage.getItem(this.config.sessionStorageKey);

            if (!sessionId) {
                sessionId = this.generateUUID();
                localStorage.setItem(this.config.sessionStorageKey, sessionId);
            }

            return sessionId;
        }

        generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        loadConversationHistory() {
            const stored = localStorage.getItem(this.config.conversationStorageKey);
            return stored ? JSON.parse(stored) : [];
        }

        saveConversationHistory() {
            // Keep only last 20 messages to avoid localStorage overflow
            const recentHistory = this.conversationHistory.slice(-20);
            localStorage.setItem(
                this.config.conversationStorageKey,
                JSON.stringify(recentHistory)
            );
        }

        showWelcomeMessage() {
            if (this.conversationHistory.length === 0) {
                this.addMessage('assistant', this.config.welcomeMessage);
            } else {
                // Restore conversation history
                this.conversationHistory.forEach(msg => {
                    this.addMessage(msg.role, msg.content, false);
                });
                this.hideQuickReplies();
            }
        }

        async sendMessage() {
            const message = this.chatInput.value.trim();

            if (!message) return;

            // Add user message to UI
            this.addMessage('user', message);

            // Clear input
            this.chatInput.value = '';

            // Show typing indicator
            this.showTypingIndicator();

            // Hide quick replies after first message
            this.hideQuickReplies();

            try {
                // Send to n8n webhook
                const response = await this.callWebhook(message);

                // Hide typing indicator
                this.hideTypingIndicator();

                // Add assistant response
                if (response && response.message) {
                    this.addMessage('assistant', response.message);
                } else {
                    throw new Error('Invalid response format');
                }

            } catch (error) {
                console.error('Error sending message:', error);
                this.hideTypingIndicator();
                this.addMessage('assistant', this.config.errorMessage);
            }
        }

        async callWebhook(message) {
            const payload = {
                session_id: this.sessionId,
                message: message,
                user_id: this.sessionId, // Using session as user ID for now
                timestamp: new Date().toISOString()
            };

            if (this.config.debug) {
                console.log('Sending to webhook:', payload);
            }

            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), this.config.requestTimeout);

            try {
                const response = await fetch(this.config.webhookUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });

                clearTimeout(timeout);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (this.config.debug) {
                    console.log('Webhook response:', data);
                }

                return data;

            } catch (error) {
                clearTimeout(timeout);
                throw error;
            }
        }

        addMessage(role, content, saveHistory = true) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';

            if (role === 'user') {
                avatarDiv.textContent = 'U';
            } else {
                avatarDiv.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 8C13.79 8 12 9.79 12 12C12 14.21 13.79 16 16 16C18.21 16 20 14.21 20 12C20 9.79 18.21 8 16 8ZM16 20C12.67 20 6 21.67 6 25V26H26V25C26 21.67 19.33 20 16 20Z" fill="currentColor"/>
                    </svg>
                `;
            }

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;

            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(contentDiv);

            this.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();

            // Save to history
            if (saveHistory) {
                this.conversationHistory.push({ role, content, timestamp: Date.now() });
                this.saveConversationHistory();
            }
        }

        showTypingIndicator() {
            if (this.isTyping) return;

            this.isTyping = true;

            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.id = 'typing-indicator';

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';
            avatarDiv.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 8C13.79 8 12 9.79 12 12C12 14.21 13.79 16 16 16C18.21 16 20 14.21 20 12C20 9.79 18.21 8 16 8ZM16 20C12.67 20 6 21.67 6 25V26H26V25C26 21.67 19.33 20 16 20Z" fill="currentColor"/>
                </svg>
            `;

            const indicatorDiv = document.createElement('div');
            indicatorDiv.className = 'typing-indicator';
            indicatorDiv.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;

            typingDiv.appendChild(avatarDiv);
            typingDiv.appendChild(indicatorDiv);

            this.chatMessages.appendChild(typingDiv);
            this.scrollToBottom();
        }

        hideTypingIndicator() {
            this.isTyping = false;
            const indicator = document.getElementById('typing-indicator');
            if (indicator) {
                indicator.remove();
            }
        }

        hideQuickReplies() {
            if (this.quickRepliesContainer) {
                this.quickRepliesContainer.style.display = 'none';
            }
        }

        hideNotificationBadge() {
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                badge.style.display = 'none';
            }
        }

        scrollToBottom() {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    // Initialize widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new AidemyChatWidget(AidemyChatConfig);
        });
    } else {
        new AidemyChatWidget(AidemyChatConfig);
    }

})();
