/**
 * Kalin - Funciones de Menús y Navegación
 */

// Variable global para session_id
window.currentSessionId = 'default';

console.log('📋 menu-functions.js cargado correctamente');
console.log('✅ Funciones registradas:', {
    showModelSelectorMenu: typeof showModelSelectorMenu,
    activateLocalModel: typeof activateLocalModel,
    closeAllMenus: typeof closeAllMenus,
    toggleTerminal: typeof toggleTerminal,
    showViewMenu: typeof showViewMenu,
    showToolsMenu: typeof showToolsMenu,
    undoLastChange: typeof undoLastChange,
    showDiffViewer: typeof showDiffViewer
});

// Sobrescribir alert, prompt y confirm para modo oscuro
(function() {
    const originalAlert = window.alert;
    const originalPrompt = window.prompt;
    const originalConfirm = window.confirm;
    
    window.alert = function(message) {
        document.body.classList.add('dialog-active');
        setTimeout(() => {
            document.body.classList.remove('dialog-active');
        }, 100);
        return originalAlert(message);
    };
    
    window.prompt = function(message, defaultValue) {
        document.body.classList.add('dialog-active');
        const result = originalPrompt(message, defaultValue);
        setTimeout(() => {
            document.body.classList.remove('dialog-active');
        }, 100);
        return result;
    };
    
    window.confirm = function(message) {
        document.body.classList.add('dialog-active');
        const result = originalConfirm(message);
        setTimeout(() => {
            document.body.classList.remove('dialog-active');
        }, 100);
        return result;
    };
})();

function closeAllMenus() {
    const submenus = document.querySelectorAll('.dropdown-submenu');
    submenus.forEach(menu => {
        if (menu.id !== 'submenu-model-selector') {
            menu.style.display = 'none';
        }
    });
}

function showFileMenu() {
    const menu = document.getElementById('menu-file');
    if (menu) {
        const button = document.querySelector('[data-menu="file"]');
        const rect = button.getBoundingClientRect();
        menu.style.top = rect.bottom + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.display = 'block';
    }
}

function hideFileMenu() {
    setTimeout(() => {
        const menu = document.getElementById('menu-file');
        if (menu && !menu.matches(':hover')) {
            menu.style.display = 'none';
        }
    }, 100);
}

function showViewMenu() {
    const menu = document.getElementById('menu-view');
    if (menu) {
        const button = document.querySelector('[data-menu="view"]');
        const rect = button.getBoundingClientRect();
        menu.style.top = rect.bottom + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.display = 'block';
    }
}

function hideViewMenu() {
    setTimeout(() => {
        const menu = document.getElementById('menu-view');
        if (menu && !menu.matches(':hover')) {
            menu.style.display = 'none';
        }
    }, 100);
}

function showToolsMenu() {
    const menu = document.getElementById('menu-tools');
    if (menu) {
        const button = document.querySelector('[data-menu="tools"]');
        const rect = button.getBoundingClientRect();
        menu.style.top = rect.bottom + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.display = 'block';
    }
}

function hideToolsMenu() {
    setTimeout(() => {
        const menu = document.getElementById('menu-tools');
        if (menu && !menu.matches(':hover')) {
            menu.style.display = 'none';
        }
    }, 100);
}

// Estado del terminal
let terminalVisible = false;

