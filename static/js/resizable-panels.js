/**
 * Kalin Frontend - Módulo de Paneles Redimensionables
 * Permite al usuario arrastrar bordes para redimensionar los paneles
 */

class ResizablePanels {
    constructor() {
        this.isResizing = false;
        this.currentPanel = null;
        this.startX = 0;
        this.startWidth = 0;
        this.minWidth = 250; // Ancho mínimo en px
        this.maxWidthPercent = 70; // Ancho máximo en porcentaje
        
        // Referencias a elementos
        this.codeArea = null;
        this.previewArea = null;
        this.chatSidebar = null;
        this.resizer1 = null; // Entre código y preview
        this.resizer2 = null; // Entre preview y chat
        
        this.initialized = false;
    }

    /**
     * Inicializar el sistema de paneles redimensionables
     */
    initialize() {
        if (this.initialized) return;

        // Obtener referencias a elementos
        this.codeArea = document.querySelector('.code-area');
        this.previewArea = document.querySelector('.preview-area');
        this.chatSidebar = document.querySelector('.chat-sidebar');

        if (!this.codeArea || !this.previewArea || !this.chatSidebar) {
            console.error('❌ Panel elements not found');
            return;
        }

        // Crear resizers
        this.createResizers();
        
        // Configurar event listeners
        this.setupEventListeners();
        
        this.initialized = true;
        console.log('✅ Resizable Panels inicializado');
    }

    /**
     * Crear elementos de resize (barras arrastrables)
     */
    createResizers() {
        // Resizer 1: Entre código y preview
        this.resizer1 = document.createElement('div');
        this.resizer1.className = 'panel-resizer';
        this.resizer1.dataset.resizer = '1';
        this.resizer1.title = 'Arrastra para redimensionar';
        // Forzar estilos inline ultra finos (1px)
        this.resizer1.style.width = '1px';
        this.resizer1.style.background = '#e8e8e8';
        this.resizer1.style.minWidth = '1px';
        this.resizer1.style.maxWidth = '1px';
        
        // Insertar después del code-area
        this.codeArea.parentNode.insertBefore(this.resizer1, this.previewArea);

        // Resizer 2: Entre preview y chat
        this.resizer2 = document.createElement('div');
        this.resizer2.className = 'panel-resizer';
        this.resizer2.dataset.resizer = '2';
        this.resizer2.title = 'Arrastra para redimensionar';
        // Forzar estilos inline ultra finos (1px)
        this.resizer2.style.width = '1px';
        this.resizer2.style.background = '#e8e8e8';
        this.resizer2.style.minWidth = '1px';
        this.resizer2.style.maxWidth = '1px';
        
        // Insertar después del preview-area
        this.previewArea.parentNode.insertBefore(this.resizer2, this.chatSidebar);
    }

    /**
     * Configurar event listeners para drag and drop
     */
    setupEventListeners() {
        // Mouse down en resizers
        document.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        
        // Mouse move global
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        
        // Mouse up global
        document.addEventListener('mouseup', () => this.handleMouseUp());
        
        // Touch events para móvil
        document.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        document.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        document.addEventListener('touchend', () => this.handleMouseUp());
    }

    /**
     * Manejar inicio de resize (mouse down)
     */
    handleMouseDown(e) {
        if (!e.target.classList.contains('panel-resizer')) return;

        e.preventDefault();
        this.isResizing = true;
        this.currentPanel = e.target.dataset.resizer;
        this.startX = e.clientX;

        // Obtener ancho actual del panel izquierdo
        if (this.currentPanel === '1') {
            this.startWidth = this.codeArea.offsetWidth;
        } else if (this.currentPanel === '2') {
            this.startWidth = this.previewArea.offsetWidth;
        }

        // Agregar clase visual
        document.body.classList.add('resizing');
        e.target.classList.add('active');

        console.log(`🔧 Resize iniciado: Panel ${this.currentPanel}`);
    }

    /**
     * Manejar movimiento durante resize (mouse move)
     */
    handleMouseMove(e) {
        if (!this.isResizing) return;

        e.preventDefault();
        const deltaX = e.clientX - this.startX;
        const containerWidth = document.querySelector('.main-layout').offsetWidth;

        if (this.currentPanel === '1') {
            // Redimensionar entre código y preview
            const newCodeWidth = this.startWidth + deltaX;
            const codeWidthPercent = (newCodeWidth / containerWidth) * 100;

            // Validar límites
            if (codeWidthPercent >= 30 && codeWidthPercent <= this.maxWidthPercent) {
                this.codeArea.style.flex = `0 0 ${codeWidthPercent}%`;
                
                // Guardar preferencia
                this.savePanelSizes({
                    code: codeWidthPercent,
                    preview: null,
                    chat: null
                });
            }

        } else if (this.currentPanel === '2') {
            // Redimensionar entre preview y chat
            const newPreviewWidth = this.startWidth + deltaX;
            const previewWidthPercent = (newPreviewWidth / containerWidth) * 100;

            // Validar límites
            if (previewWidthPercent >= 15 && previewWidthPercent <= 40) {
                this.previewArea.style.width = `${previewWidthPercent}%`;
                
                // Ajustar chat automáticamente
                const remainingPercent = 100 - this.getCodeWidthPercent() - previewWidthPercent;
                if (remainingPercent >= 15 && remainingPercent <= 40) {
                    this.chatSidebar.style.width = `${remainingPercent}%`;
                }

                // Guardar preferencia
                this.savePanelSizes({
                    code: null,
                    preview: previewWidthPercent,
                    chat: remainingPercent
                });
            }
        }
    }

