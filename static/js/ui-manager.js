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
        const toggle = document.getElementById('auto-deps-toggle');
        if (toggle) {
            const enabled = toggle.checked;
            console.log('Auto-dependencias:', enabled ? 'activado' : 'desactivado');
            localStorage.setItem('auto_dependencies', enabled);
            
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
     * Confirmar descarga de modelos
     */
    confirmDownloadModels() {
        console.log('⬇️ UIManager.confirmDownloadModels llamado');
        alert('⬇️ Descargando modelos seleccionados...');
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
        return uiManager.confirmDownloadModels();
    };
    window.closeActiveModelModal = () => {
        console.log('❌ closeActiveModelModal wrapper llamado');
        return uiManager.closeActiveModelModal();
    };
    
    console.log('✅ Funciones de UIManager expuestas globalmente para compatibilidad');
    console.log('✅ Funciones registradas:', Object.keys(window).filter(k => ['exportExperience', 'importExperience', 'checkDependencies', 'createVenv', 'installDependencies', 'downloadModels', 'selectActiveModel'].includes(k)));
}
