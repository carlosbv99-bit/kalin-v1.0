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

        // Toggle sidebar - COMENTADO (manejado por sidebar-functions.js)
        /*
        const menuToggle = document.querySelector('.menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        const sidebarClose = document.querySelector('.sidebar-close');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => this.toggleSidebar());
        }
        */
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
            
            // Manejar overlay
            const overlay = document.getElementById('overlay');
            if (overlay) {
                if (this.sidebar.classList.contains('open')) {
                    overlay.classList.add('show');
                } else {
                    overlay.classList.remove('show');
                }
            }
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
        console.log('📦 UIManager.exportExperience llamado');
        try {
            const response = await fetch('/experience/export');
            if (!response.ok) throw new Error('Error en la respuesta');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `kalin_experience_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            alert('✅ Experiencia exportada correctamente');
            console.log('✅ Experiencia exportada');
        } catch (error) {
            console.error('Error exportando experiencia:', error);
            alert('❌ Error al exportar experiencia: ' + error.message);
        }
    }

    /**
     * Importar experiencia
     */
    importExperience() {
        console.log('📥 UIManager.importExperience llamado');
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/experience/import', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.status === 'success') {
                    alert('✅ Experiencia importada correctamente\n' + result.message);
                } else {
                    alert('❌ Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error importando experiencia:', error);
                alert('❌ Error al importar experiencia: ' + error.message);
            }
        };
        
        input.click();
    }

    /**
     * Verificar dependencias
     */
    async checkDependencies() {
        console.log('🔍 UIManager.checkDependencies INICIADO');
        try {
            console.log('📡 Haciendo fetch a /system/check-dependencies...');
            const response = await fetch('/system/check-dependencies');
            console.log('📥 Respuesta recibida:', response.status);
            
            // Verificar que la respuesta sea JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('❌ La respuesta no es JSON. Content-Type:', contentType);
                alert('❌ Error: El servidor no devolvió datos válidos. Verifica que el backend esté corriendo.');
                return;
            }
            
            const data = await response.json();
            console.log('📦 Datos recibidos:', data);
            
            if (data.status === 'success') {
                console.log('✅ Mostrando reporte de dependencias');
                this.showDependencyReport(data);
            } else {
                console.error('❌ Error en respuesta:', data.message);
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('💥 Error verificando dependencias:', error);
            alert('❌ Error al verificar dependencias: ' + error.message);
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
        console.log('⚙️ UIManager.installDependencies INICIADO');
        
        if (!confirm('⚙️ ¿Deseas instalar todas las dependencias desde requirements.txt?\n\nEsto puede tardar varios minutos.')) {
            console.log('⏸️ Usuario canceló la instalación');
            return;
        }
        
        if (window.ChatManager) {
            window.ChatManager.addMessage('📦 Instalando dependencias... Esto puede tardar unos minutos.', 'assistant');
        }

        try {
            console.log('📡 Haciendo fetch a /system/install-dependencies...');
            const response = await fetch('/system/install-dependencies', {
                method: 'POST'
            });
            console.log('📥 Respuesta recibida:', response.status);
            
            // Verificar que la respuesta sea JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('❌ La respuesta no es JSON. Content-Type:', contentType);
                alert('❌ Error: El servidor no devolvió datos válidos. Verifica que el backend esté corriendo.');
                return;
            }

            const data = await response.json();
            console.log('📦 Datos recibidos:', data);
            
            if (data.status === 'success') {
                console.log('✅ Dependencias instaladas');
                if (window.ChatManager) {
                    window.ChatManager.addMessage('✅ Dependencias instaladas correctamente. Recarga la página.', 'assistant');
                }
                alert('✅ Dependencias instaladas correctamente\n\n⚠️ REINICIA Kalin para aplicar los cambios.\n\n' + data.message);
            } else {
                console.error('❌ Error en respuesta:', data.message);
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error: ' + data.message, 'assistant');
                }
                alert('❌ Error: ' + data.message + '\n\n' + (data.error || ''));
            }
        } catch (error) {
            console.error('💥 Error instalando dependencias:', error);
            if (window.ChatManager) {
                window.ChatManager.addMessage('❌ Error al instalar dependencias', 'assistant');
            }
            alert('❌ Error al instalar dependencias: ' + error.message);
        }
    }

    /**
     * Crear entorno virtual
     */
    async createVenv() {
        console.log('📦 UIManager.createVenv INICIADO');
        
        if (!confirm('📦 ¿Deseas crear un entorno virtual Python?\n\nEsto creará una carpeta .venv en el proyecto.')) {
            console.log('⏸️ Usuario canceló la creación de venv');
            return;
        }
        
        if (window.ChatManager) {
            window.ChatManager.addMessage('🔧 Creando entorno virtual...', 'assistant');
        }

        try {
            console.log('📡 Haciendo fetch a /system/create-venv...');
            const response = await fetch('/system/create-venv', {
                method: 'POST'
            });
            console.log('📥 Respuesta recibida:', response.status);
            
            // Verificar que la respuesta sea JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('❌ La respuesta no es JSON. Content-Type:', contentType);
                alert('❌ Error: El servidor no devolvió datos válidos. Verifica que el backend esté corriendo.');
                return;
            }

            const data = await response.json();
            console.log('📦 Datos recibidos:', data);
            
            if (data.status === 'success') {
                console.log('✅ Entorno virtual creado');
                if (window.ChatManager) {
                    window.ChatManager.addMessage('✅ Entorno virtual creado. Instala dependencias ahora.', 'assistant');
                }
                alert('✅ Entorno virtual creado correctamente\n\n⚠️ REINICIA Kalin para usar el nuevo entorno.\n\n' + data.message);
            } else {
                console.error('❌ Error en respuesta:', data.message);
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error: ' + data.message, 'assistant');
                }
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('💥 Error creando venv:', error);
            alert('❌ Error al crear entorno virtual: ' + error.message);
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
            'lightweight': '💚 Ligeros (2-4GB RAM)',
            'recommended': '⭐ Recomendados (4-8GB RAM)',
            'popular': '🔥 Populares (4-8GB RAM)',
            'latest': '✨ Últimos del Mercado (8-16GB RAM)',
            'high-performance': '🚀 Alto Rendimiento (16GB+ RAM)',
            'ultra': '💎 Ultra-Potentes (32GB+ RAM)'
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
                    
                    // Agregar indicador visual para modelos ultra-potentes
                    if (category === 'ultra') {
                        item.style.borderLeftWidth = '6px';
                        item.style.borderLeftColor = '#9f7aea';
                    } else if (category === 'high-performance') {
                        item.style.borderLeftWidth = '5px';
                        item.style.borderLeftColor = '#ed8936';
                    }
                    
                    item.onclick = () => this.toggleModelSelection(model.name, item);
                    
                    const nameContainer = document.createElement('div');
                    nameContainer.style.display = 'flex';
                    nameContainer.style.alignItems = 'center';
                    nameContainer.style.justifyContent = 'space-between';
                    
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
                    
                    // Agregar requisito de RAM
                    const ramReq = document.createElement('div');
                    ramReq.className = 'model-ram-requirement';
                    ramReq.style.cssText = 'font-size: 12px; color: #666; margin-top: 4px; font-weight: 500;';
                    
                    // Icono según categoría
                    let ramIcon = '💻';
                    if (category === 'ultra') ramIcon = '🖥️';
                    else if (category === 'high-performance') ramIcon = '⚡';
                    else if (category === 'lightweight') ramIcon = '💚';
                    
                    ramReq.textContent = `${ramIcon} RAM mínima: ${model.min_ram}`;
                    
                    // Agregar nota especial si existe
                    if (model.note) {
                        const note = document.createElement('div');
                        note.className = 'model-note';
                        note.style.cssText = 'font-size: 11px; color: #999; margin-top: 4px; font-style: italic; padding-left: 12px; border-left: 2px solid #ddd;';
                        note.textContent = model.note;
                        item.appendChild(note);
                    }
                    
                    const desc = document.createElement('div');
                    desc.className = 'model-description';
                    desc.textContent = model.description;
                    
                    const useCase = document.createElement('div');
                    useCase.className = 'model-use-case';
                    useCase.textContent = 'Uso: ' + model.use_case;
                    
                    item.appendChild(nameContainer);
                    item.appendChild(size);
                    item.appendChild(ramReq);
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
        console.log('🔘 toggleModelSelection:', modelName);
        
        if (!this.selectedModels) {
            this.selectedModels = [];
        }

        const index = this.selectedModels.indexOf(modelName);
        
        if (index > -1) {
            this.selectedModels.splice(index, 1);
            element.classList.remove('selected');
            console.log('➖ Modelo deseleccionado:', modelName);
        } else {
            this.selectedModels.push(modelName);
            element.classList.add('selected');
            console.log('➕ Modelo seleccionado:', modelName);
        }
        
        console.log('📦 Total seleccionados:', this.selectedModels.length, this.selectedModels);
        
        const btn = document.getElementById('download-selected-btn');
        if (btn) {
            btn.disabled = this.selectedModels.length === 0;
            btn.textContent = 'Descargar Seleccionados (' + this.selectedModels.length + ')';
            console.log('🔘 Botón estado:', btn.disabled ? 'DESHABILITADO' : 'HABILITADO');
        }
    }

    /**
     * Confirmar descarga de modelos
     */
    async confirmDownloadModels() {
        console.log('🔵 confirmDownloadModels llamado');
        console.log('📦 Modelos seleccionados:', this.selectedModels);
        
        if (!this.selectedModels || this.selectedModels.length === 0) {
            console.log('⚠️ No hay modelos seleccionados');
            alert('⚠️ Primero debes seleccionar al menos un modelo de la lista.');
            return;
        }

        const modal = document.getElementById('model-modal');
        if (modal) {
            modal.classList.remove('show');
            console.log('✅ Modal de selección cerrado');
        }

        // Mostrar alerta inmediata para confirmar que se inició
        alert('📥 Iniciando descarga de ' + this.selectedModels.length + ' modelo(s)...\n\nSe abrirá una ventana de progreso.');

        // Agregar mensaje al chat inmediatamente
        if (window.ChatManager) {
            window.ChatManager.addMessage('📥 **Iniciando descarga de modelos...**\n\nModelos seleccionados:\n' + 
                this.selectedModels.map(m => '• ' + m).join('\n') + 
                '\n\n⏳ Por favor espera, esto puede tardar varios minutos...', 'user');
        }

        // Mostrar modal de progreso
        console.log('🔄 Mostrando modal de progreso...');
        try {
            this.showDownloadProgressModal();
            console.log('✅ Modal de progreso mostrado correctamente');
        } catch (modalError) {
            console.error('💥 Error mostrando modal:', modalError);
            alert('Error al mostrar el modal de progreso: ' + modalError.message);
        }

        try {
            // Simular progreso inicial para cada modelo
            console.log('🎬 Iniciando simulación de progreso...');
            this.simulateDownloadProgress();
            
            console.log('📡 Enviando solicitud al backend...');
            const response = await fetch('/system/download-models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ models: this.selectedModels })
            });

            console.log('📥 Respuesta recibida:', response.status);
            const data = await response.json();
            console.log('📦 Datos:', data);
            
            if (data.status === 'success') {
                console.log('✅ Descarga exitosa, actualizando progreso...');
                // Actualizar progreso final para cada modelo
                this.updateDownloadProgress(data.results);
                
                // Esperar MÁS tiempo para que el usuario vea el resultado completo
                setTimeout(() => {
                    console.log('🔒 Cerrando modal de progreso...');
                    this.hideDownloadProgressModal();
                    
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
                }, 5000); // Aumentado a 5 segundos para ver mejor el progreso
            } else {
                console.log('❌ Error en respuesta:', data);
                this.hideDownloadProgressModal();
                if (window.ChatManager) {
                    window.ChatManager.addMessage('❌ Error al descargar modelos', 'assistant');
                }
            }
        } catch (error) {
            console.error('💥 Error descargando modelos:', error);
            this.hideDownloadProgressModal();
            if (window.ChatManager) {
                window.ChatManager.addMessage('❌ Error: ' + error.message, 'assistant');
            }
        }

        this.selectedModels = [];
        console.log('🧹 Modelos seleccionados limpiados');
    }

    /**
     * Simular progreso de descarga visualmente
     */
    simulateDownloadProgress() {
        this.selectedModels.forEach((modelName, index) => {
            // Marcar como "descargando" después de un delay
            setTimeout(() => {
                const itemId = 'download-' + modelName.replace(/[^a-zA-Z0-9]/g, '-');
                const item = document.getElementById(itemId);
                
                if (item && item.classList.contains('pending')) {
                    item.className = 'download-item downloading';
                    item.innerHTML = `
                        <div class="download-item-name">${modelName}</div>
                        <div class="download-item-status">⬇️ Descargando...</div>
                    `;
                }
            }, (index + 1) * 800); // Delay progresivo para efecto visual
        });
    }

    /**
     * Mostrar modal de progreso de descarga
     */
    showDownloadProgressModal() {
        console.log('📦 showDownloadProgressModal llamado');
        console.log('📦 selectedModels:', this.selectedModels);
        
        // Crear modal de progreso si no existe
        let progressModal = document.getElementById('download-progress-modal');
        console.log('🔍 Modal existente:', !!progressModal);
        
        if (!progressModal) {
            console.log('➕ Creando nuevo modal de progreso...');
            progressModal = document.createElement('div');
            progressModal.id = 'download-progress-modal';
            progressModal.className = 'modal-overlay';
            progressModal.innerHTML = `
                <div class="modal" style="max-width: 500px;">
                    <div class="modal-header">
                        <div class="modal-title">📥 Descargando Modelos</div>
                    </div>
                    <div class="modal-body">
                        <div id="download-progress-content">
                            <div style="text-align: center; padding: 20px;">
                                <div class="spinner" style="width: 50px; height: 50px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                                <p style="font-size: 16px; color: #666;">Iniciando descarga...</p>
                            </div>
                            <div id="download-models-list" style="margin-top: 20px;"></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(progressModal);
            console.log('✅ Modal agregado al DOM');
            
            // Agregar estilo de animación
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .download-item {
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 8px;
                    background: #f8f9fa;
                    border-left: 4px solid #ddd;
                    transition: all 0.3s ease;
                }
                .download-item.pending {
                    border-left-color: #ffc107;
                }
                .download-item.downloading {
                    border-left-color: #3498db;
                    background: #ebf5fb;
                }
                .download-item.completed {
                    border-left-color: #28a745;
                    background: #d4edda;
                }
                .download-item.error {
                    border-left-color: #dc3545;
                    background: #f8d7da;
                }
                .download-item-name {
                    font-weight: 600;
                    margin-bottom: 4px;
                }
                .download-item-status {
                    font-size: 13px;
                    color: #666;
                }
            `;
            document.head.appendChild(style);
            console.log('✅ Estilos agregados');
        }
        
        console.log('👁️ Mostrando modal (agregando clase show)...');
        progressModal.classList.add('show');
        console.log('✅ Clase show agregada');
        
        // Mostrar lista inicial de modelos pendientes
        const listContainer = document.getElementById('download-models-list');
        console.log('🔍 List container encontrado:', !!listContainer);
        
        if (listContainer) {
            listContainer.innerHTML = '';
            console.log('📝 Agregando', this.selectedModels.length, 'modelos a la lista...');
            
            this.selectedModels.forEach(modelName => {
                const item = document.createElement('div');
                item.className = 'download-item pending';
                item.id = 'download-' + modelName.replace(/[^a-zA-Z0-9]/g, '-');
                item.innerHTML = `
                    <div class="download-item-name">${modelName}</div>
                    <div class="download-item-status">⏳ Pendiente...</div>
                `;
                listContainer.appendChild(item);
                console.log('➕ Modelo agregado:', modelName);
            });
            console.log('✅ Lista de modelos completada');
        } else {
            console.error('❌ No se encontró download-models-list');
        }
        
        console.log('✅ showDownloadProgressModal completado');
    }

    /**
     * Actualizar progreso de descarga
     */
    updateDownloadProgress(results) {
        results.forEach((result, index) => {
            setTimeout(() => {
                const itemId = 'download-' + result.model.replace(/[^a-zA-Z0-9]/g, '-');
                const item = document.getElementById(itemId);
                
                if (item) {
                    if (result.status === 'success' || result.status === 'already_installed') {
                        item.className = 'download-item completed';
                        item.innerHTML = `
                            <div class="download-item-name">${result.model}</div>
                            <div class="download-item-status">✅ ${result.message}</div>
                        `;
                    } else if (result.status === 'downloading') {
                        item.className = 'download-item downloading';
                        item.innerHTML = `
                            <div class="download-item-name">${result.model}</div>
                            <div class="download-item-status">⬇️ Descargando...</div>
                        `;
                    } else {
                        item.className = 'download-item error';
                        item.innerHTML = `
                            <div class="download-item-name">${result.model}</div>
                            <div class="download-item-status">❌ ${result.message}</div>
                        `;
                    }
                }
            }, index * 500); // Delay para efecto visual secuencial
        });
    }

    /**
     * Ocultar modal de progreso
     */
    hideDownloadProgressModal() {
        const progressModal = document.getElementById('download-progress-modal');
        if (progressModal) {
            progressModal.classList.remove('show');
        }
    }

    /**
     * Seleccionar modelo activo
     */
    async selectActiveModel() {
        console.log('🤖 UIManager.selectActiveModel INICIADO');
        
        try {
            console.log('📡 Haciendo fetch a /system/available-models...');
            const response = await fetch('/system/available-models');
            console.log('📥 Respuesta recibida:', response.status);
            
            // Verificar que la respuesta sea JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('❌ La respuesta no es JSON. Content-Type:', contentType);
                alert('❌ Error: El servidor no devolvió datos válidos. Verifica que el backend esté corriendo.');
                return;
            }
            
            const data = await response.json();
            console.log('📦 Datos recibidos:', data);
            
            if (data.status === 'success') {
                // Filtrar solo modelos instalados
                const installedModels = data.models.filter(model => model.installed);
                console.log('✅ Modelos instalados disponibles:', installedModels.length);
                
                if (installedModels.length === 0) {
                    console.warn('⚠️ No hay modelos instalados');
                    alert('⚠️ No hay modelos instalados.\n\nPrimero debes descargar un modelo usando el botón "Descargar Modelos IA" en el menú lateral.');
                    return;
                }
                
                // Mostrar modal con lista de modelos instalados
                this.showSelectModelModal(installedModels);
            } else {
                console.error('❌ Error en respuesta:', data.message);
                alert('❌ Error al obtener modelos: ' + data.message);
            }
        } catch (error) {
            console.error('💥 Error seleccionando modelo:', error);
            alert('❌ Error al seleccionar modelo: ' + error.message + '\n\nVerifica que el servidor esté corriendo.');
        }
    }

    /**
     * Mostrar modal de selección de modelo
     */
    showSelectModelModal(installedModels) {
        console.log('📋 Mostrando modal de selección de modelo');
        
        const modal = document.getElementById('active-model-modal');
        const modelList = document.getElementById('active-model-list');
        
        if (!modal || !modelList) {
            console.error('❌ Modal o lista de modelos no encontrados');
            alert('❌ Error: No se pudo abrir el selector de modelos');
            return;
        }
        
        // Limpiar lista anterior
        modelList.innerHTML = '';
        
        // Crear elementos para cada modelo instalado
        installedModels.forEach((model, index) => {
            const item = document.createElement('div');
            item.className = 'model-item';
            item.style.cursor = 'pointer';
            item.style.padding = '12px';
            item.style.margin = '8px 0';
            item.style.border = '1px solid #e0e0e0';
            item.style.borderRadius = '8px';
            item.style.transition = 'all 0.2s';
            item.style.background = '#f8f9fa';
            
            // Efecto hover
            item.onmouseenter = () => {
                item.style.background = '#e3f2fd';
                item.style.borderColor = '#2196f3';
                item.style.transform = 'translateX(4px)';
            };
            item.onmouseleave = () => {
                item.style.background = '#f8f9fa';
                item.style.borderColor = '#e0e0e0';
                item.style.transform = 'translateX(0)';
            };
            
            // Información del modelo
            const nameDiv = document.createElement('div');
            nameDiv.style.fontWeight = '600';
            nameDiv.style.fontSize = '15px';
            nameDiv.style.marginBottom = '4px';
            nameDiv.textContent = `🤖 ${model.name}`;
            
            const sizeDiv = document.createElement('div');
            sizeDiv.style.fontSize = '13px';
            sizeDiv.style.color = '#666';
            sizeDiv.style.marginBottom = '4px';
            sizeDiv.textContent = `📦 Tamaño: ${model.size || 'Desconocido'}`;
            
            const descDiv = document.createElement('div');
            descDiv.style.fontSize = '13px';
            descDiv.style.color = '#888';
            descDiv.textContent = model.description || model.use_case || '';
            
            item.appendChild(nameDiv);
            item.appendChild(sizeDiv);
            item.appendChild(descDiv);
            
            // Click para activar modelo
            item.onclick = async () => {
                console.log(`🎯 Modelo seleccionado: ${model.name}`);
                
                if (confirm(`🤖 ¿Deseas activar el modelo "${model.name}"?`)) {
                    await this.activateModel(model.name);
                }
            };
            
            modelList.appendChild(item);
        });
        
        // Agregar mensaje informativo al final
        const infoDiv = document.createElement('div');
        infoDiv.style.padding = '12px';
        infoDiv.style.marginTop = '12px';
        infoDiv.style.background = '#fff3cd';
        infoDiv.style.borderLeft = '4px solid #ffc107';
        infoDiv.style.borderRadius = '4px';
        infoDiv.style.fontSize = '13px';
        infoDiv.style.color = '#856404';
        infoDiv.innerHTML = '💡 <strong>Consejo:</strong> Haz clic en un modelo para activarlo. El cambio se aplicará inmediatamente.';
        modelList.appendChild(infoDiv);
        
        // Mostrar modal
        modal.classList.add('show');
        console.log('✅ Modal de selección mostrado');
    }

    /**
     * Activar un modelo específico
     */
    async activateModel(modelName) {
        console.log(`📡 Activando modelo: ${modelName}`);
        
        try {
            const setResponse = await fetch('/system/set-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: modelName })
            });
            console.log('📥 Respuesta received:', setResponse.status);
            
            // Verificar que la respuesta sea JSON
            const setContentType = setResponse.headers.get('content-type');
            if (!setContentType || !setContentType.includes('application/json')) {
                console.error('❌ La respuesta de activación no es JSON');
                alert('❌ Error al activar el modelo. El servidor no devolvió datos válidos.');
                return;
            }

            const setData = await setResponse.json();
            console.log('📦 Datos de activación:', setData);
            
            if (setData.status === 'success') {
                console.log('✅ Modelo activado correctamente');
                
                // Cerrar modal
                const modal = document.getElementById('active-model-modal');
                if (modal) {
                    modal.classList.remove('show');
                }
                
                alert('✅ Modelo activado correctamente: ' + modelName + '\n\nEl cambio se aplicará inmediatamente.');
                
                if (window.ChatManager) {
                    window.ChatManager.addMessage(`✅ Modelo cambiado a: ${modelName}`, 'assistant');
                }
                
                // Recargar indicador de modelo activo
                this.loadActiveModel();
            } else {
                console.error('❌ Error activando modelo:', setData.message);
                alert('❌ Error al activar modelo: ' + setData.message);
            }
        } catch (error) {
            console.error('💥 Error activando modelo:', error);
            alert('❌ Error al activar modelo: ' + error.message);
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

    /**
     * Instalación rápida
     */
    async quickInstall() {
        console.log('🚀 UIManager.quickInstall llamado');
        
        if (!confirm('🚀 Instalación Rápida\n\nEsto ejecutará:\n1. Crear entorno virtual\n2. Instalar dependencias\n3. Descargar modelos\n\n¿Deseas continuar?')) {
            return;
        }
        
        try {
            // Paso 1: Crear entorno virtual
            alert('📦 Paso 1: Creando entorno virtual...');
            const venvResponse = await fetch('/system/create-venv', { method: 'POST' });
            const venvResult = await venvResponse.json();
            console.log('Venv:', venvResult);
            
            // Paso 2: Instalar dependencias
            alert('⚙️ Paso 2: Instalando dependencias...\n\nEsto puede tardar varios minutos.');
            const depsResponse = await fetch('/system/install-deps', { method: 'POST' });
            const depsResult = await depsResponse.json();
            console.log('Dependencies:', depsResult);
            
            // Paso 3: Descargar modelos
            alert('📥 Paso 3: Abriendo selector de modelos...');
            this.downloadModels();
            
            alert('✅ Instalación rápida completada\n\nPor favor, verifica que los modelos se hayan descargado correctamente.');
        } catch (error) {
            console.error('Error en instalación rápida:', error);
            alert('❌ Error durante la instalación: ' + error.message);
        }
    }

    /**
     * Toggle auto-dependencias
     */
    toggleAutoDependencies() {
        // Buscar el checkbox en ambos lugares (sidebar y dropdown)
        const toggle = document.getElementById('auto-deps-toggle') || 
                      document.getElementById('auto-deps-toggle-dropdown');
        
        if (toggle) {
            const enabled = toggle.checked;
            console.log('Auto-dependencias:', enabled ? 'activado' : 'desactivado');
            localStorage.setItem('auto_dependencies', enabled);
            
            // Sincronizar ambos checkboxes si existen
            const toggleSidebar = document.getElementById('auto-deps-toggle');
            const toggleDropdown = document.getElementById('auto-deps-toggle-dropdown');
            
            if (toggleSidebar && toggleDropdown) {
                toggleSidebar.checked = enabled;
                toggleDropdown.checked = enabled;
            }
            
            // Guardar en el backend también
            fetch('/system/set-auto-deps', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: enabled })
            }).then(() => {
                alert(enabled ? '✅ Detección automática activada' : '⏸️ Detección automática desactivada');
            }).catch(error => {
                console.error('Error guardando configuración:', error);
                alert('⚠️ Configuración guardada localmente pero hubo un error al guardar en el servidor');
            });
        }
    }

    /**
     * Verificar dependencias pendientes
     */
    async checkPendingDependencies() {
        console.log('🔍 UIManager.checkPendingDependencies llamado');
        try {
            const response = await fetch('/system/check-pending-deps');
            const result = await response.json();
            
            if (result.status === 'success') {
                if (result.pending.length === 0) {
                    alert('✅ No hay dependencias pendientes\n\nTodas las bibliotecas están instaladas.');
                } else {
                    const depsList = result.pending.join('\n');
                    alert(`📦 Dependencias pendientes (${result.pending.length}):\n\n${depsList}\n\nUsa "Instalar dependencias pendientes" para instalarlas.`);
                }
            } else {
                alert('❌ Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error verificando dependencias:', error);
            alert('❌ Error al verificar dependencias: ' + error.message);
        }
    }

    /**
     * Instalar dependencias pendientes
     */
    async installPendingDependencies() {
        console.log('⚙️ UIManager.installPendingDependencies llamado');
        
        if (!confirm('⚙️ ¿Deseas instalar las dependencias pendientes?\n\nEsto puede tardar varios minutos.')) {
            return;
        }
        
        try {
            alert('⚙️ Instalando dependencias...\n\nPor favor espera, esto puede tardar.');
            const response = await fetch('/system/install-pending-deps', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                alert('✅ Dependencias instaladas correctamente\n' + result.message);
            } else {
                alert('❌ Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error instalando dependencias:', error);
            alert('❌ Error al instalar dependencias: ' + error.message);
        }
    }

    /**
     * Ver/Editar archivo .env
     */
    async viewEnvFile() {
        console.log('📄 UIManager.viewEnvFile llamado');
        
        try {
            const response = await fetch('/system/read-env');
            const result = await response.json();
            
            if (result.status !== 'success') {
                alert('❌ Error al leer .env: ' + result.message);
                return;
            }
            
            // Mostrar en un prompt editable
            const newContent = prompt('📄 Archivo .env\n\nEdita la configuración (ten cuidado):', result.content);
            
            if (newContent !== null && newContent !== result.content) {
                // Guardar cambios
                const saveResponse = await fetch('/system/update-env', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: newContent })
                });
                const saveResult = await saveResponse.json();
                
                if (saveResult.status === 'success') {
                    alert('✅ Archivo .env actualizado\n\n⚠️ REINICIA Kalin para aplicar los cambios.');
                } else {
                    alert('❌ Error al guardar: ' + saveResult.message);
                }
            }
        } catch (error) {
            console.error('Error accediendo a .env:', error);
            alert('❌ Error al acceder al archivo .env: ' + error.message);
        }
    }

    /**
     * Cerrar modal de modelos
     */
    closeModelModal() {
        console.log('❌ UIManager.closeModelModal llamado');
        const modal = document.getElementById('model-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    /**
     * Cerrar modal de modelo activo
     */
    closeActiveModelModal() {
        console.log('❌ UIManager.closeActiveModelModal llamado');
        const modal = document.getElementById('active-model-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }
}

// Exportar como singleton
const uiManager = new UIManager();

// Registrar funciones globales INMEDIATAMENTE (antes de DOMContentLoaded)
if (typeof window !== 'undefined') {
    window.UIManager = uiManager;
    
    console.log('🔧 Registrando funciones globales del sidebar...');
    
    // Exponer métodos como funciones globales para compatibilidad con onclick
    window.exportExperience = () => {
        console.log('📦 exportExperience wrapper llamado');
        return uiManager.exportExperience();
    };
    window.importExperience = () => {
        console.log('📥 importExperience wrapper llamado');
        return uiManager.importExperience();
    };
    window.quickInstall = () => {
        console.log('🚀 quickInstall wrapper llamado');
        return uiManager.quickInstall();
    };
    window.toggleAutoDependencies = () => {
        console.log('⚙️ toggleAutoDependencies wrapper llamado');
        return uiManager.toggleAutoDependencies();
    };
    window.checkPendingDependencies = () => {
        console.log('🔍 checkPendingDependencies wrapper llamado');
        return uiManager.checkPendingDependencies();
    };
    window.installPendingDependencies = () => {
        console.log('⚙️ installPendingDependencies wrapper llamado');
        return uiManager.installPendingDependencies();
    };
    window.checkDependencies = () => {
        console.log('🔍 checkDependencies wrapper llamado');
        return uiManager.checkDependencies();
    };
    window.createVenv = () => {
        console.log('📦 createVenv wrapper llamado');
        return uiManager.createVenv();
    };
    window.installDependencies = () => {
        console.log('⚙️ installDependencies wrapper llamado');
        return uiManager.installDependencies();
    };
    window.downloadModels = () => {
        console.log('📥 downloadModels wrapper llamado');
        return uiManager.downloadModels();
    };
    window.selectActiveModel = () => {
        console.log('🤖 selectActiveModel wrapper llamado');
        return uiManager.selectActiveModel();
    };
    window.viewEnvFile = () => {
        console.log('📄 viewEnvFile wrapper llamado');
        return uiManager.viewEnvFile();
    };
    window.closeModelModal = () => {
        console.log('❌ closeModelModal wrapper llamado');
        return uiManager.closeModelModal();
    };
    window.confirmDownloadModels = () => {
        console.log('⬇️ confirmDownloadModels wrapper llamado');
        console.log('📦 uiManager existe:', !!uiManager);
        console.log('📦 selectedModels:', uiManager ? uiManager.selectedModels : 'N/A');
        if (!uiManager) {
            console.error('❌ uiManager no está inicializado');
            alert('Error: uiManager no está disponible. Recarga la página.');
            return;
        }
        return uiManager.confirmDownloadModels();
    };
    window.closeActiveModelModal = () => {
        console.log('❌ closeActiveModelModal wrapper llamado');
        return uiManager.closeActiveModelModal();
    };
    
    console.log('✅ Funciones de UIManager expuestas globalmente para compatibilidad');
    console.log('✅ Funciones registradas:', Object.keys(window).filter(k => ['exportExperience', 'importExperience', 'checkDependencies', 'createVenv', 'installDependencies', 'downloadModels', 'selectActiveModel'].includes(k)));
}

/**
 * Mostrar modal de confirmación personalizado con modo oscuro
 */
function showConfirmModal(message, onConfirm, onCancel) {
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.background = 'rgba(0, 0, 0, 0.7)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = '10000';
    
    // Crear modal
    const modal = document.createElement('div');
    modal.style.background = '#1e1e1e';
    modal.style.color = '#ffffff';
    modal.style.padding = '24px';
    modal.style.borderRadius = '12px';
    modal.style.maxWidth = '500px';
    modal.style.width = '90%';
    modal.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.5)';
    modal.style.border = '1px solid #333';
    
    // Mensaje
    const messageDiv = document.createElement('div');
    messageDiv.style.marginBottom = '20px';
    messageDiv.style.whiteSpace = 'pre-line';
    messageDiv.style.lineHeight = '1.6';
    messageDiv.style.fontSize = '14px';
    messageDiv.textContent = message;
    
    // Botones
    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'flex';
    buttonContainer.style.gap = '12px';
    buttonContainer.style.justifyContent = 'flex-end';
    
    // Botón Cancelar
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancelar';
    cancelBtn.style.padding = '10px 20px';
    cancelBtn.style.border = '1px solid #555';
    cancelBtn.style.background = '#2d2d2d';
    cancelBtn.style.color = '#ffffff';
    cancelBtn.style.borderRadius = '6px';
    cancelBtn.style.cursor = 'pointer';
    cancelBtn.style.fontSize = '14px';
    cancelBtn.onmouseenter = () => {
        cancelBtn.style.background = '#3d3d3d';
    };
    cancelBtn.onmouseleave = () => {
        cancelBtn.style.background = '#2d2d2d';
    };
    cancelBtn.onclick = () => {
        document.body.removeChild(overlay);
        if (onCancel) onCancel();
    };
    
    // Botón Aceptar
    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = 'Aceptar';
    confirmBtn.style.padding = '10px 20px';
    confirmBtn.style.border = 'none';
    confirmBtn.style.background = '#dc3545';
    confirmBtn.style.color = '#ffffff';
    confirmBtn.style.borderRadius = '6px';
    confirmBtn.style.cursor = 'pointer';
    confirmBtn.style.fontSize = '14px';
    confirmBtn.onmouseenter = () => {
        confirmBtn.style.background = '#c82333';
    };
    confirmBtn.onmouseleave = () => {
        confirmBtn.style.background = '#dc3545';
    };
    confirmBtn.onclick = () => {
        document.body.removeChild(overlay);
        if (onConfirm) onConfirm();
    };
    
    buttonContainer.appendChild(cancelBtn);
    buttonContainer.appendChild(confirmBtn);
    
    modal.appendChild(messageDiv);
    modal.appendChild(buttonContainer);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Focus en botón Aceptar
    setTimeout(() => confirmBtn.focus(), 100);
}

/**
 * Mostrar indicador de progreso de descarga de modelo
 */
function showModelDownloadIndicator(modelName) {
    const indicator = document.getElementById('model-download-indicator');
    const textSpan = document.getElementById('model-download-text');
    
    if (indicator && textSpan) {
        textSpan.textContent = `Descargando modelo ${modelName}...`;
        indicator.style.display = 'flex';
        console.log(`📥 Indicador de descarga mostrado para: ${modelName}`);
    }
}

/**
 * Ocultar indicador de progreso de descarga de modelo
 */
function hideModelDownloadIndicator() {
    const indicator = document.getElementById('model-download-indicator');
    
    if (indicator) {
        indicator.style.display = 'none';
        console.log('📥 Indicador de descarga ocultado');
    }
}

/**
 * Actualizar texto del indicador de descarga
 */
function updateModelDownloadStatus(message) {
    const textSpan = document.getElementById('model-download-text');
    
    if (textSpan) {
        textSpan.textContent = message;
    }
}

/**
 * Mostrar alerta personalizada con modo oscuro
 */
function showAlertModal(message, type = 'info') {
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.background = 'rgba(0, 0, 0, 0.7)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = '10000';
    
    // Crear modal
    const modal = document.createElement('div');
    modal.style.background = '#1e1e1e';
    modal.style.color = '#ffffff';
    modal.style.padding = '24px';
    modal.style.borderRadius = '12px';
    modal.style.maxWidth = '450px';
    modal.style.width = '90%';
    modal.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.5)';
    modal.style.border = '1px solid #333';
    
    // Icono según tipo
    let icon = 'ℹ️';
    let borderColor = '#17a2b8';
    if (type === 'success') {
        icon = '✅';
        borderColor = '#28a745';
    } else if (type === 'error') {
        icon = '❌';
        borderColor = '#dc3545';
    } else if (type === 'warning') {
        icon = '⚠️';
        borderColor = '#ffc107';
    }
    
    modal.style.borderLeft = `4px solid ${borderColor}`;
    
    // Contenido
    const contentDiv = document.createElement('div');
    contentDiv.style.display = 'flex';
    contentDiv.style.alignItems = 'flex-start';
    contentDiv.style.gap = '12px';
    contentDiv.style.marginBottom = '20px';
    
    const iconSpan = document.createElement('span');
    iconSpan.textContent = icon;
    iconSpan.style.fontSize = '20px';
    
    const messageDiv = document.createElement('div');
    messageDiv.style.flex = '1';
    messageDiv.style.whiteSpace = 'pre-line';
    messageDiv.style.lineHeight = '1.6';
    messageDiv.style.fontSize = '14px';
    messageDiv.textContent = message;
    
    contentDiv.appendChild(iconSpan);
    contentDiv.appendChild(messageDiv);
    
    // Botón Cerrar
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Cerrar';
    closeBtn.style.padding = '10px 24px';
    closeBtn.style.border = 'none';
    closeBtn.style.background = '#0066ff';
    closeBtn.style.color = '#ffffff';
    closeBtn.style.borderRadius = '6px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.fontSize = '14px';
    closeBtn.style.float = 'right';
    closeBtn.onmouseenter = () => {
        closeBtn.style.background = '#0052cc';
    };
    closeBtn.onmouseleave = () => {
        closeBtn.style.background = '#0066ff';
    };
    closeBtn.onclick = () => {
        document.body.removeChild(overlay);
    };
    
    modal.appendChild(contentDiv);
    modal.appendChild(closeBtn);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Auto-focus en botón cerrar
    setTimeout(() => closeBtn.focus(), 100);
}

/**
 * Cargar modelos de Ollama y mostrar opciones contextuales
 */
async function loadOllamaModelsList() {
    const modelsList = document.getElementById('ollama-models-list');
    if (!modelsList) return;
    
    try {
        // Obtener lista de modelos instalados desde backend
        const response = await fetch('/api/ollama/models');
        const data = await response.json();
        
        if (data.status !== 'success' || !data.models) {
            modelsList.innerHTML = `
                <div class="dropdown-item" style="color: #999; font-style: italic;">
                    <span>Error al cargar modelos</span>
                </div>
            `;
            return;
        }
        
        // Lista de modelos disponibles para descargar
        const availableModels = [
            { name: 'llama3.2', displayName: '🦙 Llama 3.2', size: '3B', description: 'Ligero y rápido' },
            { name: 'llama3.1', displayName: '🦙 Llama 3.1', size: '8B', description: 'Balanceado' },
            { name: 'mistral', displayName: '💨 Mistral', size: '7B', description: 'Eficiente' },
            { name: 'qwen2.5', displayName: '🔵 Qwen 2.5', size: '7B', description: 'Excelente para código' },
            { name: 'codellama', displayName: '🦙 CodeLlama', size: '7B', description: 'Especializado en código' },
            { name: 'deepseek-coder', displayName: '🔍 DeepSeek', size: '6.7B', description: 'Optimizado para programación' }
        ];
        
        // Crear lista de modelos instalados para referencia rápida
        const installedModelNames = data.models.filter(m => m.installed).map(m => m.name);
        
        // Limpiar lista
        modelsList.innerHTML = '';
        
        // Agregar cada modelo con su estado
        availableModels.forEach(model => {
            const isInstalled = installedModelNames.some(installed => 
                installed.includes(model.name) || model.name.includes(installed)
            );
            
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.style.position = 'relative';
            item.style.cursor = 'pointer'; // AGREGAR: Indicar que es clickeable
            
            // Efecto hover para mejor UX
            item.onmouseenter = function(e) {
                this.style.background = '#e3f2fd';
                // Si está instalado, también mostrar submenú
                if (isInstalled) {
                    showModelSubmenu(e, model.name);
                }
            };
            item.onmouseleave = function(e) {
                this.style.background = '';
                // Si está instalado, ocultar submenú
                if (isInstalled) {
                    hideModelSubmenu(e, model.name);
                }
            };
            
            // Contenido principal del modelo
            const content = document.createElement('div');
            content.style.display = 'flex';
            content.style.alignItems = 'center';
            content.style.justifyContent = 'space-between';
            content.style.width = '100%';
            
            // Información del modelo
            const infoDiv = document.createElement('div');
            infoDiv.style.flex = '1';
            
            const nameSpan = document.createElement('span');
            nameSpan.textContent = `${model.displayName} (${model.size})`;
            nameSpan.style.fontWeight = isInstalled ? '600' : '400';
            
            const descSpan = document.createElement('span');
            descSpan.textContent = ` - ${model.description}`;
            descSpan.style.fontSize = '12px';
            descSpan.style.color = '#666';
            
            infoDiv.appendChild(nameSpan);
            infoDiv.appendChild(descSpan);
            
            // Indicador de estado
            const statusSpan = document.createElement('span');
            statusSpan.style.marginLeft = '8px';
            statusSpan.style.fontSize = '12px';
            
            if (isInstalled) {
                statusSpan.textContent = '✅';
                statusSpan.title = 'Instalado - Clic para usar, hover para ver opciones';
                statusSpan.style.color = '#28a745';
            } else {
                statusSpan.textContent = '⬇️';
                statusSpan.title = 'No instalado - Clic para descargar';
                statusSpan.style.color = '#ffc107';
            }
            
            content.appendChild(infoDiv);
            content.appendChild(statusSpan);
            
            // Botón de eliminar (solo visible en hover para modelos instalados)
            if (isInstalled) {
                const deleteBtn = document.createElement('span');
                deleteBtn.innerHTML = '🗑️';
                deleteBtn.title = 'Eliminar modelo';
                deleteBtn.style.marginLeft = '8px';
                deleteBtn.style.cursor = 'pointer';
                deleteBtn.style.opacity = '0'; // Oculto por defecto
                deleteBtn.style.transition = 'opacity 0.2s';
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    if (confirm(`¿Estás seguro de borrar el modelo "${model.name}"?\n\nEsta acción no se puede deshacer.`)) {
                        deleteOllamaModel(model.name);
                    }
                };
                content.appendChild(deleteBtn);
                
                // Mostrar botón de eliminar en hover
                item.onmouseenter = function(e) {
                    this.style.background = '#e3f2fd';
                    deleteBtn.style.opacity = '1'; // Mostrar botón
                };
                item.onmouseleave = function(e) {
                    this.style.background = '';
                    deleteBtn.style.opacity = '0'; // Ocultar botón
                };
            } else {
                // Efecto hover simple para modelos no instalados
                item.onmouseenter = function(e) {
                    this.style.background = '#e3f2fd';
                };
                item.onmouseleave = function(e) {
                    this.style.background = '';
                };
            }
            
            item.appendChild(content);
            
            // AGREGAR: Evento de clic - modelos instalados preguntan si se desea eliminar
            item.onclick = (e) => {
                e.stopPropagation();
                if (isInstalled) {
                    // Modelo instalado: preguntar si desea eliminar con modal oscuro
                    const message1 = `¿Deseas eliminar este modelo de tu equipo?\n\nModelo: ${model.displayName} (${model.size})\n\nEsta acción no se puede deshacer.`;
                    
                    showConfirmModal(message1, () => {
                        // PRIMERA CONFIRMACIÓN ACEPTADA - Mostrar segunda confirmación
                        const message2 = `⚠️ ÚLTIMA CONFIRMACIÓN\n\n¿Estás COMPLETAMENTE SEGURO de que deseas eliminar "${model.name}"?\n\n• Se liberará espacio en disco\n• Tendrás que descargarlo nuevamente si lo necesitas\n• Esta acción NO se puede deshacer\n\nHaz clic en ACEPTAR para eliminar o CANCELAR para mantenerlo.`;
                        
                        showConfirmModal(message2, () => {
                            // SEGUNDA CONFIRMACIÓN ACEPTADA - Eliminar modelo
                            deleteOllamaModel(model.name);
                        });
                    });
                } else {
                    // Modelo no instalado: preguntar si desea descargar con modal oscuro
                    const message = `¿Deseas descargar e instalar este modelo?\n\nModelo: ${model.displayName} (${model.size})\nDescripción: ${model.description}\n\nLa descarga puede tardar varios minutos dependiendo de tu conexión a internet.`;
                    
                    showConfirmModal(message, () => {
                        // CONFIRMACIÓN ACEPTADA - Descargar modelo
                        downloadLocalModel(model.name);
                    });
                }
            };
            
            modelsList.appendChild(item);
        });
        
        console.log(`✅ Cargados ${availableModels.length} modelos (${installedModelNames.length} instalados)`);
        
    } catch (error) {
        console.error('❌ Error cargando modelos de Ollama:', error);
        modelsList.innerHTML = `
            <div class="dropdown-item" style="color: #dc3545;">
                <span>Error: ${error.message}</span>
            </div>
        `;
    }
}

/**
 * Mostrar submenú de modelo
 */
function showModelSubmenu(event, modelName) {
    const submenu = document.getElementById(`submenu-${modelName}`);
    if (submenu) {
        // Ocultar otros submenús primero
        hideAllSubmenus();
        submenu.style.display = 'block';
    }
}

/**
 * Ocultar submenú de modelo
 */
function hideModelSubmenu(event, modelName) {
    // No ocultar inmediatamente para permitir hover en el submenu
    setTimeout(() => {
        const submenu = document.getElementById(`submenu-${modelName}`);
        if (submenu && !submenu.matches(':hover')) {
            submenu.style.display = 'none';
        }
    }, 100);
}

/**
 * Ocultar todos los submenús
 */
function hideAllSubmenus() {
    const allSubmenus = document.querySelectorAll('#ollama-models-list .dropdown-submenu');
    allSubmenus.forEach(menu => {
        menu.style.display = 'none';
    });
}

/**
 * Activar modelo por nombre
 */
async function activateModelByName(modelName) {
    try {
        const response = await fetch('/system/set-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: modelName })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlertModal(`Modelo activado: ${modelName}`, 'success');
            if (window.UIManager) {
                window.UIManager.loadActiveModel();
            }
        } else {
            showAlertModal(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error activando modelo:', error);
        showAlertModal(`Error al activar modelo: ${error.message}`, 'error');
    }
}

/**
 * Borrar modelo de Ollama
 */
async function deleteOllamaModel(modelName) {
    try {
        const response = await fetch('/api/ollama/delete-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: modelName })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlertModal(`Modelo borrado: ${modelName}`, 'success');
            // Recargar lista de modelos
            setTimeout(() => loadOllamaModelsList(), 500);
        } else {
            showAlertModal(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error borrando modelo:', error);
        showAlertModal(`Error al borrar modelo: ${error.message}`, 'error');
    }
}

// Verificación adicional cuando DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Verificando funciones del menú de configuración...');
    
    const requiredFunctions = [
        'selectActiveModel',
        'downloadModels', 
        'installDependencies',
        'createVenv'
    ];
    
    let allRegistered = true;
    requiredFunctions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ Función ${funcName} registrada correctamente`);
        } else {
            console.error(`❌ Función ${funcName} NO está registrada`);
            allRegistered = false;
        }
    });
    
    if (allRegistered) {
        console.log('✅ Todas las funciones del menú de configuración están disponibles');
    } else {
        console.error('❌ ALGUNAS FUNCIONES NO ESTÁN REGISTRADAS - Los botones pueden no funcionar');
    }
});