    /**
     * Manejar fin de resize (mouse up)
     */
    handleMouseUp() {
        if (!this.isResizing) return;

        this.isResizing = false;
        document.body.classList.remove('resizing');
        
        // Remover clase active de todos los resizers
        document.querySelectorAll('.panel-resizer').forEach(resizer => {
            resizer.classList.remove('active');
        });

        console.log('✅ Resize completado');
    }

    /**
     * Manejar touch start (móvil)
     */
    handleTouchStart(e) {
        if (!e.target.classList.contains('panel-resizer')) return;

        const touch = e.touches[0];
        this.handleMouseDown({
            target: e.target,
            clientX: touch.clientX,
            preventDefault: () => e.preventDefault()
        });
    }

    /**
     * Manejar touch move (móvil)
     */
    handleTouchMove(e) {
        if (!this.isResizing) return;

        const touch = e.touches[0];
        this.handleMouseMove({
            clientX: touch.clientX,
            preventDefault: () => e.preventDefault()
        });
    }

    /**
     * Obtener ancho actual del panel de código en porcentaje
     */
    getCodeWidthPercent() {
        const containerWidth = document.querySelector('.main-layout').offsetWidth;
        return (this.codeArea.offsetWidth / containerWidth) * 100;
    }

    /**
     * Guardar tamaños de paneles en localStorage
     */
    savePanelSizes(sizes) {
        try {
            let savedSizes = JSON.parse(localStorage.getItem('kalin_panel_sizes') || '{}');
            
            if (sizes.code !== null) savedSizes.code = sizes.code;
            if (sizes.preview !== null) savedSizes.preview = sizes.preview;
            if (sizes.chat !== null) savedSizes.chat = sizes.chat;

            localStorage.setItem('kalin_panel_sizes', JSON.stringify(savedSizes));
            console.log('💾 Tamaños de paneles guardados:', savedSizes);
        } catch (error) {
            console.warn('⚠️ No se pudieron guardar tamaños:', error);
        }
    }

    /**
     * Cargar tamaños de paneles desde localStorage
     */
    loadPanelSizes() {
        try {
            const savedSizes = JSON.parse(localStorage.getItem('kalin_panel_sizes'));
            
            if (!savedSizes) return;

            // Aplicar tamaños guardados
            if (savedSizes.code) {
                this.codeArea.style.flex = `0 0 ${savedSizes.code}%`;
            }
            if (savedSizes.preview) {
                this.previewArea.style.width = `${savedSizes.preview}%`;
            }
            if (savedSizes.chat) {
                this.chatSidebar.style.width = `${savedSizes.chat}%`;
            }

            console.log('📂 Tamaños de paneles cargados:', savedSizes);
        } catch (error) {
            console.warn('⚠️ No se pudieron cargar tamaños:', error);
        }
    }

    /**
     * Resetear tamaños a valores por defecto
     */
    resetToDefault() {
        this.codeArea.style.flex = '1'; // 50%
        this.previewArea.style.width = '25%';
        this.chatSidebar.style.width = '25%';
        
        localStorage.removeItem('kalin_panel_sizes');
        console.log('🔄 Tamaños reseteados a valores por defecto');
    }

    /**
     * Obtener estado actual de los paneles
     */
    getStatus() {
        const containerWidth = document.querySelector('.main-layout').offsetWidth;
        
        return {
            code: {
                width: this.codeArea.offsetWidth,
                percent: ((this.codeArea.offsetWidth / containerWidth) * 100).toFixed(1)
            },
            preview: {
                width: this.previewArea.offsetWidth,
                percent: ((this.previewArea.offsetWidth / containerWidth) * 100).toFixed(1)
            },
            chat: {
                width: this.chatSidebar.offsetWidth,
                percent: ((this.chatSidebar.offsetWidth / containerWidth) * 100).toFixed(1)
            }
        };
    }
}

// Exportar como singleton
const resizablePanels = new ResizablePanels();

if (typeof window !== 'undefined') {
    window.ResizablePanels = resizablePanels;
}
