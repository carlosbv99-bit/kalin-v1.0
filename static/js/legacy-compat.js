/**
 * Kalin Frontend - Script Legacy Compatibility
 * Este archivo mantiene compatibilidad con funciones legacy del index.html original
 * mientras se migra gradualmente a la arquitectura modular.
 */

// Variables globales legacy
let previewEnabled = false;
let lastGeneratedCode = '';

/**
 * Función togglePreview legacy (redirige a PreviewManager)
 */
function togglePreview() {
    console.log('🔘 Legacy togglePreview called');
    
    if (window.PreviewManager) {
        console.log('✅ PreviewManager found, calling toggle');
        window.PreviewManager.toggle();
        previewEnabled = window.PreviewManager.enabled;
        console.log('✅ Preview state changed to:', previewEnabled);
    } else {
        console.error('❌ PreviewManager no disponible');
        alert('Error: PreviewManager no está inicializado');
    }
}

/**
 * Función renderInPreview legacy (redirige a PreviewManager)
 */
function renderInPreview(code) {
    if (window.PreviewManager) {
        window.PreviewManager.render(code);
        lastGeneratedCode = code;
    } else {
        console.warn('⚠️ PreviewManager no disponible');
    }
}

/**
 * Función isHTMLCode legacy (redirige a PreviewManager)
 */
function isHTMLCode(code) {
    if (window.PreviewManager) {
        return window.PreviewManager.isHTMLCode(code);
    }
    
    // Fallback si PreviewManager no está disponible
    const patterns = [
        '<html', '<!doctype', '<div', '<body', '<script', '<style'
    ];
    return patterns.some(pattern => code.includes(pattern));
}

/**
 * Función displayCodeInMainArea legacy (redirige a ChatManager)
 */
function displayCodeInMainArea(text) {
    if (window.ChatManager) {
        const code = extractCodeFromText(text);
        if (code) {
            window.ChatManager.displayCodeInMainArea(code);
            
            // Auto-renderizar si es HTML y preview está activo
            if (previewEnabled && isHTMLCode(code)) {
                setTimeout(() => {
                    renderInPreview(code);
                }, 500);
            }
        }
    } else {
        console.warn('⚠️ ChatManager no disponible');
    }
}

/**
 * Extraer código de texto
 */
function extractCodeFromText(text) {
    const regex = /```(\w+)?\n([\s\S]*?)```/g;
    const match = regex.exec(text);
    return match ? match[2] : text;
}

/**
 * Inicialización legacy
 */
function initializeLegacy() {
    console.log('🔄 Inicializando compatibilidad legacy...');
    
    // Sincronizar estado
    if (window.PreviewManager) {
        previewEnabled = window.PreviewManager.enabled;
    }
    
    // Agregar comando para resetear paneles (accesible desde consola)
    window.resetPanelSizes = function() {
        if (window.ResizablePanels) {
            window.ResizablePanels.resetToDefault();
            return '✅ Tamaños de paneles reseteados';
        }
        return '⚠️ ResizablePanels no disponible';
    };
    
    // Agregar comando para ver estado de paneles
    window.getPanelStatus = function() {
        if (window.ResizablePanels) {
            return window.ResizablePanels.getStatus();
        }
        return '⚠️ ResizablePanels no disponible';
    };
    
    console.log('✅ Compatibilidad legacy lista');
    console.log('💡 Comandos disponibles: resetPanelSizes(), getPanelStatus()');
}

// Ejecutar cuando los módulos estén listos
if (typeof window !== 'undefined') {
    setTimeout(() => {
        initializeLegacy();
    }, 100);
}

console.log('✅ Legacy compatibility layer loaded');
