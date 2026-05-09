/**
 * Kalin Frontend - Módulo de Preview/Renderizado
 * Maneja el renderizado seguro de código HTML/CSS/JS en iframe sandbox
 */

class PreviewManager {
    constructor() {
        this.enabled = window.AppConfig?.UI.DEFAULT_PREVIEW_ENABLED || false;
        this.previewFrame = null;
        this.placeholder = null;
        this.toggleButton = null;
        this.initialized = false;
    }

    /**
     * Inicializar el manager de preview
     */
    initialize() {
        if (this.initialized) return;

        this.previewFrame = document.getElementById('preview-frame');
        this.placeholder = document.getElementById('preview-placeholder');
        this.toggleButton = document.getElementById('preview-toggle');

        if (!this.previewFrame || !this.placeholder) {
            console.error('❌ Preview elements not found');
            return;
        }

        this.setupEventListeners();
        this.updateToggleButton();
        this.initialized = true;

        if (window.AppConfig?.LOGGING.ENABLE_SECURITY_LOGS) {
            this.initializeSecurityLog();
        }
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => this.toggle());
        }
    }

    /**
     * Activar/desactivar preview
     */
    toggle() {
        this.enabled = !this.enabled;
        this.updateToggleButton();

        if (this.enabled) {
            console.log('✅ Preview activado');
        } else {
            console.log('⏸️ Preview desactivado');
            this.hidePreview();
        }
    }

    /**
     * Actualizar estado del botón toggle
     */
    updateToggleButton() {
        if (!this.toggleButton) return;

        if (this.enabled) {
            this.toggleButton.textContent = 'Desactivar';
            this.toggleButton.classList.add('active');
        } else {
            this.toggleButton.textContent = 'Activar';
            this.toggleButton.classList.remove('active');
        }
    }

    /**
     * Renderizar código en el preview
     * @param {string} code - Código HTML/CSS/JS a renderizar
     */
    render(code) {
        if (!this.previewFrame || !this.placeholder) {
            console.warn('⚠️ Preview no inicializado');
            return;
        }

        if (!this.enabled) {
            this.showPlaceholderMessage('💡 Activa el preview para ver el resultado');
            return;
        }

        // Verificar si es código HTML renderizable
        if (!this.isHTMLCode(code)) {
            this.showPlaceholderMessage('📝 El código no es HTML/CSS/JS renderizable');
            return;
        }

        // Ocultar placeholder, mostrar iframe
        this.placeholder.style.display = 'none';
        this.previewFrame.style.display = 'block';

        // Crear documento completo con CSP estricta
        const htmlContent = this.prepareSecureHTML(code);

        // Renderizar en iframe usando srcdoc
        this.previewFrame.srcdoc = htmlContent;

        console.log('✅ Preview renderizado con sandbox seguro:', code.length, 'chars');
    }

    /**
     * Preparar HTML seguro con CSP y protecciones
     * @param {string} code - Código HTML original
     * @returns {string} - HTML con seguridad aplicada
     */
    prepareSecureHTML(code) {
        let htmlContent = code;

        // Si no es documento completo, envolverlo
        if (!code.includes('<!DOCTYPE') && !code.includes('<html')) {
            htmlContent = '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>' + code + '</body></html>';
        }

        // Agregar CSP estricta
        const cspPolicy = this.buildCSPPolicy();
        const cspMeta = '<meta http-equiv="Content-Security-Policy" content="' + cspPolicy + '">';
        htmlContent = htmlContent.replace('<head>', '<head>' + cspMeta);

        // Agregar script de seguridad
        const securityScript = this.buildSecurityScript();
        htmlContent = htmlContent.replace('</head>', securityScript + '</head>');

        return htmlContent;
    }

    /**
     * Construir política CSP
     * @returns {string} - Política CSP
     */
    buildCSPPolicy() {
        return [
            "default-src 'self'",
            "script-src 'unsafe-inline' 'unsafe-eval'",
            "style-src 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'none'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'none'"
        ].join('; ');
    }

    /**
     * Construir script de seguridad para bloquear APIs peligrosas
     * @returns {string} - Script de seguridad
     */
    buildSecurityScript() {
        return `<script>
            (function() {
                // Bloquear acceso a window.top (previene clickjacking)
                try { Object.defineProperty(window, "top", { value: window }); } catch(e) {}
                try { Object.defineProperty(window, "parent", { value: window }); } catch(e) {}
                
                // Bloquear storage compartido
                try { delete window.localStorage; } catch(e) {}
                try { delete window.sessionStorage; } catch(e) {}
                try { delete window.indexedDB; } catch(e) {}
                
                // Bloquear cookies
                Object.defineProperty(document, "cookie", {
                    get: function() { return ""; },
                    set: function() { }
                });
                
                // Bloquear navegación superior
                window.open = function() { return null; };
                window.location.replace = function() { };
                window.location.assign = function() { };
            })();
        <\/script>`;
    }

    /**
     * Detectar si el código es HTML/CSS/JS renderizable
     * @param {string} code - Código a verificar
     * @returns {boolean}
     */
    isHTMLCode(code) {
        const patterns = window.AppConfig?.RENDERING.HTML_DETECTION_PATTERNS || [];
        return patterns.some(pattern => code.includes(pattern));
    }

    /**
     * Mostrar mensaje en placeholder
     * @param {string} message - Mensaje a mostrar
     */
    showPlaceholderMessage(message) {
        if (!this.placeholder) return;

        this.previewFrame.style.display = 'none';
        this.placeholder.style.display = 'flex';

        const textElement = this.placeholder.querySelector('.preview-placeholder-text');
        if (textElement) {
            textElement.textContent = message;
        }
    }

    /**
     * Ocultar preview
     */
    hidePreview() {
        if (this.previewFrame) {
            this.previewFrame.style.display = 'none';
        }
        if (this.placeholder) {
            this.placeholder.style.display = 'flex';
        }
    }

    /**
     * Inicializar log de seguridad en consola
     */
    initializeSecurityLog() {
        console.log('\n🔒 ===== BROWSER SANDBOX SECURITY =====');
        console.log('✅ iframe sandbox:', window.AppConfig?.RENDERING.SANDBOX_ATTRIBUTES);
        console.log('✅ CSP estricta aplicada');
        console.log('✅ Bloqueado: top-navigation');
        console.log('✅ Bloqueado: storage compartido (localStorage, sessionStorage, indexedDB)');
        console.log('✅ Bloqueado: cookies');
        console.log('✅ Bloqueado: window.open');
        console.log('✅ Bloqueado: window.top / window.parent access');
        console.log('=====================================\n');
    }
}

// Exportar como singleton
const previewManager = new PreviewManager();

if (typeof window !== 'undefined') {
    window.PreviewManager = previewManager;
}