function toggleTerminal() {
    console.log('🔍 toggleTerminal llamado');
    const terminalPanel = document.getElementById('terminal-panel');
    const codeEditorContainer = document.getElementById('code-editor-container');
    const codePlaceholder = document.getElementById('code-placeholder');
    
    console.log('terminalPanel:', terminalPanel);
    console.log('codeEditorContainer:', codeEditorContainer);
    console.log('codeEditorContainer.style.display:', codeEditorContainer ? codeEditorContainer.style.display : 'N/A');
    
    if (!terminalPanel) {
        console.error('❌ Panel de terminal no encontrado');
        alert('Error: Panel de terminal no encontrado');
        return;
    }
    
    // Si el editor no está visible, mostrarlo primero
    if (codeEditorContainer) {
        const computedStyle = window.getComputedStyle(codeEditorContainer);
        console.log('Computed display:', computedStyle.display);
        
        if (computedStyle.display === 'none' || codeEditorContainer.style.display === 'none') {
            console.log('Mostrando editor de código...');
            codeEditorContainer.style.display = 'flex';
            if (codePlaceholder) codePlaceholder.style.display = 'none';
        }
    }
    
    terminalVisible = !terminalVisible;
    
    if (terminalVisible) {
        terminalPanel.style.display = 'flex';
        console.log('✅ Terminal mostrado - display:', terminalPanel.style.display);
        console.log('Terminal computed style:', window.getComputedStyle(terminalPanel).display);
        console.log('Terminal offsetHeight:', terminalPanel.offsetHeight);
        
        // Hacer scroll para mostrar el terminal
        setTimeout(() => {
            terminalPanel.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
        
        // Enfocar el input del terminal
        setTimeout(() => {
            const terminalInput = document.getElementById('terminal-input');
            if (terminalInput) terminalInput.focus();
        }, 200);
    } else {
        terminalPanel.style.display = 'none';
        console.log('✅ Terminal ocultado');
    }
}

function handleTerminalKeyPress(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('terminal-input');
        const output = document.getElementById('terminal-output');
        
        if (!input || !output) return;
        
        const command = input.value.trim();
        if (!command) return;
        
        // Mostrar comando en el output
        output.innerHTML += `<div style="color: #4ec9b0;">$ ${escapeHtml(command)}</div>`;
        
        // Ejecutar comando (simulado por ahora)
        executeTerminalCommand(command, output);
        
        // Limpiar input
        input.value = '';
        
        // Scroll al final
        output.scrollTop = output.scrollHeight;
    }
}

function executeTerminalCommand(command, output) {
    // Simulación de comandos básicos
    const commands = {
        'help': 'Comandos disponibles: help, clear, echo, date, whoami',
        'clear': () => { output.innerHTML = ''; return ''; },
        'date': new Date().toString(),
        'whoami': 'usuario@kalin',
    };
    
    let response = '';
    
    if (command.startsWith('echo ')) {
        response = command.substring(5);
    } else if (commands[command]) {
        response = typeof commands[command] === 'function' ? commands[command]() : commands[command];
    } else {
        response = `Comando no reconocido: ${command}. Escribe 'help' para ver los comandos disponibles.`;
    }
    
    if (response) {
        output.innerHTML += `<div style="color: #d4d4d4; margin-bottom: 8px;">${escapeHtml(response)}</div>`;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showCreateProjectSubmenu(event) {
    event.stopPropagation();
    const submenu = document.getElementById('submenu-create-project');
    if (submenu) {
        const rect = event.target.getBoundingClientRect();
        submenu.style.top = rect.top + 'px';
        submenu.style.left = (rect.right - 5) + 'px';
        submenu.style.display = 'block';
    }
}

function hideCreateProjectSubmenu(event) {
    setTimeout(() => {
        const submenu = document.getElementById('submenu-create-project');
        if (submenu && !submenu.matches(':hover')) {
            submenu.style.display = 'none';
        }
    }, 100);
}

function showPreferencesSubmenu(event) {
    event.stopPropagation();
    const submenu = document.getElementById('submenu-preferences');
    if (submenu) {
        const rect = event.target.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const submenuHeight = 500;
        
        let top = rect.top;
        if (rect.top + submenuHeight > viewportHeight) {
            top = Math.max(10, viewportHeight - submenuHeight - 10);
        }
        
        submenu.style.top = top + 'px';
        submenu.style.left = (rect.right + 5) + 'px';
        submenu.style.display = 'block';
    }
}

function hidePreferencesSubmenu(event) {
    setTimeout(() => {
        const submenu = document.getElementById('submenu-preferences');
        if (submenu && !submenu.matches(':hover')) {
            submenu.style.display = 'none';
        }
    }, 100);
}

function showModelSelectorMenu(event) {
    console.log('🔍 showModelSelectorMenu llamado', event);
    event.stopPropagation();
    const submenu = document.getElementById('submenu-model-selector');
    console.log('Submenú encontrado:', submenu);
    if (submenu) {
        const rect = event.target.getBoundingClientRect();
        submenu.style.top = rect.bottom + 'px';
        submenu.style.left = rect.left + 'px';
        submenu.style.display = 'block';
        console.log('Submenú mostrado');
        loadInstalledModelsToMainSubmenu();
    } else {
        console.error('❌ Submenú no encontrado');
    }
}

function hideModelSelectorMenu(event) {
    setTimeout(() => {
        const submenu = document.getElementById('submenu-model-selector');
        if (submenu && !submenu.matches(':hover')) {
            submenu.style.display = 'none';
        }
    }, 100);
}

function loadInstalledModelsToMainSubmenu() {
    const submenu = document.getElementById('submenu-model-selector');
    if (!submenu) return;
    
    submenu.innerHTML = '<div style="padding: 12px; text-align: center; color: #666;">Cargando modelos...</div>';
    
    fetch('/system/list-models')
    .then(response => {
        console.log('Respuesta del servidor:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Datos recibidos:', data);
        
        // Manejar diferentes formatos de respuesta
        let models = [];
        let providersConfigured = {};
        
        if (data.models && Array.isArray(data.models)) {
            models = data.models;
            providersConfigured = data.providers_configured || {};
        } else if (Array.isArray(data)) {
            models = data;
        }
        
        // Filtrar solo modelos con API Key configurada o modelos locales instalados
        let availableModels = [];
        
        models.forEach(model => {
            const modelName = typeof model === 'string' ? model : (model.name || model.id || JSON.stringify(model));
            
            // Verificar si es modelo local (Ollama)
            if (modelName.includes('(Local)')) {
                // Modelos locales siempre están disponibles si Ollama está instalado
                availableModels.push(modelName);
            }
            // Verificar si es modelo en la nube - VERIFICACIÓN DINÁMICA
            else if (modelName.includes('(Nube')) {
                // Extraer el nombre del proveedor del formato "(Nube - ProviderName)"
                const match = modelName.match(/\(Nube - (.+?)\)/);
                if (match) {
                    const providerName = match[1].toLowerCase();
                    
                    // Verificar en providers_configured (backend)
                    if (providersConfigured[providerName]) {
                        availableModels.push(modelName);
                    }
                    // Fallback: verificar localStorage
                    else {
                        const apiKey = localStorage.getItem(`${providerName}_api_key`);
                        if (apiKey) {
                            availableModels.push(modelName);
                        }
                    }
                }
            }
        });
        
        if (availableModels.length > 0) {
            let html = '';
            availableModels.forEach(model => {
                const modelName = typeof model === 'string' ? model : (model.name || model.id || JSON.stringify(model));
                
                // Determinar icono según el tipo - DINÁMICO
                let icon = '🦙';
                if (modelName.includes('OpenAI')) icon = '🔵';
                else if (modelName.includes('Anthropic')) icon = '🟣';
                else if (modelName.includes('Groq') || modelName.includes('Grok')) icon = '⚡';
                else if (modelName.includes('Gemini')) icon = '🌟';
                else if (modelName.includes('Mistral')) icon = '🎯';
                else if (modelName.includes('MiMo')) icon = '🚀';
                else if (modelName.includes('Azure')) icon = '☁️';
                else if (modelName.includes('HuggingFace')) icon = '🤗';
                
                html += `<div class="dropdown-item" onclick="activateLocalModel('${modelName}')"><span>${icon} ${modelName}</span></div>`;
            });
            submenu.innerHTML = html;
        } else {
            submenu.innerHTML = `
                <div style="padding: 12px; text-align: center; color: #666;">
                    No hay modelos disponibles<br>
                    <small>Configura una API Key o instala modelos Ollama</small>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error al cargar modelos:', error);
        submenu.innerHTML = `
            <div style="padding: 12px; text-align: center; color: #ff4444;">
                Error al cargar modelos<br>
                <small style="color: #999;">${error.message}</small><br>
                <button onclick="loadInstalledModelsToMainSubmenu()" style="margin-top: 8px; padding: 4px 12px; background: #0066ff; color: white; border: none; border-radius: 4px; cursor: pointer;">Reintentar</button>
            </div>
        `;
    });
}

function updateModelIndicator() {
    const indicator = document.getElementById('active-model-indicator');
    if (!indicator) return;
    
    fetch('/system/current-model')
    .then(response => response.json())
    .then(data => {
        console.log('Modelo actual:', data);
        
        let modelName = '';
        let provider = 'ollama';
        
        if (data.model) {
            // Formato: "llama3.2 (Local)" o "Grok (llama-3.1-8b-instant)"
            const fullModel = data.model;
            modelName = fullModel.split(' (')[0].trim();
            
            // Detectar proveedor - DINÁMICO
            if (fullModel.includes('Nube')) {
                const match = fullModel.match(/\(Nube - (.+?)\)/);
                if (match) {
                    provider = match[1].toLowerCase();
                }
            }
        } else if (data.current_model) {
            modelName = data.current_model.split(' (')[0].trim();
        }
        
        if (modelName) {
            let icon = '🤖';
            
            if (provider === 'ollama') icon = '🦙';
            else if (provider === 'openai') icon = '🔵';
            else if (provider === 'anthropic') icon = '🟣';
            else if (provider === 'groq') icon = '⚡';
            else if (provider === 'gemini') icon = '🌟';
            else if (provider === 'mistral') icon = '🎯';
            else if (provider === 'mimo') icon = '🚀';
            
            indicator.innerHTML = `${icon} ${modelName} <span style="font-size: 10px;">▼</span>`;
        }
    })
    .catch(error => {
        console.error('Error al actualizar indicador:', error);
        const lastModel = localStorage.getItem('last_active_model');
        if (lastModel) {
            indicator.innerHTML = `🤖 ${lastModel} <span style="font-size: 10px;">▼</span>`;
        }
    });
}

function activateLocalModel(modelName) {
    closeAllMenus();
    
    // Limpiar el nombre del modelo (quitar etiquetas como "(Local)")
    const cleanModelName = modelName.split(' (')[0].trim();
    
    const indicator = document.getElementById('active-model-indicator');
    if (indicator) {
        indicator.innerHTML = `🦙 ${cleanModelName} <span style="font-size: 10px;">▼</span>`;
    }
    
    localStorage.setItem('last_active_model', cleanModelName);
    
    // Determinar si es modelo local o cloud - DINÁMICO
    const isCloud = modelName.includes('(Nube');
    let provider = 'ollama';
    
    if (modelName.includes('OpenAI')) provider = 'openai';
    else if (modelName.includes('Anthropic')) provider = 'anthropic';
    else if (modelName.includes('Groq') || modelName.includes('Grok')) provider = 'groq';
    else if (modelName.includes('Gemini')) provider = 'gemini';
    else if (modelName.includes('Mistral')) provider = 'mistral';
    else if (modelName.includes('MiMo')) provider = 'mimo';
    
    // Obtener API Key si es modelo cloud
    const apiKey = isCloud ? localStorage.getItem(`${provider}_api_key`) : null;
    
    fetch('/system/set-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            model: modelName, 
            provider: provider,
            api_key: apiKey
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`✅ Modelo ${cleanModelName} activado`);
            updateModelIndicator();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/**
 * Mostrar submenú de descarga de modelos
 */
function showDownloadModelsSubmenu(event) {
    event.stopPropagation();
    const submenu = document.getElementById('submenu-download-models');
    if (submenu) {
        const preferencesSubmenu = document.getElementById('submenu-preferences');
        if (preferencesSubmenu && preferencesSubmenu.style.display === 'block') {
            const prefRect = preferencesSubmenu.getBoundingClientRect();
            submenu.style.top = prefRect.top + 'px';
            submenu.style.left = (prefRect.right - 5) + 'px';
        } else {
            const rect = event.target.getBoundingClientRect();
            submenu.style.top = rect.top + 'px';
            submenu.style.left = (rect.right - 5) + 'px';
        }
        submenu.style.display = 'block';
        
        // Cargar modelos de Ollama dinámicamente
        if (typeof loadOllamaModelsList === 'function') {
            loadOllamaModelsList();
        }
    }
}

/**
 * Ocultar submenú de descarga de modelos
 */
function hideDownloadModelsSubmenu(event) {
    setTimeout(() => {
        const submenu = document.getElementById('submenu-download-models');
        if (submenu && !submenu.matches(':hover')) {
            submenu.style.display = 'none';
        }
    }, 100);
}

/**
 * Descargar modelo local (Ollama)
 */
function downloadLocalModel(modelName) {
    closeAllMenus();
    
    // Mostrar indicador de progreso
    if (typeof showModelDownloadIndicator === 'function') {
        showModelDownloadIndicator(modelName);
    }
    
    fetch('/system/check-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.installed) {
            // Modelo ya instalado - preguntar si activar
            showConfirmModal(
                `El modelo ${modelName} ya está instalado.\n\n¿Deseas activarlo como modelo activo?`,
                () => activateLocalModel(modelName)
            );
        } else {
            // Modelo no instalado - preguntar si descargar
            showConfirmModal(
                `El modelo ${modelName} no está instalado.\n\n¿Deseas descargarlo e instalarlo?\n\nEsto puede tardar varios minutos.`,
                () => {
                    fetch('/system/download-model', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model: modelName })
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Ocultar indicador de progreso
                        if (typeof hideModelDownloadIndicator === 'function') {
                            hideModelDownloadIndicator();
                        }
                        
                        if (data.status === 'success') {
                            showAlertModal(
                                `Modelo ${modelName} descargado correctamente.\n\n¿Deseas activarlo ahora?`,
                                'success'
                            );
                            // Agregar botones de acción al modal
                            setTimeout(() => {
                                const overlay = document.querySelector('div[style*="z-index: 10000"]');
                                if (overlay) {
                                    const modal = overlay.querySelector('div');
                                    const buttonContainer = modal.querySelector('div:last-child');
                                    
                                    // Botón Sí
                                    const yesBtn = document.createElement('button');
                                    yesBtn.textContent = 'Sí, activar';
                                    yesBtn.style.padding = '10px 20px';
                                    yesBtn.style.border = 'none';
                                    yesBtn.style.background = '#28a745';
                                    yesBtn.style.color = '#ffffff';
                                    yesBtn.style.borderRadius = '6px';
                                    yesBtn.style.cursor = 'pointer';
                                    yesBtn.style.fontSize = '14px';
                                    yesBtn.style.marginLeft = '8px';
                                    yesBtn.onclick = () => {
                                        document.body.removeChild(overlay);
                                        activateLocalModel(modelName);
                                    };
                                    
                                    // Botón No
                                    const noBtn = document.createElement('button');
                                    noBtn.textContent = 'No, más tarde';
                                    noBtn.style.padding = '10px 20px';
                                    noBtn.style.border = '1px solid #555';
                                    noBtn.style.background = '#2d2d2d';
                                    noBtn.style.color = '#ffffff';
                                    noBtn.style.borderRadius = '6px';
                                    noBtn.style.cursor = 'pointer';
                                    noBtn.style.fontSize = '14px';
                                    noBtn.onclick = () => {
                                        document.body.removeChild(overlay);
                                    };
                                    
                                    buttonContainer.insertBefore(yesBtn, buttonContainer.firstChild);
                                    buttonContainer.insertBefore(noBtn, buttonContainer.firstChild);
                                }
                            }, 100);
                        } else {
                            showAlertModal(`Error al descargar modelo: ${data.message}`, 'error');
                        }
                    })
                    .catch(error => {
                        // Ocultar indicador de progreso
                        if (typeof hideModelDownloadIndicator === 'function') {
                            hideModelDownloadIndicator();
                        }
                        
                        console.error('Error al descargar modelo:', error);
                        showAlertModal('Error de conexión al descargar modelo', 'error');
                    });
                }
            );
        }
    })
    .catch(error => {
        // Ocultar indicador de progreso
        if (typeof hideModelDownloadIndicator === 'function') {
            hideModelDownloadIndicator();
        }
        
        console.error('Error al verificar modelo:', error);
        showConfirmModal(
            `No se pudo verificar el estado del modelo ${modelName}.\n\n¿Deseas intentar descargarlo de todas formas?`,
            () => {
                fetch('/system/download-model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: modelName })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showAlertModal(`Modelo ${modelName} descargado correctamente`, 'success');
                    } else {
                        showAlertModal(`Error: ${data.message}`, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlertModal('Error de conexión', 'error');
                });
            }
        );
    });
}

/**
 * Mostrar submenú de proveedor cloud
 */
function showCloudProviderSubmenu(event, provider) {
    event.stopPropagation();
    
    let submenuId;
    if (event.target.closest('#submenu-download-models')) {
        submenuId = `submenu-download-${provider}-models`;
    } else {
        submenuId = `submenu-${provider}-models`;
    }
    
    const submenu = document.getElementById(submenuId);
    if (submenu) {
        ['openai', 'anthropic', 'groq', 'gemini', 'mistral'].forEach(p => {
            if (p !== provider) {
                const otherSubmenu1 = document.getElementById(`submenu-${p}-models`);
                const otherSubmenu2 = document.getElementById(`submenu-download-${p}-models`);
                if (otherSubmenu1) otherSubmenu1.style.display = 'none';
                if (otherSubmenu2) otherSubmenu2.style.display = 'none';
            }
        });
        
        const rect = event.target.getBoundingClientRect();
        submenu.style.top = rect.top + 'px';
        submenu.style.left = (rect.right - 5) + 'px';
        submenu.style.display = 'block';
    }
}

/**
 * Ocultar submenú de proveedor cloud
 */
let cloudSubmenuTimeout = null;

function hideCloudProviderSubmenu(event) {
    if (cloudSubmenuTimeout) {
        clearTimeout(cloudSubmenuTimeout);
    }
    
    cloudSubmenuTimeout = setTimeout(() => {
        let anyHovered = false;
        ['openai', 'anthropic', 'groq', 'gemini', 'mistral'].forEach(provider => {
            const submenu1 = document.getElementById(`submenu-${provider}-models`);
            const submenu2 = document.getElementById(`submenu-download-${provider}-models`);
            const parentItem1 = submenu1 ? submenu1.parentElement : null;
            const parentItem2 = submenu2 ? submenu2.parentElement : null;
            
            if ((submenu1 && submenu1.matches(':hover')) || 
                (submenu2 && submenu2.matches(':hover')) ||
                (parentItem1 && parentItem1.matches(':hover')) ||
                (parentItem2 && parentItem2.matches(':hover'))) {
                anyHovered = true;
            }
        });
        
        if (!anyHovered) {
            ['openai', 'anthropic', 'groq', 'gemini', 'mistral'].forEach(provider => {
                const submenu1 = document.getElementById(`submenu-${provider}-models`);
                const submenu2 = document.getElementById(`submenu-download-${provider}-models`);
                if (submenu1) submenu1.style.display = 'none';
                if (submenu2) submenu2.style.display = 'none';
            });
        }
    }, 300);
}

/**
 * Mantener submenú de proveedor cloud abierto
 */
function keepCloudProviderSubmenuOpen(provider) {
    let submenu;
    if (provider.startsWith('download-')) {
        const baseProvider = provider.replace('download-', '');
        submenu = document.getElementById(`submenu-download-${baseProvider}-models`);
    } else {
        submenu = document.getElementById(`submenu-${provider}-models`);
    }
    
    if (submenu) {
        submenu.style.display = 'block';
    }
}

/**
 * Activar modelo en la nube con verificación de API Key
 */
function activateCloudModel(provider, modelName) {
    console.log('🔍 activateCloudModel llamado con:', provider, modelName);
    closeAllMenus();
    
    const providerNames = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'groq': 'Groq',
        'gemini': 'Google Gemini',
        'mistral': 'Mistral AI',
        'mimo': 'Xiaomi MiMo'
    };
    
    const savedApiKey = localStorage.getItem(`${provider}_api_key`);
    console.log('💾 API Key guardada en localStorage:', savedApiKey ? 'SÍ' : 'NO');
    
    if (savedApiKey) {
        const useSaved = confirm(`API Key de ${providerNames[provider]} encontrada.\n\n¿Deseas usarla para activar ${modelName}?\n\n(Aceptar: Usar guardada / Cancelar: Ingresar nueva)`);
        
        if (useSaved) {
            setCloudModel(provider, modelName, savedApiKey);
            return;
        }
    }
    
    // Mostrar modal personalizado para ingresar API Key
    showApiKeyModal(provider, modelName, function(apiKey) {
        console.log('✅ API Key ingresada:', apiKey ? 'SÍ' : 'NO');
        localStorage.setItem(`${provider}_api_key`, apiKey);
        setCloudModel(provider, modelName, apiKey);
    });
}

/**
 * Configurar y activar modelo en la nube
 */
function setCloudModel(provider, modelName, apiKey) {
    console.log('🚀 setCloudModel llamado con:', { provider, modelName, apiKey: apiKey ? 'SÍ (' + apiKey.length + ' chars)' : 'NO' });
    
    const providerNames = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'groq': 'Groq',
        'gemini': 'Google Gemini',
        'mistral': 'Mistral AI',
        'mimo': 'MiMo'
    };
    
    // Construir el nombre completo con etiqueta de nube
    const fullModelName = `${modelName} (Nube - ${providerNames[provider]})`;
    console.log('📤 Enviando al servidor:', fullModelName);
    console.log('📤 Datos completos:', { model: fullModelName, provider: provider, api_key: apiKey ? '[HIDDEN]' : null });
    
    fetch('/system/set-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            model: fullModelName,
            provider: provider,
            api_key: apiKey
        })
    })
    .then(response => {
        console.log('📥 Respuesta HTTP status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📥 Respuesta del servidor:', data);
        if (data.status === 'success') {
            alert(`✅ Modelo activado: ${modelName} (${providerNames[provider]})`);
            updateModelIndicator();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('❌ Error al cambiar modelo:', error);
        alert('❌ Error de conexión al cambiar modelo');
    });
}

// Registrar globalmente
window.closeAllMenus = closeAllMenus;
window.showFileMenu = showFileMenu;
window.hideFileMenu = hideFileMenu;
window.showCreateProjectSubmenu = showCreateProjectSubmenu;
window.hideCreateProjectSubmenu = hideCreateProjectSubmenu;
window.showPreferencesSubmenu = showPreferencesSubmenu;
window.hidePreferencesSubmenu = hidePreferencesSubmenu;
window.showModelSelectorMenu = showModelSelectorMenu;
window.hideModelSelectorMenu = hideModelSelectorMenu;
window.loadInstalledModelsToMainSubmenu = loadInstalledModelsToMainSubmenu;
window.updateModelIndicator = updateModelIndicator;
window.activateLocalModel = activateLocalModel;
window.showDownloadModelsSubmenu = showDownloadModelsSubmenu;
window.hideDownloadModelsSubmenu = hideDownloadModelsSubmenu;
window.downloadLocalModel = downloadLocalModel;
window.showCloudProviderSubmenu = showCloudProviderSubmenu;
window.hideCloudProviderSubmenu = hideCloudProviderSubmenu;
window.keepCloudProviderSubmenuOpen = keepCloudProviderSubmenuOpen;
window.activateCloudModel = activateCloudModel;
window.setCloudModel = setCloudModel;

/**
 * Función para el botón lateral "Seleccionar Modelo Activo"
 * Muestra el mismo submenú que el botón superior
 */
function selectActiveModel() {
    console.log('🔍 selectActiveModel llamado');
    
    // Crear temporalmente el submenú si no existe en el contexto del botón
    const submenu = document.getElementById('submenu-model-selector');
    if (submenu) {
        // Mostrar el submenú existente cerca del cursor o centrado
        submenu.style.display = 'block';
        submenu.style.position = 'fixed';
        submenu.style.top = '50%';
        submenu.style.left = '50%';
        submenu.style.transform = 'translate(-50%, -50%)';
        submenu.style.zIndex = '10000';
        
        // Cargar modelos
        loadInstalledModelsToMainSubmenu();
        
        // Cerrar al hacer clic fuera
        setTimeout(() => {
            document.addEventListener('click', function closeHandler(e) {
                if (!submenu.contains(e.target)) {
                    submenu.style.display = 'none';
                    submenu.style.position = '';
                    submenu.style.top = '';
                    submenu.style.left = '';
                    submenu.style.transform = '';
                    submenu.style.zIndex = '';
                    document.removeEventListener('click', closeHandler);
                }
            });
        }, 100);
    } else {
        alert('❌ Error: No se encontró el menú de selección de modelos');
    }
}

window.selectActiveModel = selectActiveModel;

/**
 * Modal personalizado para API Keys (reemplaza prompt nativo)
 */
let apiKeyCallback = null;

function showApiKeyModal(provider, modelName, callback) {
    const modal = document.getElementById('api-key-modal');
    const title = document.getElementById('api-key-modal-title');
    const message = document.getElementById('api-key-modal-message');
    const input = document.getElementById('api-key-input');
    
    const providerNames = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'groq': 'Groq',
        'gemini': 'Google Gemini',
        'mistral': 'Mistral AI',
        'mimo': 'Xiaomi MiMo'
    };
    
    title.textContent = `🔑 API Key de ${providerNames[provider] || provider}`;
    message.innerHTML = `Ingresa tu API Key para activar el modelo:<br><strong style="color: #0066ff;">${modelName}</strong>`;
    input.value = '';
    
    apiKeyCallback = callback;
    modal.style.display = 'flex';
    
    // Enfocar el input después de un breve delay
    setTimeout(() => input.focus(), 100);
}

function closeApiKeyModal() {
    const modal = document.getElementById('api-key-modal');
    modal.style.display = 'none';
    apiKeyCallback = null;
}

function submitApiKey() {
    console.log('🔑 submitApiKey llamado');
    const input = document.getElementById('api-key-input');
    const apiKey = input.value.trim();
    
    console.log('🔑 API Key ingresada:', apiKey ? 'SÍ (' + apiKey.length + ' caracteres)' : 'NO');
    
    if (!apiKey) {
        alert('⚠️ Por favor ingresa una API Key válida');
        return;
    }
    
    // Guardar el callback ANTES de cerrar el modal
    const callback = apiKeyCallback;
    console.log('🔑 Callback guardado:', callback ? 'SÍ' : 'NO');
    
    closeApiKeyModal();
    
    console.log('🔑 Ejecutando callback...');
    if (callback) {
        console.log('🔑 Callback existe, ejecutando...');
        callback(apiKey);
    } else {
        console.error('❌ callback es NULL');
    }
}

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(e) {
    const modal = document.getElementById('api-key-modal');
    if (e.target === modal) {
        closeApiKeyModal();
    }
});

// Permitir Enter para enviar
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && document.getElementById('api-key-modal').style.display === 'flex') {
        submitApiKey();
    }
    if (e.key === 'Escape' && document.getElementById('api-key-modal').style.display === 'flex') {
        closeApiKeyModal();
    }
});

// ===== FUNCIONES DEL SISTEMA DE PARCHES =====

/**
 * Deshacer el último cambio usando el sistema de snapshots
 */
async function undoLastChange() {
    console.log('↩️ Deshaciendo último cambio...');
    
    try {
        // Cerrar menú
        closeAllMenus();
        
        // Obtener session_id del contexto actual
        const sessionId = window.currentSessionId || 'default';
        
        // Llamar al backend para revertir
        const response = await fetch('/api/revert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.files) {
            // Actualizar editor con código revertido
            const revertedCode = result.files['current_file'] || result.files['index.html'];
            
            if (revertedCode && window.CodeEditorManager) {
                window.CodeEditorManager.setCode(revertedCode);
                
                // Actualizar preview si es HTML
                if (window.PreviewManager && revertedCode.includes('<html')) {
                    window.PreviewManager.updatePreview(revertedCode);
                }
                
                // Mostrar mensaje de éxito
                showNotification('✅ Cambio deshecho correctamente', 'success');
                console.log('✅ Revertido exitosamente');
            } else {
                showNotification('⚠️ No se pudo actualizar el editor', 'warning');
            }
        } else {
            showNotification('⚠️ No hay cambios para deshacer', 'info');
        }
        
    } catch (error) {
        console.error('❌ Error al deshacer:', error);
        showNotification('❌ Error al deshacer: ' + error.message, 'error');
    }
}

/**
 * Mostrar visualizador de diffs
 */
function showDiffViewer() {
    console.log('🔍 Abriendo visualizador de diffs...');
    
    // Cerrar menú
    closeAllMenus();
    
    // Crear modal de visualización de diffs
    const modal = document.createElement('div');
    modal.id = 'diff-viewer-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 1200px;
            height: 80%;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        ">
            <!-- Header -->
            <div style="
                padding: 16px 20px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #f8f9fa;
                border-radius: 8px 8px 0 0;
            ">
                <h3 style="margin: 0; font-size: 16px; color: #333;">🔍 Visualizador de Diffs</h3>
                <button onclick="closeDiffViewer()" style="
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">✕</button>
            </div>
            
            <!-- Content -->
            <div id="diff-content" style="
                flex: 1;
                overflow: auto;
                padding: 20px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.6;
                background: #fafafa;
            ">
                <div style="text-align: center; color: #999; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
                    <div>Cargando historial de cambios...</div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="
                padding: 12px 20px;
                border-top: 1px solid #e0e0e0;
                background: #f8f9fa;
                border-radius: 0 0 8px 8px;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            ">
                <button onclick="loadDiffHistory()" style="
                    padding: 8px 16px;
                    background: #007acc;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                ">🔄 Recargar</button>
                <button onclick="closeDiffViewer()" style="
                    padding: 8px 16px;
                    background: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                ">Cerrar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Cargar historial automáticamente
    setTimeout(() => loadDiffHistory(), 100);
}

/**
 * Cerrar visualizador de diffs
 */
function closeDiffViewer() {
    const modal = document.getElementById('diff-viewer-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Cargar y mostrar historial de diffs
 */
async function loadDiffHistory() {
    const contentDiv = document.getElementById('diff-content');
    if (!contentDiv) return;
    
    try {
        const sessionId = window.currentSessionId || 'default';
        
        const response = await fetch(`/api/history?session_id=${sessionId}&limit=10`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const history = await response.json();
        
        if (!history || history.length === 0) {
            contentDiv.innerHTML = `
                <div style="text-align: center; color: #999; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                    <div>No hay cambios en el historial</div>
                    <div style="font-size: 12px; margin-top: 8px; color: #bbb;">Los cambios aparecerán aquí después de modificar código</div>
                </div>
            `;
            return;
        }
        
        // Generar HTML del historial
        let html = '<div style="max-width: 800px; margin: 0 auto;">';
        html += '<h4 style="margin-bottom: 16px; color: #333;">Historial de Cambios Recientes</h4>';
        
        history.forEach((change, index) => {
            const date = new Date(change.timestamp * 1000).toLocaleString('es-ES');
            
            html += `
                <div style="
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 16px;
                    margin-bottom: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <div style="font-weight: 600; color: #333; margin-bottom: 4px;">
                                ${index + 1}. ${escapeHtml(change.description || 'Sin descripción')}
                            </div>
                            <div style="font-size: 12px; color: #666;">
                                📄 ${escapeHtml(change.file)} | 
                                🔧 ${escapeHtml(change.operation)} | 
                                🕐 ${date}
                            </div>
                        </div>
                        <div style="font-size: 11px; color: #999; font-family: monospace;">
                            ${change.patch_id.substring(0, 12)}...
                        </div>
                    </div>
                    
                    <div style="
                        background: #f8f9fa;
                        border-left: 3px solid #007acc;
                        padding: 12px;
                        margin-top: 8px;
                        font-size: 12px;
                        overflow-x: auto;
                    ">
                        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word; color: #333;">${escapeHtml(change.content_preview)}</pre>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        contentDiv.innerHTML = html;
        
    } catch (error) {
        console.error('Error cargando historial:', error);
        contentDiv.innerHTML = `
            <div style="text-align: center; color: #dc3545; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
                <div>Error al cargar el historial</div>
                <div style="font-size: 12px; margin-top: 8px; color: #999;">${escapeHtml(error.message)}</div>
            </div>
        `;
    }
}

/**
 * Mostrar notificación temporal
 */
function showNotification(message, type = 'info') {
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10001;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Agregar animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Funciones de menú registradas');
