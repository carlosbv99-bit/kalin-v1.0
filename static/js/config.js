/**
 * Kalin Frontend - Módulo de Configuración
 * Centraliza todas las configuraciones del frontend para fácil mantenimiento
 */

const AppConfig = {
    // URLs y endpoints
    API: {
        BASE_URL: '',
        SEND_MESSAGE: '/chat',  // Endpoint correcto del backend
        GET_CODE: '/get_code',
        HEALTH: '/health'
    },

    // Configuración de UI
    UI: {
        DEFAULT_PREVIEW_ENABLED: false,
        CODE_PANEL_WIDTH_PERCENT: 50,
        PREVIEW_PANEL_WIDTH_PERCENT: 25,
        CHAT_PANEL_WIDTH_PERCENT: 25,
        MAX_CHAT_MESSAGES: 100,
        AUTO_SCROLL_THRESHOLD: 100 // px desde el bottom
    },

    // Configuración de renderizado
    RENDERING: {
        HTML_DETECTION_PATTERNS: [
            '<html', '<!doctype', '<div', '<body', '<script', '<style'
        ],
        PREVIEW_RENDER_DELAY: 500, // ms
        SANDBOX_ATTRIBUTES: 'allow-scripts allow-same-origin'
    },

    // Tipos de componentes Android soportados
    ANDROID_COMPONENTS: {
        ACTIVITY: 'activity',
        FRAGMENT: 'fragment',
        ADAPTER: 'adapter',
        CUSTOM_VIEW: 'custom_view',
        SERVICE: 'service',
        BROADCAST_RECEIVER: 'broadcast_receiver'
    },

    // Lenguajes soportados
    LANGUAGES: {
        JAVA: 'java',
        KOTLIN: 'kotlin',
        PYTHON: 'python',
        JAVASCRIPT: 'javascript',
        TYPESCRIPT: 'typescript',
        HTML: 'html',
        CSS: 'css',
        XML: 'xml'
    },

    // Configuración de logs
    LOGGING: {
        ENABLE_CONSOLE_LOGS: true,
        ENABLE_SECURITY_LOGS: true,
        LOG_LEVEL: 'info' // 'debug', 'info', 'warn', 'error'
    }
};

// Hacer disponible globalmente
if (typeof window !== 'undefined') {
    window.AppConfig = AppConfig;
}
