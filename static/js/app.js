/**
 * Kalin Frontend - Punto de Entrada Principal
 * Inicializa y coordina todos los módulos del frontend
 */

// Importar módulos (cuando se use bundler)
// import './config.js';
// import './preview.js';
// import './chat.js';
// import './android-utils.js';

class KalinApp {
    constructor() {
        this.initialized = false;
        this.modules = {};
    }

    /**
     * Inicializar la aplicación
     */
    async initialize() {
        if (this.initialized) {
            console.warn('⚠️ KalinApp ya está inicializada');
            return;
        }

        console.log('🚀 Inicializando Kalin AI Frontend...');

        try {
            // Verificar configuración
            this.verifyConfig();

            // Inicializar módulos
            await this.initializeModules();

            // Configurar event listeners globales
            this.setupGlobalListeners();

            // Mostrar mensaje de bienvenida - DESACTIVADO
            // this.showWelcomeMessage();

            this.initialized = true;
            console.log('✅ Kalin AI Frontend listo');

        } catch (error) {
            console.error('❌ Error inicializando KalinApp:', error);
            this.showError('Error al iniciar la aplicación. Recarga la página.');
        }
    }

    /**
     * Verificar que la configuración esté disponible
     */
    verifyConfig() {
        if (!window.AppConfig) {
            throw new Error('AppConfig no está disponible. Verifica que config.js esté cargado.');
        }
        console.log('✅ Configuración verificada');
    }

    /**
     * Inicializar todos los módulos
     */
    async initializeModules() {
        console.log('📦 Inicializando módulos...');

        // UI Manager (debe inicializarse primero)
        if (window.UIManager) {
            window.UIManager.initialize();
            this.modules.ui = window.UIManager;
            console.log('✅ UI Manager inicializado');
        } else {
            console.warn('⚠️ UIManager no disponible');
        }

        // Preview Manager
        if (window.PreviewManager) {
            window.PreviewManager.initialize();
            this.modules.preview = window.PreviewManager;
            console.log('✅ Preview Manager inicializado');
        } else {
            console.warn('⚠️ PreviewManager no disponible');
        }

        // Chat Manager
        if (window.ChatManager) {
            window.ChatManager.initialize();
            this.modules.chat = window.ChatManager;
            console.log('✅ Chat Manager inicializado');
        } else {
            console.warn('⚠️ ChatManager no disponible');
        }

        // Android Utils
        if (window.AndroidUtils) {
            this.modules.android = window.AndroidUtils;
            console.log('✅ Android Utils cargado');
        } else {
            console.warn('⚠️ AndroidUtils no disponible');
        }

        // Resizable Panels
        if (window.ResizablePanels) {
            window.ResizablePanels.initialize();
            
            // Cargar tamaños guardados después de un pequeño delay
            setTimeout(() => {
                window.ResizablePanels.loadPanelSizes();
            }, 100);
            
            this.modules.resizable = window.ResizablePanels;
            console.log('✅ Resizable Panels inicializado');
        } else {
            console.warn('⚠️ ResizablePanels no disponible');
        }

        // Code Editor Manager
        if (window.CodeEditorManager) {
            window.CodeEditorManager.initialize();
            this.modules.codeEditor = window.CodeEditorManager;
            console.log('✅ Code Editor Manager inicializado');
        } else {
            console.warn('⚠️ CodeEditorManager no disponible');
        }

        // WebContainer Manager
        if (window.WebContainerManager) {
            // Inicializar WebContainer de forma asíncrona
            window.WebContainerManager.initialize().then(() => {
                this.modules.webcontainer = window.WebContainerManager;
                console.log('✅ WebContainer Manager inicializado');
            }).catch(error => {
                console.error('❌ Error inicializando WebContainer:', error);
            });
        } else {
            console.warn('⚠️ WebContainerManager no disponible');
        }

        // Universal Renderer
        if (window.UniversalRenderer) {
            window.UniversalRenderer.initialize();
            this.modules.renderer = window.UniversalRenderer;
            console.log('✅ Universal Renderer inicializado');
        } else {
            console.warn('⚠️ UniversalRenderer no disponible');
        }

        console.log(`✅ ${Object.keys(this.modules).length} módulos inicializados`);
    }

    /**
     * Configurar event listeners globales
     */
    setupGlobalListeners() {
        // Manejar errores globales
        window.addEventListener('error', (event) => {
            console.error('💥 Error global:', event.error);
        });

        // Manejar promesas rechazadas
        window.addEventListener('unhandledrejection', (event) => {
            console.error('💥 Promesa rechazada:', event.reason);
        });

        // Detectar cambios de tamaño de ventana para layout responsive
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });

        console.log('✅ Event listeners globales configurados');
    }

    /**
     * Manejar resize de ventana
     */
    handleResize() {
        const width = window.innerWidth;

        // Ajustes para pantallas pequeñas
        if (width < 1200) {
            console.log('📱 Pantalla pequeña detectada, ajustando layout...');
            // Aquí se pueden agregar ajustes específicos
        }
    }

    /**
     * Mostrar mensaje de bienvenida
     */
    showWelcomeMessage() {
        const welcomeMessage = `
🤖 ¡Bienvenido a Kalin AI!

Puedo ayudarte con:
• Generar código en múltiples lenguajes
• Crear componentes Android (Activity, Fragment, Adapter, etc.)
• Renderizar HTML/CSS/JS en vivo
• Validar y detectar errores en código

Ejemplos:
- "crea una Activity llamada LoginScreen"
- "genera una página HTML con un botón"
- "valida mi código Java"

¡Empieza a escribir! ✨
        `;

        if (window.ChatManager) {
            window.ChatManager.addMessage(welcomeMessage.trim(), 'assistant');
        }
    }

    /**
     * Mostrar error al usuario
     * @param {string} message - Mensaje de error
     */
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-banner';
        errorDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff4444;
            color: white;
            padding: 12px 20px;
            text-align: center;
            z-index: 9999;
            font-weight: 600;
        `;
        errorDiv.textContent = message;

        document.body.insertBefore(errorDiv, document.body.firstChild);

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    /**
     * Obtener estado de la aplicación
     * @returns {Object}
     */
    getStatus() {
        return {
            initialized: this.initialized,
            modules: Object.keys(this.modules),
            config: !!window.AppConfig,
            preview: !!window.PreviewManager,
            chat: !!window.ChatManager,
            android: !!window.AndroidUtils
        };
    }
}

// Crear instancia global
const kalinApp = new KalinApp();

// Auto-inicializar cuando el DOM esté listo
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            kalinApp.initialize();
        });
    } else {
        kalinApp.initialize();
    }
}

// Exportar para uso externo
if (typeof window !== 'undefined') {
    window.KalinApp = kalinApp;
}
