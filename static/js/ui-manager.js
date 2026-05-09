/**
 * Kalin Frontend - Módulo de UI y Sidebar
 * Maneja toda la interfaz de usuario, menú lateral y funciones auxiliares
 */

class UIManager {
    constructor() {
        this.sidebar = null;
        this.recognition = null;
        this.isRecording = false;
        this.initialized = false;
    }

    /**
     * Inicializar UI Manager
     */
    initialize() {
        if (this.initialized) return;

        this.sidebar = document.querySelector('.sidebar');
        
        // Configurar reconocimiento de voz si está disponible
        this.setupSpeechRecognition();
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Cargar modelo activo
        this.loadActiveModel();
        
        this.initialized = true;
        console.log('✅ UI Manager inicializado');
    }

    /**
     * Configurar reconocimiento de voz
     */
    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'es-ES';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const input = document.getElementById('chat-input');
                if (input) {
                    input.value = transcript;
                    this.stopRecording();
                    if (window.ChatManager) {
                        window.ChatManager.updateButton();
                    }
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Error de voz:', event.error);
                this.stopRecording();
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };
        } else {
            const micBtn = document.getElementById('mic-btn');
            if (micBtn) {
                micBtn.style.display = 'none';
            }
        }
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Input del chat
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (window.ChatManager) {
                        window.ChatManager.sendMessage();
                    }
                }
            });
            
            chatInput.addEventListener('input', () => {
                if (window.ChatManager) {
                    window.ChatManager.updateButton();
                }
            });
        }

        // Botón enviar
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                if (window.ChatManager) {
                    window.ChatManager.sendMessage();
                }
            });
        }

        // Botón micrófono
        const micBtn = document.getElementById('mic-btn');
        if (micBtn) {
            micBtn.addEventListener('click', () => this.toggleMic());
        }

        // Toggle sidebar
        const menuToggle = document.querySelector('.menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        const sidebarClose = document.querySelector('.sidebar-close');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => this.toggleSidebar());
        }
    }

    /**
     * Cargar modelo activo desde backend
     */
    async loadActiveModel() {
        try {
            const response = await fetch('/system/current-model');
            const data = await response.json();
            
            if (data.status === 'success' && data.current_model) {
                const indicator = document.getElementById('active-model-indicator');
                if (indicator) {
                    indicator.textContent = '🤖 ' + data.current_model;
                    indicator.title = 'Modelo de IA activo: ' + data.current_model;
                }
            }
        } catch (error) {
            console.error('Error cargando modelo activo:', error);
        }
    }

    /**
     * Toggle micrófono
     */
    toggleMic() {
        if (!this.recognition) {
            alert('Reconocimiento de voz no soportado en este navegador');
            return;
        }

        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    /**
     * Iniciar grabación de voz
     */
    startRecording() {
        if (this.recognition) {
            this.recognition.start();
            this.isRecording = true;
            const micBtn = document.getElementById('mic-btn');
            if (micBtn) {
                micBtn.classList.add('recording');
            }
            console.log('🎤 Grabación iniciada');
        }
    }

    /**
     * Detener grabación de voz
     */
    stopRecording() {
        if (this.recognition) {
            this.recognition.stop();
            this.isRecording = false;
            const micBtn = document.getElementById('mic-btn');
            if (micBtn) {
                micBtn.classList.remove('recording');
            }
            console.log('⏹️ Grabación detenida');
        }
    }

    /**
     * Toggle sidebar
     */
    toggleSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('open');
        }
    }

    /**
     * Ocultar pantalla de bienvenida
     */
    hideWelcomeScreen() {
        const welcome = document.querySelector('.welcome-screen');
        if (welcome) {
            welcome.classList.add('hidden');
        }
    }

    /**
     * Exportar experiencia
     */
    async exportExperience() {
        try {
            const response = await fetch('/experience/export');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `kalin_experience_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            console.log('✅ Experiencia exportada');
        } catch (error) {
            console.error('Error exportando experiencia:', error);
            alert('Error al exportar experiencia');
        }
    }

    /**
     * Importar experiencia
     */
    importExperience() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/experience/import', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (data.status === 'success') {
                    alert('✅ Experiencia importada correctamente');
                    location.reload();
                } else {
                    alert('❌ Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error importando experiencia:', error);
                alert('Error al importar experiencia');
            }
        };

        input.click();
    }

    /**
     * Verificar dependencias
     */
    async checkDependencies() {
        try {
            const response = await fetch('/system/check-dependencies');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showDependencyReport(data);
            }
        } catch (error) {
            console.error('Error verificando dependencias:', error);
        }
    }

    /**
     * Mostrar reporte de dependencias
     */
    showDependencyReport(data) {
        let message = '📊 **Reporte de Dependencias**\n\n';
        
        if (data.missing.length > 0) {
            message += '❌ **Faltantes:**\n';
            data.missing.forEach(dep => {
                message += `• ${dep}\n`;
            });
            message += '\n';
        }
        
        if (data.installed.length > 0) {
            message += '✅ **Instaladas:**\n';
            data.installed.forEach(dep => {
                message += `• ${dep}\n`;
            });
            message += '\n';
        }
        
        if (data.missing.length > 0) {
            message += '💡 Ejecuta "Instalar Dependencias" desde el menú para instalar las faltantes.';
        } else {
            message += '✨ ¡Todas las dependencias están instaladas!';
        }

        if (window.ChatManager) {
            window.ChatManager.addMessage(message, 'assistant');
        }
    }

    /**
     * Instalar dependencias
     */
    async installDependencies() {
        if (window.ChatManager) {
            window.ChatManager.addMessage('📦 Instalando dependencias... Esto puede tardar unos minutos.', 'assistant');
        }

        try {
            const response = await fetch('/system/install-dependencies', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('✅ Dependencias instaladas correctamente. Recarga la página.', 'assistant');
                }
            } else {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error: ' + data.message, 'assistant');
                }
            }
        } catch (error) {
            console.error('Error instalando dependencias:', error);
            if (window.ChatManager) {
                window.ChatManager.addMessage('❌ Error al instalar dependencias', 'assistant');
            }
        }
    }

    /**
     * Crear entorno virtual
     */
    async createVenv() {
        if (window.ChatManager) {
            window.ChatManager.addMessage('🔧 Creando entorno virtual...', 'assistant');
        }

        try {
            const response = await fetch('/system/create-venv', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('✅ Entorno virtual creado. Instala dependencias ahora.', 'assistant');
                }
            } else {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error: ' + data.message, 'assistant');
                }
            }
        } catch (error) {
            console.error('Error creando venv:', error);
        }
    }

    /**
     * Descargar modelos Ollama
     */
    downloadModels() {
        // Abrir modal de selección de modelos
        const modal = document.getElementById('model-modal');
        if (modal) {
            modal.classList.add('show');
            this.loadAvailableModels();
        }
    }

    /**
     * Cargar modelos disponibles
     */
    async loadAvailableModels() {
        try {
            const response = await fetch('/system/available-models');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderModelList(data.models);
            }
        } catch (error) {
            console.error('Error cargando modelos:', error);
        }
    }

    /**
     * Renderizar lista de modelos
     */
    renderModelList(models) {
        const container = document.getElementById('model-list');
        if (!container) return;

        container.innerHTML = '';
        
        const categories = {
            'recommended': '⭐ Recomendados',
            'popular': '🔥 Populares',
            'latest': '✨ Últimos del Mercado',
            'lightweight': '💚 Ligeros'
        };
        
        const grouped = {};
        models.forEach(model => {
            if (!grouped[model.category]) {
                grouped[model.category] = [];
            }
            grouped[model.category].push(model);
        });
        
        Object.keys(categories).forEach(category => {
            if (grouped[category]) {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'model-category';
                
                const title = document.createElement('div');
                title.className = 'model-category-title';
                title.textContent = categories[category];
                categoryDiv.appendChild(title);
                
                grouped[category].forEach(model => {
                    const item = document.createElement('div');
                    item.className = 'model-item';
                    
                    if (model.installed) {
                        item.style.background = '#f0fff4';
                        item.style.borderColor = '#48bb78';
                    }
                    
                    item.onclick = () => this.toggleModelSelection(model.name, item);
                    
                    const nameContainer = document.createElement('div');
                    nameContainer.style.display = 'flex';
                    nameContainer.style.alignItems = 'center';
                    
                    const name = document.createElement('div');
                    name.className = 'model-name';
                    name.textContent = model.name;
                    
                    const status = document.createElement('span');
                    status.className = 'model-status ' + (model.installed ? 'installed' : 'not-installed');
                    status.textContent = model.installed ? '✓ Instalado' : '⬇ Descargar';
                    
                    nameContainer.appendChild(name);
                    nameContainer.appendChild(status);
                    
                    const size = document.createElement('div');
                    size.className = 'model-size';
                    size.textContent = 'Tamaño: ' + model.size;
                    
                    const desc = document.createElement('div');
                    desc.className = 'model-description';
                    desc.textContent = model.description;
                    
                    const useCase = document.createElement('div');
                    useCase.className = 'model-use-case';
                    useCase.textContent = 'Uso: ' + model.use_case;
                    
                    item.appendChild(nameContainer);
                    item.appendChild(size);
                    item.appendChild(desc);
                    item.appendChild(useCase);
                    
                    categoryDiv.appendChild(item);
                });
                
                container.appendChild(categoryDiv);
            }
        });
    }

    /**
     * Toggle selección de modelo
     */
    toggleModelSelection(modelName, element) {
        if (!this.selectedModels) {
            this.selectedModels = [];
        }

        const index = this.selectedModels.indexOf(modelName);
        
        if (index > -1) {
            this.selectedModels.splice(index, 1);
            element.classList.remove('selected');
        } else {
            this.selectedModels.push(modelName);
            element.classList.add('selected');
        }
        
        const btn = document.getElementById('download-selected-btn');
        if (btn) {
            btn.disabled = this.selectedModels.length === 0;
            btn.textContent = 'Descargar Seleccionados (' + this.selectedModels.length + ')';
        }
    }

    /**
     * Confirmar descarga de modelos
     */
    async confirmDownloadModels() {
        if (!this.selectedModels || this.selectedModels.length === 0) {
            return;
        }

        const modal = document.getElementById('model-modal');
        if (modal) {
            modal.classList.remove('show');
        }

        const modelList = this.selectedModels.join('\n• ');
        if (!confirm('¿Descargar los siguientes modelos?\n\n• ' + modelList + '\n\nEsto puede tardar varios minutos dependiendo de tu conexión.')) {
            return;
        }

        if (window.ChatManager) {
            window.ChatManager.addMessage('📥 Descargando ' + this.selectedModels.length + ' modelo(s)... Esto puede tardar varios minutos.', 'user');
        }

        try {
            const response = await fetch('/system/download-models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ models: this.selectedModels })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                let message = '📊 **Resultado de descarga de modelos**\n\n';
                
                data.results.forEach(result => {
                    message += result.message + '\n';
                });
                
                message += '\n✅ **Kalin ha detectado automáticamente los nuevos modelos!**\n';
                message += 'No necesitas reiniciar. Los modelos están listos para usar.\n';
                
                message += '\n💡 **Modelos disponibles:**\n';
                this.selectedModels.forEach(model => {
                    message += '• ' + model + '\n';
                });
                message += '\n¡Kalin está listo para funcionar!';
                
                if (window.ChatManager) {
                    window.ChatManager.addMessage(message, 'assistant');
                }
            } else {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error al descargar modelos', 'assistant');
                }
            }
        } catch (error) {
            console.error('Error descargando modelos:', error);
            if (window.ChatManager) {
                window.ChatManager.addMessage('❌ Error: ' + error.message, 'assistant');
            }
        }

        this.selectedModels = [];
    }

    /**
     * Seleccionar modelo activo
     */
    async selectActiveModel() {
        try {
            const response = await fetch('/system/list-models');
            const data = await response.json();
            
            if (data.status === 'success' && data.models.length > 0) {
                const modelName = prompt('Selecciona un modelo:\n' + data.models.join('\n'));
                
                if (modelName && data.models.includes(modelName)) {
                    const setResponse = await fetch('/system/set-model', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model: modelName })
                    });

                    const setData = await setResponse.json();
                    
                    if (setData.status === 'success') {
                        if (window.ChatManager) {
                            window.ChatManager.addMessage(`✅ Modelo cambiado a: ${modelName}`, 'assistant');
                        }
                        this.loadActiveModel();
                    }
                }
            }
        } catch (error) {
            console.error('Error seleccionando modelo:', error);
        }
    }

    /**
     * Crear archivo .env
     */
    async createEnvFile() {
        const ollamaUrl = prompt('URL de Ollama (default: http://localhost:11434):', 'http://localhost:11434');
        const model = prompt('Modelo por defecto (default: qwen2.5-coder:7b):', 'qwen2.5-coder:7b');

        try {
            const response = await fetch('/system/create-env', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ollama_url: ollamaUrl || 'http://localhost:11434',
                    default_model: model || 'qwen2.5-coder:7b'
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('✅ Archivo .env creado correctamente. Reinicia Kalin para aplicar cambios.', 'assistant');
                }
            } else {
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error: ' + data.message, 'assistant');
                }
            }
        } catch (error) {
            console.error('Error creando .env:', error);
        }
    }
}

// Exportar como singleton
const uiManager = new UIManager();

if (typeof window !== 'undefined') {
    window.UIManager = uiManager;
}
