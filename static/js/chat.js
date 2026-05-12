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
        
        // Obtener código actual del editor si existe
        let currentCode = '';
        if (window.CodeEditorManager && window.CodeEditorManager.codeEditor) {
            currentCode = window.CodeEditorManager.codeEditor.value;
        }

        // Obtener session_id para mantener contexto conversacional
        const sessionId = window.currentSessionId || 'default';

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message,
                session_id: sessionId,  // Enviar session_id para contexto
                context: {
                    current_code: currentCode
                }
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Guardar session_id recibido del backend para futuras peticiones
        if (data.session_id) {
            window.currentSessionId = data.session_id;
        }
        
        return data;
    }

    /**
     * Procesar respuesta del backend
     * @param {Object} response - Respuesta del servidor
     */
    processResponse(response) {
        // Extraer texto de la respuesta (el backend usa 'respuesta' en español)
        const responseText = response.respuesta || response.text || response.message || response.response || '';

        if (!responseText) {
            this.addMessage('⚠️ No se recibió respuesta', 'assistant');
            console.error('❌ Respuesta vacía. Keys disponibles:', Object.keys(response));
            return;
        }

        // Verificar si hay código en la respuesta
        const hasCode = response.code || this.containsCode(responseText);
        
        if (hasCode) {
            const code = response.code || this.extractCode(responseText);
            if (code) {
                // Enviar código directamente al panel de código (sin mostrarlo en el chat)
                this.displayCodeInMainArea(code);
                
                // Mensaje de confirmación breve en el chat
                const lang = this.detectLanguage(code);
                this.addMessage(`✅ Código ${lang.toUpperCase()} generado y actualizado en el editor.`, 'assistant');
                
                // Renderizar automáticamente
                setTimeout(() => {
                    if (window.UniversalRenderer) {
                        window.UniversalRenderer.render(code);
                    } else if (window.PreviewManager && window.PreviewManager.isHTMLCode(code)) {
                        window.PreviewManager.render(code);
                    }
                }, 300);
            }
        } else {
            // Si no hay código, mostrar el texto completo en el chat
            this.addMessage(responseText, 'assistant');
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
        // Usar el nuevo CodeEditorManager si está disponible
        if (window.CodeEditorManager) {
            window.CodeEditorManager.displayGeneratedCode(code);
        } else {
            // Fallback al método anterior
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
               text.includes('<!DOCTYPE') ||
               text.includes('import ') ||
               // Detectar fragmentos HTML simples
               (text.includes('<') && text.includes('>') && /<(div|span|p|button|input|form|table|h[1-6]|ul|ol|li|a|img|video|audio|canvas|svg)/i.test(text));
    }

    /**
     * Extraer código de texto con markdown
     * @param {string} text - Texto con código
     * @returns {string|null}
     */
    extractCode(text) {
        if (!text) return null;
        
        // Buscar bloques de código con formato ```lenguaje\ncódigo```
        const codeBlockRegex = /```(?:py|python|javascript|js|html|css|json|md)?\s*\n([\s\S]*?)```/i;
        const match = text.match(codeBlockRegex);
        
        if (match && match[1]) {
            // Limpiar el código extraído (quitar espacios iniciales/finales)
            return match[1].trim();
        }
        
        // Si no hay bloques de código markdown, buscar fragmentos HTML simples
        // Detectar si el texto es principalmente un elemento HTML
        const htmlFragmentRegex = /<(div|span|p|button|input|form|table|h[1-6]|ul|ol|li|a|img|video|audio|canvas|svg)[^>]*>[\s\S]*?<\/\1>/i;
        const htmlMatch = text.match(htmlFragmentRegex);
        
        if (htmlMatch) {
            return htmlMatch[0].trim();
        }
        
        // Si no hay patrones específicos, retornar null
        return null;
    }

    /**
     * Detectar lenguaje del código
     * @param {string} code - Código a analizar
     * @returns {string} - Lenguaje detectado
     */
    detectLanguage(code) {
        if (!code) return 'text';
        const c = code.trim();
        
        // HTML (incluir etiquetas sueltas y SVG)
        if (c.startsWith('<!DOCTYPE') || 
            c.includes('<html') || 
            c.includes('<div') || 
            c.includes('<span') ||
            c.includes('<circle') ||
            c.includes('<svg') ||
            c.includes('<body') ||
            c.includes('<head')) {
            return 'html';
        }
        
        // Python
        if (c.includes('def ') || c.includes('import ') || c.includes('print(')) return 'python';
        
        // C / C++
        if (c.includes('#include')) {
            if (c.includes('<iostream>') || c.includes('std::') || c.includes('cout')) return 'cpp';
            return 'c';
        }
        
        // Java
        if (c.includes('public class') || c.includes('System.out.println')) return 'java';
        
        // JavaScript
        if (c.includes('function') || c.includes('const ') || c.includes('console.log')) return 'javascript';
        
        // CSS
        if (c.includes('{') && c.includes(':') && c.includes(';') && !c.includes('int ') && !c.includes('void')) return 'css';
        
        return 'text';
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
