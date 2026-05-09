/**
 * Kalin Frontend - Sidebar Functions (Versión Simplificada)
 * Funciones globales para el menú lateral - Delega a UIManager
 */

// Manejador de errores global para depuración
window.addEventListener('error', function(e) {
    console.error('Error:', e.message, 'en', e.filename, 'línea', e.lineno);
});

/**
 * Toggle sidebar
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('overlay');
    
    if (!sidebar) {
        console.error('No se encontró el elemento .sidebar');
        return;
    }
    
    // Verificar estado actual
    const currentLeft = sidebar.style.left;
    const isOpen = currentLeft === '0px';
    
    // Toggle sidebar
    if (isOpen) {
        // Cerrar
        sidebar.classList.remove('open');
        sidebar.style.left = '-320px';
        
        if (overlay) {
            overlay.classList.remove('show');
        }
    } else {
        // Abrir
        sidebar.classList.add('open');
        sidebar.style.left = '0px';
        
        if (overlay) {
            overlay.classList.add('show');
        }
    }
}

/**
 * Cerrar sidebar
 */
function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('overlay');
    
    if (sidebar) {
        sidebar.classList.remove('open');
        sidebar.style.left = '-320px';
    }
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Hacer funciones disponibles globalmente
if (typeof window !== 'undefined') {
    window.toggleSidebar = toggleSidebar;
    window.closeSidebar = closeSidebar;
}

// Agregar event listeners cuando el DOM esté listo
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        // Botón del menú principal
        const menuToggle = document.querySelector('.menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', function(e) {
                e.preventDefault();
                toggleSidebar();
            });
        }
        
        // Botón cerrar del sidebar (X)
        const sidebarClose = document.querySelector('.sidebar-close');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', function(e) {
                e.preventDefault();
                
                const sidebar = document.querySelector('.sidebar');
                const overlay = document.getElementById('overlay');
                
                if (sidebar) {
                    sidebar.classList.remove('open');
                    sidebar.style.left = '-320px';
                }
                if (overlay) {
                    overlay.classList.remove('show');
                }
            });
        }
        
        // Overlay - cerrar sidebar al hacer clic fuera
        const overlay = document.getElementById('overlay');
        if (overlay) {
            overlay.addEventListener('click', function(e) {
                e.preventDefault();
                
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) {
                    sidebar.classList.remove('open');
                    sidebar.style.left = '-320px';
                }
                
                overlay.classList.remove('show');
            });
        }
        
        // Agregar event listeners a los botones del sidebar
        const sidebarButtons = document.querySelectorAll('.sidebar-btn');
        
        sidebarButtons.forEach((btn) => {
            const onclickAttr = btn.getAttribute('onclick');
            
            btn.addEventListener('click', function(e) {
                if (onclickAttr) {
                    try {
                        const funcName = onclickAttr.replace('()', '');
                        
                        if (typeof window[funcName] === 'function') {
                            window[funcName]();
                        } else {
                            console.error('Función no encontrada:', funcName);
                        }
                    } catch (error) {
                        console.error('Error ejecutando función:', error);
                    }
                }
            });
        });
    });
}
