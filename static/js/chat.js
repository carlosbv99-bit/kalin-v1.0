/**
 * Kalin Frontend - Módulo de Chat
 * Maneja la interfaz de chat, envío/recepción de mensajes y historial
 */

class ChatManager {
    constructor() {
        this.messages = [];
        this.chatInput = null;
        this.chatMessages = null;
        this.sendButton = null;
        this.initialized = false;
        this.isProcessing = false;
    }

    /**
     * Inicializar el manager de chat
     */
    initialize() {
        if (this.initialized) return;

        this.chatInput = document.getElementById('chat-input');
        this.chatMessages = document.getElementById('chat-messages');
        this.sendButton = document.getElementById('send-button');

        if (!this.chatInput || !this.chatMessages) {
            console.error('❌ Chat elements not found');
            return;
        }

        this.setupEventListeners();
        this.initialized = true;
        console.log('✅ Chat Manager inicializado');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Enviar con Enter
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Botón enviar
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
    }

    /**
     * Enviar mensaje al backend
     */
    async sendMessage() {
        const message = this.chatInput.value.trim();

        if (!message || this.isProcessing) return;

        // Agregar mensaje del usuario
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.isProcessing = true;

        try {
            // Mostrar indicador de typing
            this.showTypingIndicator();

            // Enviar al backend
            const response = await this.callBackend(message);

            // Ocultar typing
            this.hideTypingIndicator();

            // Procesar respuesta
            this.processResponse(response);

        } catch (error) {
            console.error('❌ Error enviando mensaje:', error);
            this.hideTypingIndicator();
            this.addMessage('❌ Error: ' + error.message, 'assistant');
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Llamar al backend
     * @param {string} message - Mensaje a enviar
     * @returns {Promise<Object>}
     */
    async callBackend(message) {
        const apiUrl = window.AppConfig?.API.SEND_MESSAGE || '/send';

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Procesar respuesta del backend
     * @param {Object} response - Respuesta del servidor
     */
    processResponse(response) {
        // Extraer texto de la respuesta
        const responseText = response.text || response.message || response.response || '';

        if (!responseText) {
            this.addMessage('⚠️ No se recibió respuesta', 'assistant');
            return;
        }

        // Agregar mensaje del asistente
        this.addMessage(responseText, 'assistant');

        // Si hay código, mostrarlo en el panel principal
        if (response.code || this.containsCode(responseText)) {
            const code = response.code || this.extractCode(responseText);
            if (code) {
                this.displayCodeInMainArea(code);
            }
        }

        // Si es HTML y preview está activo, renderizar
        if (window.PreviewManager) {
            const code = response.code || this.extractCode(responseText);
            if (code && window.PreviewManager.isHTMLCode(code)) {
                setTimeout(() => {
                    window.PreviewManager.render(code);
                }, window.AppConfig?.RENDERING.PREVIEW_RENDER_DELAY || 500);
            }
        }
    }

    /**
     * Agregar mensaje al chat
     * @param {string} text - Texto del mensaje
     * @param {string} sender - 'user' o 'assistant'
     */
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);

        // Auto-scroll al final
        this.scrollToBottom();

        // Limitar número de mensajes
        this.limitMessages();
    }

    /**
     * Mostrar indicador de typing
     */
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator';
        typingDiv.id = 'typing-indicator';

        const dotsDiv = document.createElement('div');
        dotsDiv.className = 'typing-dots';
        dotsDiv.innerHTML = '<span></span><span></span><span></span>';

        typingDiv.appendChild(dotsDiv);
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    /**
     * Ocultar indicador de typing
     */
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Mostrar código en el área principal
     * @param {string} code - Código a mostrar
     */
    displayCodeInMainArea(code) {
        const codeArea = document.querySelector('.code-area');
        if (!codeArea) return;

        // Crear elemento de código
        const codeBlock = document.createElement('pre');
        codeBlock.className = 'code-block';
        codeBlock.innerHTML = `<code>${this.escapeHTML(code)}</code>`;

        // Limpiar área anterior y agregar nuevo código
        codeArea.innerHTML = '';
        codeArea.appendChild(codeBlock);

        console.log('✅ Código mostrado en panel principal:', code.length, 'chars');
    }

    /**
     * Detectar si el texto contiene código
     * @param {string} text - Texto a verificar
     * @returns {boolean}
     */
    containsCode(text) {
        return text.includes('```') || 
               text.includes('function') || 
               text.includes('class ') ||
               text.includes('def ') ||
               text.includes('<html') ||
               text.includes('import ');
    }

    /**
     * Extraer código de texto con markdown
     * @param {string} text - Texto con código
     * @returns {string|null}
     */
    extractCode(text) {
        const match = text.match(/```(\w+)?\n([\s\S]*?)```/);
        return match ? match[2] : null;
    }

    /**
     * Escapar HTML para seguridad
     * @param {string} html - HTML a escapar
     * @returns {string}
     */
    escapeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    /**
     * Scroll automático al final
     */
    scrollToBottom() {
        const threshold = window.AppConfig?.UI.AUTO_SCROLL_THRESHOLD || 100;
        const isNearBottom = this.chatMessages.scrollHeight - this.chatMessages.scrollTop - this.chatMessages.clientHeight < threshold;

        if (isNearBottom) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    /**
     * Limitar número de mensajes en historial
     */
    limitMessages() {
        const maxMessages = window.AppConfig?.UI.MAX_CHAT_MESSAGES || 100;
        const messages = this.chatMessages.querySelectorAll('.message');

        if (messages.length > maxMessages) {
            const toRemove = messages.length - maxMessages;
            for (let i = 0; i < toRemove; i++) {
                messages[i].remove();
            }
        }
    }
}

// Exportar como singleton
const chatManager = new ChatManager();

if (typeof window !== 'undefined') {
    window.ChatManager = chatManager;
}
