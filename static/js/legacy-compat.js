/**
 * Kalin Frontend - Script Legacy Compatibility
 * Este archivo mantiene compatibilidad con funciones legacy del index.html original
 * mientras se migra gradualmente a la arquitectura modular.
 */

console.log('========================================');
console.log('📜 legacy-compat.js CARGADO');
console.log('========================================');

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
 * Funciones globales para el menú lateral (Sidebar)
 * NOTA: Estas funciones AHORA están en ui-manager.js como wrappers globales
 * Las definiciones aquí están COMENTADAS para evitar conflictos
 */

// TODAS las funciones del sidebar ahora se definen en ui-manager.js
// Ver líneas 845-916 de ui-manager.js para los wrappers globales

/**
 * Toggle sidebar - COMENTADO (ahora en sidebar-functions.js)
 */
/*
function toggleSidebar() {
    console.log('🔘 toggleSidebar llamado');
    
    // Intentar usar UIManager si está disponible
    if (window.UIManager) {
        console.log('✅ Usando UIManager.toggleSidebar()');
        window.UIManager.toggleSidebar();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback directo');
        // Fallback directo si UIManager no está inicializado
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('overlay');
        
        if (sidebar) {
            sidebar.classList.toggle('open');
            console.log('✅ Sidebar toggled directamente');
            
            if (overlay) {
                if (sidebar.classList.contains('open')) {
                    overlay.classList.add('show');
                } else {
                    overlay.classList.remove('show');
                }
            }
        } else {
            console.error('❌ No se encontró el elemento .sidebar');
        }
    }
}
*/

/**
 * Exportar experiencia - COMENTADO (ahora definido en ui-manager.js)
 */
/*
async function exportExperience() {
    console.log('📦 exportExperience llamado');
    
    if (window.UIManager) {
        window.UIManager.exportExperience();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        // Fallback directo
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
            
            console.log('✅ Experiencia exportada (fallback)');
        } catch (error) {
            console.error('Error exportando experiencia:', error);
            alert('Error al exportar experiencia');
        }
    }
}
*/

/**
 * Importar experiencia - COMENTADO (ahora definido en ui-manager.js)
 */
/*
function importExperience() {
    console.log('📥 importExperience llamado');
    
    if (window.UIManager) {
        window.UIManager.importExperience();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        // Fallback directo
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
}
*/

/**
 * Verificar dependencias - COMENTADO (ahora definido en ui-manager.js)
 */
/*
async function checkDependencies() {
    console.log('🔍 checkDependencies llamado');
    
    if (window.UIManager) {
        window.UIManager.checkDependencies();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        try {
            const response = await fetch('/system/check-dependencies');
            const data = await response.json();
            
            if (data.status === 'success') {
                let message = '📊 **Reporte de Dependencias**\n\n';
                
                if (data.missing && data.missing.length > 0) {
                    message += '❌ **Faltantes:**\n';
                    data.missing.forEach(dep => {
                        message += `• ${dep}\n`;
                    });
                    message += '\n';
                }
                
                if (data.installed && data.installed.length > 0) {
                    message += '✅ **Instaladas:**\n';
                    data.installed.forEach(dep => {
                        message += `• ${dep}\n`;
                    });
                    message += '\n';
                }
                
                if (data.missing && data.missing.length > 0) {
                    message += '💡 Ejecuta "Instalar Dependencias" desde el menú para instalar las faltantes.';
                } else {
                    message += '✨ ¡Todas las dependencias están instaladas!';
                }

                alert(message);
            }
        } catch (error) {
            console.error('Error verificando dependencias:', error);
        }
    }
}
*/

/**
 * Instalar dependencias - COMENTADO (ahora definido en ui-manager.js)
 */
/*
async function installDependencies() {
    console.log('⚙️ installDependencies llamado');
    
    if (window.UIManager) {
        window.UIManager.installDependencies();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        alert('📦 Instalando dependencias... Esto puede tardar unos minutos.');
        
        try {
            const response = await fetch('/system/install-dependencies', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                alert('✅ Dependencias instaladas correctamente. Recarga la página.');
            } else {
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error instalando dependencias:', error);
            alert('❌ Error al instalar dependencias');
        }
    }
}
*/

/**
 * Crear entorno virtual - COMENTADO (ahora definido en ui-manager.js)
 */
/*
async function createVenv() {
    console.log('📦 createVenv llamado');
    
    if (window.UIManager) {
        window.UIManager.createVenv();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        alert('🔧 Creando entorno virtual...');

        try {
            const response = await fetch('/system/create-venv', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                alert('✅ Entorno virtual creado. Instala dependencias ahora.');
            } else {
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error creando venv:', error);
            alert('❌ Error al crear entorno virtual');
        }
    }
}
*/

/**
 * Descargar modelos - COMENTADO (ahora definido en ui-manager.js)
 */
/*
function downloadModels() {
    console.log('📥 downloadModels llamado');
    
    if (window.UIManager) {
        window.UIManager.downloadModels();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
        alert('ℹ️ Para descargar modelos, usa el menú lateral después de que la aplicación se inicialice completamente.');
    }
}
*/

/**
 * Seleccionar modelo activo - COMENTADO (ahora definido en ui-manager.js)
 */
/*
async function selectActiveModel() {
    console.log('🤖 selectActiveModel llamado');
    
    if (window.UIManager) {
        window.UIManager.selectActiveModel();
    } else {
        console.warn('⚠️ UIManager no disponible, usando fallback');
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
                        alert(`✅ Modelo cambiado a: ${modelName}`);
                    }
                }
            }
        } catch (error) {
            console.error('Error seleccionando modelo:', error);
        }
    }
}
*/

/**
 * Crear archivo .env
 */
function createEnvFile() {
    if (window.UIManager) {
        window.UIManager.createEnvFile();
    } else {
        console.error('❌ UIManager no disponible');
    }
}

/**
 * Ver/Editar archivo .env
 */
async function viewEnvFile() {
    try {
        // Obtener contenido actual del .env
        const response = await fetch('/system/read-env');
        const data = await response.json();
        
        if (data.status === 'error') {
            if (window.ChatManager) {
                window.ChatManager.addMessage(data.message, 'assistant');
            }
            return;
        }
        
        // Mostrar el contenido actual y permitir edición
        const newContent = prompt('Edita el archivo .env (copia y pega el contenido):', data.content);
        
        if (newContent !== null && newContent !== data.content) {
            // Usuario modificó el contenido
            const updateResponse = await fetch('/system/update-env', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: newContent })
            });
            
            const updateData = await updateResponse.json();
            
            if (updateData.status === 'success') {
                if (window.ChatManager) {
                    window.ChatManager.addMessage(updateData.message, 'assistant');
                }
            } else {
                if (window.ChatManager) {
                    window.ChatManager.addMessage(updateData.message, 'assistant');
                }
            }
        }
    } catch (error) {
        console.error('Error al ver/editar .env:', error);
        if (window.ChatManager) {
            window.ChatManager.addMessage('❌ Error al acceder al archivo .env', 'assistant');
        }
    }
}

/**
 * Instalación rápida
 */
function quickInstall() {
    if (window.ChatManager) {
        window.ChatManager.addMessage('🚀 Iniciando instalación automática...', 'assistant');
        
        // Ejecutar pasos en secuencia
        setTimeout(() => createVenv(), 1000);
        setTimeout(() => installDependencies(), 3000);
        setTimeout(() => downloadModels(), 5000);
    }
}

/**
 * Toggle auto-dependencias
 */
function toggleAutoDependencies() {
    const toggle = document.getElementById('auto-deps-toggle');
    if (toggle) {
        const enabled = toggle.checked;
        console.log('Auto-dependencias:', enabled ? 'activado' : 'desactivado');
        
        // Guardar preferencia en localStorage
        localStorage.setItem('auto_dependencies', enabled);
        
        if (window.ChatManager) {
            window.ChatManager.addMessage(
                enabled ? '✅ Detección automática de dependencias activada' : '⏸️ Detección automática desactivada',
                'assistant'
            );
        }
    }
}

/**
 * Verificar dependencias pendientes
 */
function checkPendingDependencies() {
    if (window.ChatManager) {
        window.ChatManager.addMessage('🔍 Verificando dependencias pendientes...', 'assistant');
        // Aquí se puede implementar la lógica específica
    }
}

/**
 * Instalar dependencias pendientes
 */
function installPendingDependencies() {
    if (window.UIManager) {
        window.UIManager.installDependencies();
    }
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
    
    // Cargar preferencia de auto-dependencias
    const autoDepsToggle = document.getElementById('auto-deps-toggle');
    if (autoDepsToggle) {
        const saved = localStorage.getItem('auto_dependencies');
        if (saved !== null) {
            autoDepsToggle.checked = saved === 'true';
        }
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
