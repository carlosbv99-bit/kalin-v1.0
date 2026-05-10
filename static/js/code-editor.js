/**
 * Kalin Frontend - Módulo de Editor de Código
 * Maneja el editor de código editable, árbol de archivos y pestañas
 */

console.log('📄 code-editor.js cargado correctamente');

/**
 * Sistema de Resaltado de Sintaxis y Formateo
 */
class SyntaxHighlighter {
    constructor() {
        this.languages = {
            python: {
                keywords: ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return', 'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'lambda', 'yield', 'async', 'await', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'],
                builtins: ['print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set', 'tuple', 'type', 'isinstance', 'issubclass', 'super', 'self', 'open', 'input', 'format', 'join', 'split', 'append', 'extend', 'remove', 'pop', 'keys', 'values', 'items', 'get', 'update', 'clear', 'copy', 'sorted', 'reverse', 'min', 'max', 'sum', 'abs', 'round', 'map', 'filter', 'zip', 'enumerate', 'repr', 'eval', 'exec'],
                decorators: ['@staticmethod', '@classmethod', '@property', '@abstractmethod'],
                comment: '#'
            },
            javascript: {
                keywords: ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'class', 'extends', 'super', 'this', 'new', 'typeof', 'instanceof', 'in', 'of', 'async', 'await', 'import', 'export', 'default', 'from', 'true', 'false', 'null', 'undefined'],
                builtins: ['console', 'document', 'window', 'Math', 'Array', 'Object', 'String', 'Number', 'Boolean', 'Date', 'JSON', 'Promise', 'Map', 'Set', 'parseInt', 'parseFloat', 'setTimeout', 'setInterval', 'fetch', 'alert', 'confirm', 'prompt'],
                comment: '//'
            },
            java: {
                keywords: ['public', 'private', 'protected', 'class', 'interface', 'extends', 'implements', 'static', 'final', 'void', 'int', 'double', 'float', 'boolean', 'char', 'String', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'throws', 'new', 'this', 'super', 'import', 'package', 'abstract', 'synchronized'],
                builtins: ['System', 'out', 'println', 'print', 'Math', 'Arrays', 'Collections', 'List', 'ArrayList', 'HashMap', 'Map', 'Set', 'HashSet', 'StringBuilder', 'Integer', 'Double', 'Boolean', 'Exception', 'RuntimeException', 'Thread', 'Runnable'],
                comment: '//'
            }
        };
    }

    /**
     * Detectar lenguaje basado en extensión de archivo
     */
    detectLanguage(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        const langMap = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'javascript',
            'tsx': 'javascript',
            'java': 'java',
            'html': 'html',
            'css': 'css',
            'json': 'json'
        };
        return langMap[ext] || null;
    }

    /**
     * Aplicar resaltado de sintaxis al código
     */
    highlightSyntax(code, language) {
        if (!language || !this.languages[language]) {
            return this.escapeHtml(code);
        }

        const lang = this.languages[language];
        let highlighted = this.escapeHtml(code);

        // Resaltar comentarios
        highlighted = highlighted.replace(
            new RegExp(`(${lang.comment}.*)`, 'g'),
            '<span style="color: #6a9955;">$1</span>'
        );

        // Resaltar strings (comillas simples y dobles)
        highlighted = highlighted.replace(
            /(['"`])(.*?)\1/g,
            '<span style="color: #ce9178;">$1$2$1</span>'
        );

        // Resaltar keywords
        lang.keywords.forEach(keyword => {
            const regex = new RegExp(`\\b(${keyword})\\b`, 'g');
            highlighted = highlighted.replace(
                regex,
                '<span style="color: #569cd6; font-weight: bold;">$1</span>'
            );
        });

        // Resaltar builtins
        if (lang.builtins) {
            lang.builtins.forEach(builtin => {
                const regex = new RegExp(`\\b(${builtin})\\b`, 'g');
                highlighted = highlighted.replace(
                    regex,
                    '<span style="color: #dcdcaa;">$1</span>'
                );
            });
        }

        // Resaltar números
        highlighted = highlighted.replace(
            /\b(\d+)\b/g,
            '<span style="color: #b5cea8;">$1</span>'
        );

        // Resaltar decoradores (Python)
        if (lang.decorators) {
            lang.decorators.forEach(decorator => {
                highlighted = highlighted.replace(
                    new RegExp(decorator.replace('@', '\\@'), 'g'),
                    '<span style="color: #dcdcaa;">' + decorator + '</span>'
                );
            });
        }

        return highlighted;
    }

    /**
     * Escapar HTML para seguridad
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Formatear código con indentación automática
     */
    formatCode(code, language) {
        if (!language || !code) return code;

        const lines = code.split('\n');
        const formatted = [];
        let indentLevel = 0;
        const indentSize = 4;
        const indent = ' '.repeat(indentSize);

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            const trimmedLine = line.trim();
            
            // Saltar líneas vacías
            if (!trimmedLine) {
                formatted.push('');
                continue;
            }

            // Reducir indentación para líneas que cierran bloques
            if (this.isClosingLine(trimmedLine, language)) {
                indentLevel = Math.max(0, indentLevel - 1);
            }

            // Aplicar indentación
            const currentIndent = indent.repeat(indentLevel);
            formatted.push(currentIndent + trimmedLine);

            // Aumentar indentación para líneas que abren bloques
            if (this.isOpenLine(trimmedLine, language)) {
                indentLevel++;
            }
        }

        return formatted.join('\n');
    }

    /**
     * Verificar si una línea abre un bloque
     */
    isOpenLine(line, language) {
        const openPatterns = {
            python: [/:\s*$/, /\{$/],
            javascript: [/\{$/, /\($/, /\[$/],
            java: [/\{$/, /\($/, /\[$/]
        };

        const patterns = openPatterns[language] || [];
        return patterns.some(pattern => pattern.test(line));
    }

    /**
     * Verificar si una línea cierra un bloque
     */
    isClosingLine(line, language) {
        const closePatterns = {
            python: [],
            javascript: [/^\}/, /^\)/, /^\]/],
            java: [/^\}/, /^\)/, /^\]/]
        };

        const patterns = closePatterns[language] || [];
        return patterns.some(pattern => pattern.test(line));
    }
}

class CodeEditorManager {
    constructor() {
        this.codeEditor = null;
        this.lineNumbers = null;
        this.fileTabs = null;
        this.fileTreeContent = null;
        this.currentFileName = null;
        this.openFiles = []; // Archivos abiertos en pestañas
        this.currentFile = null; // Archivo actualmente activo
        this.projectFiles = []; // Lista de archivos del proyecto
        this.initialized = false;
        this.undoStack = []; // Historial para deshacer
        this.redoStack = []; // Historial para rehacer
        this.lastSavedState = ''; // Último estado guardado
    }

    /**
     * Inicializar el manager del editor de código
     */
    initialize() {
        if (this.initialized) return;

        this.codeEditor = document.getElementById('code-editor');
        this.lineNumbers = document.getElementById('line-numbers');
        this.fileTabs = document.getElementById('file-tabs');
        this.fileTreeContent = document.getElementById('file-tree-content');
        this.currentFileName = document.getElementById('current-file-name');

        if (!this.codeEditor || !this.lineNumbers) {
            console.error('❌ Elementos del editor de código no encontrados');
            return;
        }

        this.setupEventListeners();
        this.loadProjectFiles();
        this.initialized = true;
        console.log('✅ Code Editor Manager inicializado');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Sincronizar scroll entre editor y números de línea
        this.codeEditor.addEventListener('scroll', () => {
            this.lineNumbers.scrollTop = this.codeEditor.scrollTop;
            // Sincronizar contenedor de guías
            const guidesContainer = document.getElementById('indent-guides-container');
            if (guidesContainer) {
                guidesContainer.style.transform = `translate(${-this.codeEditor.scrollLeft}px, ${-this.codeEditor.scrollTop}px)`;
            }
        });

        // Actualizar números de línea al cambiar el contenido
        this.codeEditor.addEventListener('input', () => {
            this.saveState(); // Guardar estado antes de cambiar
            this.updateLineNumbers();
            this.autoSaveCurrentFile();
            // Actualizar guías de indentación
            setTimeout(() => this.updateIndentGuides(), 10);
        });

        // Manejar tecla Tab para indentación
        this.codeEditor.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.codeEditor.selectionStart;
                const end = this.codeEditor.selectionEnd;

                // Insertar 4 espacios
                this.codeEditor.value = this.codeEditor.value.substring(0, start) + '    ' + this.codeEditor.value.substring(end);

                // Mover cursor
                this.codeEditor.selectionStart = this.codeEditor.selectionEnd = start + 4;
                this.updateLineNumbers();
            }
            
            // Auto-indentación al presionar Enter
            if (e.key === 'Enter') {
                e.preventDefault();
                const start = this.codeEditor.selectionStart;
                const end = this.codeEditor.selectionEnd;
                const value = this.codeEditor.value;
                
                // Obtener la línea actual
                const lineStart = value.lastIndexOf('\n', start - 1) + 1;
                const currentLine = value.substring(lineStart, start);
                
                // Calcular indentación actual
                const indentMatch = currentLine.match(/^(\s*)/);
                let indent = indentMatch ? indentMatch[1] : '';
                
                // Verificar si la línea termina en : o { (aumentar indentación)
                const trimmedLine = currentLine.trim();
                if (trimmedLine.endsWith(':') || trimmedLine.endsWith('{') || trimmedLine.endsWith('(')) {
                    indent += '    ';
                }
                
                // Insertar nueva línea con indentación
                const newValue = value.substring(0, start) + '\n' + indent + value.substring(end);
                this.codeEditor.value = newValue;
                
                // Mover cursor al final de la nueva línea indentada
                const newCursorPos = start + 1 + indent.length;
                this.codeEditor.selectionStart = this.codeEditor.selectionEnd = newCursorPos;
                
                this.updateLineNumbers();
            }
        });

        // Resaltado de línea al hacer click o mover el cursor
        this.codeEditor.addEventListener('click', (e) => this.highlightCurrentLine());
        this.codeEditor.addEventListener('keyup', (e) => this.highlightCurrentLine());
        this.codeEditor.addEventListener('mouseup', (e) => this.highlightCurrentLine());

        // Manejar Ctrl+Z (deshacer) y Ctrl+Y (rehacer)
        this.codeEditor.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undo();
            }
            if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
                e.preventDefault();
                this.redo();
            }
        });

        // Botón ejecutar código
        const runBtn = document.getElementById('run-code-btn');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runCode());
        }

        // Botón cerrar output
        const closeOutputBtn = document.getElementById('close-output-btn');
        if (closeOutputBtn) {
            closeOutputBtn.addEventListener('click', () => this.hideOutput());
        }
    }

    /**
     * Actualizar números de línea
     */
    updateLineNumbers() {
        if (!this.codeEditor || !this.lineNumbers) return;
        
        const lines = this.codeEditor.value.split('\n');
        const lineCount = lines.length;
        
        // Crear HTML con cada número en su propia línea usando <div>
        let lineNumbersHTML = '';
        for (let i = 1; i <= lineCount; i++) {
            lineNumbersHTML += `<div>${i}</div>`;
        }
        
        this.lineNumbers.innerHTML = lineNumbersHTML;
        
        // Ajustar el ancho del contenedor de números si es necesario
        const maxWidth = String(lineCount).length * 10 + 20;
        this.lineNumbers.style.minWidth = Math.max(50, maxWidth) + 'px';
    }

    /**
     * Resaltar línea actual
     */
    highlightCurrentLine() {
        const highlight = document.getElementById('line-highlight');
        if (!highlight || !this.codeEditor) return;

        // Calcular posición de la línea actual
        const cursorPos = this.codeEditor.selectionStart;
        const textBeforeCursor = this.codeEditor.value.substring(0, cursorPos);
        const currentLine = textBeforeCursor.split('\n').length;

        // Calcular posición Y basada en la línea
        const lineHeight = 22.4; // Ajustado al line-height del editor
        const paddingTop = 16; // Padding superior del textarea
        const topPos = paddingTop + (currentLine - 1) * lineHeight - this.codeEditor.scrollTop;

        // Mostrar y posicionar el resaltado
        highlight.style.display = 'block';
        highlight.style.top = topPos + 'px';
    }

    /**
     * Guardar estado actual en el historial
     */
    saveState() {
        if (!this.codeEditor) return;
        
        const currentState = this.codeEditor.value;
        
        // No guardar si es igual al último estado
        if (this.undoStack.length > 0 && this.undoStack[this.undoStack.length - 1] === currentState) {
            return;
        }
        
        // Agregar al historial de deshacer
        this.undoStack.push(currentState);
        
        // Limitar el historial a 50 estados para no consumir mucha memoria
        if (this.undoStack.length > 50) {
            this.undoStack.shift();
        }
        
        // Limpiar el historial de rehacer cuando se hace un cambio nuevo
        this.redoStack = [];
    }

    /**
     * Deshacer última acción (Ctrl+Z)
     */
    undo() {
        if (this.undoStack.length <= 1) {
            console.log('⚠️ Nada que deshacer');
            return;
        }
        
        // Mover estado actual al historial de rehacer
        const currentState = this.undoStack.pop();
        this.redoStack.push(currentState);
        
        // Restaurar estado anterior
        const previousState = this.undoStack[this.undoStack.length - 1];
        this.codeEditor.value = previousState;
        this.updateLineNumbers();
        this.updateIndentGuides();
        this.autoSaveCurrentFile();
        
        console.log('↩️ Deshecho');
    }

    /**
     * Rehacer acción deshecha (Ctrl+Y o Ctrl+Shift+Z)
     */
    redo() {
        if (this.redoStack.length === 0) {
            console.log('⚠️ Nada que rehacer');
            return;
        }
        
        // Sacar estado del historial de rehacer
        const nextState = this.redoStack.pop();
        this.undoStack.push(nextState);
        
        // Aplicar estado
        this.codeEditor.value = nextState;
        this.updateLineNumbers();
        this.updateIndentGuides();
        this.autoSaveCurrentFile();
        
        console.log('↪️ Rehecho');
    }

    /**
     * Actualizar guías de indentación verticales
     */
    updateIndentGuides() {
        if (!this.codeEditor) return;

        const wrapper = document.querySelector('.code-editor-wrapper');
        if (!wrapper) return;

        // Eliminar guías existentes
        const existingGuides = document.querySelectorAll('.indent-guide');
        existingGuides.forEach(guide => guide.remove());

        const code = this.codeEditor.value;
        if (!code) return; // No crear guías si no hay código

        const lines = code.split('\n');
        const charWidth = 8.4; // Ancho aproximado de un carácter en la fuente monospace
        const paddingLeft = 60; // Padding izquierdo del textarea
        const paddingTop = 16;
        const indentSize = 4; // 4 espacios por nivel

        // Crear contenedor para las guías
        let guidesContainer = document.getElementById('indent-guides-container');
        if (!guidesContainer) {
            guidesContainer = document.createElement('div');
            guidesContainer.id = 'indent-guides-container';
            guidesContainer.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                z-index: 0;
            `;
            wrapper.insertBefore(guidesContainer, wrapper.firstChild);
        }

        // Crear guías para cada nivel de indentación visible
        const maxLevel = 10; // Máximo nivel de indentación a mostrar
        
        for (let level = 1; level <= maxLevel; level++) {
            const xPos = paddingLeft + (level * indentSize * charWidth);
            
            // Verificar si hay líneas que usan este nivel de indentación
            let hasContent = false;
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const match = line.match(/^(\s*)/);
                if (match) {
                    const leadingSpaces = match[1].length;
                    if (leadingSpaces >= level * indentSize) {
                        hasContent = true;
                        break;
                    }
                }
            }

            if (hasContent) {
                const guide = document.createElement('div');
                guide.className = 'indent-guide';
                guide.style.cssText = `
                    position: absolute;
                    left: ${xPos}px;
                    top: 0;
                    height: ${lines.length * 22.4}px;
                    width: 1px;
                    background: rgba(100, 100, 100, 0.15);
                    pointer-events: none;
                `;
                
                guidesContainer.appendChild(guide);
            }
        }
    }

    /**
     * Cargar archivos del proyecto (simulado por ahora)
     */
    async loadProjectFiles() {
        // NO cargar archivos de ejemplo - esperar a que el usuario abra un proyecto
        this.projectFiles = [];
        this.fileTreeContent.innerHTML = '<div style="padding: 4px 0; color: #666;">Abre un proyecto para ver los archivos</div>';
    }

    /**
     * Renderizar árbol de archivos
     */
    renderFileTree() {
        if (!this.fileTreeContent) return;

        this.fileTreeContent.innerHTML = '';

        this.projectFiles.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.style.cssText = 'padding: 6px 8px; cursor: pointer; border-radius: 4px; margin: 2px 0; transition: background 0.2s;';
            fileItem.textContent = '📄 ' + file.name;
            
            fileItem.addEventListener('mouseenter', () => {
                fileItem.style.background = '#e9ecef';
            });
            
            fileItem.addEventListener('mouseleave', () => {
                fileItem.style.background = 'transparent';
            });
            
            fileItem.addEventListener('click', () => this.openFile(file));
            
            this.fileTreeContent.appendChild(fileItem);
        });
    }

    /**
     * Abrir un archivo en el editor
     */
    async openFile(file) {
        // Verificar si el archivo ya está abierto
        const existingTab = this.openFiles.find(f => f.path === file.path);
        
        if (!existingTab) {
            // Agregar a archivos abiertos
            this.openFiles.push({
                ...file,
                content: await this.loadFileContent(file.path)
            });
        }

        // Cambiar a este archivo
        this.currentFile = this.openFiles.find(f => f.path === file.path);
        this.renderTabs();
        this.displayFileInEditor(this.currentFile);
    }

    /**
     * Cargar contenido del archivo (simulado)
     */
    async loadFileContent(filePath) {
        // En una implementación real, esto vendría del backend
        // Por ahora, retornamos contenido de ejemplo
        const fileContents = {
            '/main.py': '# Archivo principal de Kalin AI\n\ndef main():\n    print("Hola desde Kalin!")\n\nif __name__ == "__main__":\n    main()',
            '/utils.py': '# Utilidades varias\n\ndef helper_function():\n    return "Ayuda"',
            '/config.py': '# Configuración\n\nDEBUG = True\nVERSION = "1.0"',
            '/README.md': '# Kalin AI\n\nAsistente de desarrollo inteligente.'
        };

        return fileContents[filePath] || '# Contenido de ' + filePath;
    }

    /**
     * Renderizar pestañas de archivos
     */
    renderTabs() {
        if (!this.fileTabs) return;

        this.fileTabs.innerHTML = '';

        this.openFiles.forEach(file => {
            const tab = document.createElement('div');
            tab.style.cssText = `
                padding: 8px 16px; 
                cursor: pointer; 
                border-right: 1px solid #ddd; 
                background: ${this.currentFile && this.currentFile.path === file.path ? '#ffffff' : '#f0f0f0'};
                font-size: 13px;
                white-space: nowrap;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            
            tab.innerHTML = `
                <span>📄 ${file.name}</span>
                <span onclick="event.stopPropagation(); window.CodeEditorManager.closeFile('${file.path}')" 
                      style="margin-left: 8px; opacity: 0.6; cursor: pointer; font-weight: bold;">×</span>
            `;
            
            tab.addEventListener('click', () => {
                this.currentFile = this.openFiles.find(f => f.path === file.path);
                this.renderTabs();
                this.displayFileInEditor(this.currentFile);
            });
            
            this.fileTabs.appendChild(tab);
        });
    }

    /**
     * Cerrar un archivo
     */
    closeFile(filePath) {
        const index = this.openFiles.findIndex(f => f.path === filePath);
        if (index > -1) {
            this.openFiles.splice(index, 1);
            
            // Si cerramos el archivo actual, cambiar a otro
            if (this.currentFile && this.currentFile.path === filePath) {
                this.currentFile = this.openFiles.length > 0 ? this.openFiles[0] : null;
            }
            
            this.renderTabs();
            
            if (this.currentFile) {
                this.displayFileInEditor(this.currentFile);
            } else {
                this.showPlaceholder();
            }
        }
    }

    /**
     * Mostrar archivo en el editor
     */
    displayFileInEditor(file) {
        const placeholder = document.getElementById('code-placeholder');
        const editorContainer = document.getElementById('code-editor-container');
        
        if (placeholder) placeholder.style.display = 'none';
        if (editorContainer) {
            editorContainer.style.display = 'flex';
            this.codeEditor.value = file.content;
            this.currentFileName.textContent = file.name;
            // Actualizar números de línea después de un pequeño delay para asegurar que el contenido esté renderizado
            setTimeout(() => {
                this.updateLineNumbers();
                this.updateIndentGuides(); // Actualizar guías de indentación
                this.undoStack = [this.codeEditor.value]; // Guardar estado inicial
                this.redoStack = []; // Limpiar rehacer
            }, 10);
        }
    }

    /**
     * Mostrar placeholder cuando no hay archivos
     */
    showPlaceholder() {
        const placeholder = document.getElementById('code-placeholder');
        const editorContainer = document.getElementById('code-editor-container');
        
        if (placeholder) placeholder.style.display = 'flex';
        if (editorContainer) editorContainer.style.display = 'none';
    }

    /**
     * Copiar código al portapapeles
     */
    async copyCode() {
        if (!this.codeEditor || !this.codeEditor.value) return;

        try {
            await navigator.clipboard.writeText(this.codeEditor.value);
            
            // Feedback visual temporal
            const copyBtn = document.getElementById('copy-code-btn');
            if (copyBtn) {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✓ Copiado';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('Error al copiar:', err);
            alert('No se pudo copiar el código');
        }
    }

    /**
     * Descargar código como archivo
     */
    downloadCode() {
        if (!this.codeEditor || !this.codeEditor.value || !this.currentFile) return;

        const blob = new Blob([this.codeEditor.value], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.currentFile.name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    /**
     * Formatear código automáticamente
     */
    formatCode() {
        if (!this.codeEditor || !this.codeEditor.value) return;

        const currentCode = this.codeEditor.value;
        
        // Guardar backup para deshacer
        this.lastCodeBeforeFormat = currentCode;

        try {
            // Aplicar formateo básico y seguro
            const formattedCode = this.basicFormat(currentCode);
                    
            // Actualizar editor
            this.codeEditor.value = formattedCode;
            this.updateLineNumbers();
            this.updateIndentGuides();
            this.autoSaveCurrentFile();

            console.log('✅ Código formateado');
            
            // Mostrar botón de deshacer
            this.showUndoButton();

        } catch (error) {
            console.error('❌ Error al formatear:', error);
            alert('Error al formatear. Se ha restaurado el código original.');
            this.codeEditor.value = currentCode;
        }
    }

    /**
     * Formateo básico que preserva la estructura del código
     */
    basicFormat(code) {
        const lines = code.split('\n');
        const result = [];
        let indentLevel = 0;
        const indentString = '    '; // 4 espacios

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmed = line.trim();

            // Preservar líneas vacías sin indentación
            if (trimmed === '') {
                result.push('');
                continue;
            }

            // Detectar líneas que cierran bloques
            const isClosing = /^\s*[}\])]/.test(line);
            if (isClosing && indentLevel > 0) {
                indentLevel--;
            }

            // Aplicar indentación actual
            const indentedLine = indentString.repeat(indentLevel) + trimmed;
            result.push(indentedLine);

            // Detectar líneas que abren bloques
            const isOpening = /[:{]\s*$/.test(trimmed) || /[({\[]$/.test(trimmed);
            if (isOpening) {
                indentLevel++;
            }
        }

        return result.join('\n');
    }

    /**
     * Mostrar botón de deshacer formateo
     */
    showUndoButton() {
        // Remover botón anterior si existe
        const existingBtn = document.getElementById('undo-format-btn');
        if (existingBtn) existingBtn.remove();

        const undoBtn = document.createElement('button');
        undoBtn.id = 'undo-format-btn';
        undoBtn.textContent = '↩️ Deshacer Formateo';
        undoBtn.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
        `;
        
        undoBtn.onmouseenter = () => {
            undoBtn.style.background = '#ff5252';
            undoBtn.style.transform = 'scale(1.05)';
        };
        undoBtn.onmouseleave = () => {
            undoBtn.style.background = '#ff6b6b';
            undoBtn.style.transform = 'scale(1)';
        };
        
        undoBtn.onclick = () => this.undoFormat();
        document.body.appendChild(undoBtn);

        // Auto-ocultar después de 15 segundos
        setTimeout(() => {
            if (undoBtn.parentNode) {
                undoBtn.style.opacity = '0';
                setTimeout(() => undoBtn.remove(), 300);
            }
        }, 15000);
    }

    /**
     * Deshacer último formateo
     */
    undoFormat() {
        if (this.lastCodeBeforeFormat && this.codeEditor) {
            this.codeEditor.value = this.lastCodeBeforeFormat;
            this.updateLineNumbers();
            this.updateIndentGuides();
            this.autoSaveCurrentFile();
            
            // Remover botón
            const undoBtn = document.getElementById('undo-format-btn');
            if (undoBtn) undoBtn.remove();
            
            console.log('✅ Formateo deshecho');
        }
    }

    /**
     * Auto-guardar archivo actual (simulado)
     */
    autoSaveCurrentFile() {
        if (this.currentFile && this.codeEditor) {
            this.currentFile.content = this.codeEditor.value;
            // En una implementación real, aquí se enviaría al backend
        }
    }

    /**
     * Mostrar código generado por Kalin
     */
    displayGeneratedCode(code, fileName = 'generated.py') {
        const filePath = '/' + fileName;
        
        // Verificar si el archivo ya está abierto
        const existingFile = this.openFiles.find(f => f.path === filePath);
        
        if (existingFile) {
            // Si ya existe, actualizar su contenido y cambiar a él
            existingFile.content = code;
            this.currentFile = existingFile;
        } else {
            // Crear un nuevo archivo
            const newFile = {
                name: fileName,
                path: filePath,
                type: 'file',
                content: code
            };
            
            // Agregar a archivos abiertos
            this.openFiles.push(newFile);
            this.currentFile = newFile;
        }
        
        // Actualizar UI
        this.renderTabs();
        this.displayFileInEditor(this.currentFile);
        
        console.log('✅ Código mostrado en editor:', fileName, '-', code.length, 'chars');
    }

    /**
     * Ejecutar código con WebContainer
     */
    async runCode() {
        if (!this.currentFile || !this.codeEditor) {
            alert('No hay código para ejecutar');
            return;
        }

        if (!window.WebContainerManager) {
            alert('WebContainer no está disponible. Verifica tu conexión a internet.');
            return;
        }

        try {
            // Mostrar panel de output
            this.showOutput();
            this.clearOutput();
            this.appendOutput('🚀 Iniciando ejecución...\n');

            // Determinar el tipo de archivo y comando a ejecutar
            const fileName = this.currentFile.name.toLowerCase();
            const code = this.codeEditor.value;

            if (fileName.endsWith('.js')) {
                // Ejecutar JavaScript con Node.js
                await this.runJavaScript(code);
            } else if (fileName.endsWith('.html')) {
                // Para HTML, usar el preview existente
                if (window.PreviewManager) {
                    window.PreviewManager.render(code);
                    this.appendOutput('✅ HTML renderizado en el panel de Preview\n');
                } else {
                    this.appendOutput('⚠️ Preview Manager no disponible\n');
                }
            } else if (fileName.endsWith('.py')) {
                // Python no es soportado nativamente por WebContainers
                this.appendOutput('⚠️ Python no es soportado directamente en WebContainers.\n');
                this.appendOutput('💡 Sugerencia: Usa el backend de Kalin para ejecutar código Python.\n');
            } else {
                this.appendOutput('⚠️ Tipo de archivo no soportado para ejecución: ' + fileName + '\n');
            }

        } catch (error) {
            console.error('❌ Error ejecutando código:', error);
            this.appendOutput('❌ Error: ' + error.message + '\n');
        }
    }

    /**
     * Ejecutar código JavaScript
     */
    async runJavaScript(code) {
        if (!window.WebContainerManager) return;

        try {
            // Escribir archivo index.js
            await window.WebContainerManager.writeFile('index.js', code);
            this.appendOutput('📝 Archivo index.js creado\n');

            // Ejecutar con Node.js
            this.appendOutput('▶️ Ejecutando node index.js...\n\n');
            
            await window.WebContainerManager.runCommand('node index.js', (output) => {
                this.appendOutput(output);
            });

            this.appendOutput('\n✅ Ejecución completada\n');

        } catch (error) {
            this.appendOutput('❌ Error: ' + error.message + '\n');
        }
    }

    /**
     * Mostrar panel de output
     */
    showOutput() {
        const outputPanel = document.getElementById('webcontainer-output');
        if (outputPanel) {
            outputPanel.style.display = 'block';
        }
    }

    /**
     * Ocultar panel de output
     */
    hideOutput() {
        const outputPanel = document.getElementById('webcontainer-output');
        if (outputPanel) {
            outputPanel.style.display = 'none';
        }
    }

    /**
     * Limpiar output
     */
    clearOutput() {
        const outputContent = document.getElementById('output-content');
        if (outputContent) {
            outputContent.textContent = '';
        }
    }

    /**
     * Agregar texto al output
     */
    appendOutput(text) {
        const outputContent = document.getElementById('output-content');
        if (outputContent) {
            outputContent.textContent += text;
            // Auto-scroll al final
            outputContent.parentElement.scrollTop = outputContent.parentElement.scrollHeight;
        }
    }
}

// Exportar como singleton
const codeEditorManager = new CodeEditorManager();

if (typeof window !== 'undefined') {
    window.CodeEditorManager = codeEditorManager;
}

// ===== FUNCIONES GLOBALES PARA MENÚS =====

/**
 * Abrir archivo/proyecto
 */
function openProject() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.py,.js,.html,.css,.json,.md,.txt';
    
    input.onchange = async (e) => {
        const files = e.target.files;
        for (let file of files) {
            const content = await file.text();
            if (window.CodeEditorManager) {
                window.CodeEditorManager.displayGeneratedCode(content, file.name);
            }
        }
    };
    
    input.click();
    closeAllMenus();
}

/**
 * Guardar archivo actual
 */
function saveFile() {
    if (window.CodeEditorManager && window.CodeEditorManager.currentFile) {
        window.CodeEditorManager.downloadCode();
    } else {
        alert('No hay archivo abierto para guardar');
    }
    closeAllMenus();
}

/**
 * Guardar como...
 */
function saveFileAs() {
    saveFile(); // Por ahora igual que guardar
    closeAllMenus();
}

/**
 * Copiar código
 */
function copyCode() {
    if (window.CodeEditorManager) {
        window.CodeEditorManager.copyCode();
    }
    closeAllMenus();
}

/**
 * Formatear código
 */
function formatCode() {
    if (window.CodeEditorManager) {
        window.CodeEditorManager.formatCode();
    }
    closeAllMenus();
}

/**
 * Pegar código
 */
async function pasteCode() {
    try {
        const text = await navigator.clipboard.readText();
        if (window.CodeEditorManager && window.CodeEditorManager.codeEditor) {
            const editor = window.CodeEditorManager.codeEditor;
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            editor.value = editor.value.substring(0, start) + text + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + text.length;
        }
    } catch (err) {
        console.error('Error al pegar:', err);
        alert('No se pudo acceder al portapapeles');
    }
    closeAllMenus();
}

/**
 * Cortar código
 */
function cutCode() {
    if (window.CodeEditorManager && window.CodeEditorManager.codeEditor) {
        const editor = window.CodeEditorManager.codeEditor;
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const selected = editor.value.substring(start, end);
        
        navigator.clipboard.writeText(selected);
        editor.value = editor.value.substring(0, start) + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start;
    }
    closeAllMenus();
}

/**
 * Cerrar archivo actual
 */
function closeFile() {
    if (window.CodeEditorManager && window.CodeEditorManager.currentFile) {
        const path = window.CodeEditorManager.currentFile.path;
        window.CodeEditorManager.closeFile(path);
    }
    closeAllMenus();
}

/**
 * Abrir proyecto (seleccionar carpeta)
 */
function openProject() {
    // En un navegador, no podemos seleccionar carpetas directamente
    // Usamos múltiples archivos como simulación
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true; // Permite seleccionar directorios (Chrome/Edge)
    input.directory = true;
    
    input.onchange = async (e) => {
        const files = e.target.files;
        
        // Filtrar archivos irrelevantes (node_modules, .git, build, caché, etc.)
        const EXCLUDED_DIRS = ['node_modules', '.git', 'build', 'dist', '.vscode', '.idea', '__pycache__', '.venv', 'venv', '.next', 'out', 'target', 'obj', 'bin', '.gradle', 'gradle', 'captures', 'apk', 'Debug', 'Release'];
        const EXCLUDED_EXTS = ['.tab', '.len', '.keystream', '.suo', '.user', '.pdb', '.ilk', '.obj', '.o', '.class', '.pyc', '.pyo', '.dex', '.aar', '.apk', '.so', '.dylib', '.jar', '.iml', '.ipr', '.iws', '.log', '.tmp'];
        
        // Para proyectos grandes, solo cargar archivos de código fuente
        const SOURCE_EXTS = ['.java', '.kt', '.kts', '.xml', '.gradle', '.kts', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.md', '.txt', '.yml', '.yaml', '.properties', '.pro', '.cfg', '.ini', '.cmake', '.cpp', '.c', '.h', '.hpp', '.swift', '.dart', '.rs', '.go', '.rb', '.php'];
        
        const filteredFiles = Array.from(files).filter(file => {
            const path = file.webkitRelativePath || file.name;
            const parts = path.split('/');
            
            // Excluir si está en carpeta ignorada
            for (let part of parts) {
                if (EXCLUDED_DIRS.includes(part)) {
                    return false;
                }
            }
            
            // Excluir por extensión
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (EXCLUDED_EXTS.includes(ext)) {
                return false;
            }
            
            // Para proyectos MUY grandes (>500 archivos), solo cargar archivos de código fuente
            if (files.length > 500 && !SOURCE_EXTS.includes(ext)) {
                return false;
            }
            
            // Excluir archivos muy grandes (>500KB para proyectos grandes, >1MB para pequeños)
            const maxSize = files.length > 500 ? 500 * 1024 : 1024 * 1024;
            if (file.size > maxSize) {
                return false;
            }
            
            return true;
        });
        

        
        if (filteredFiles.length === 0) {
            alert('⚠️ No se encontraron archivos válidos. La carpeta puede contener solo archivos de caché o binarios.');
            return;
        }
        
        // DEBUG: Mostrar información inmediatamente

        
        if (!window.CodeEditorManager) {
            console.error('❌ CodeEditorManager no está inicializado');
            alert('Error: El editor no está listo. Recarga la página.');
            return;
        }
        
        if (files.length === 0) {

            alert('⚠️ No se seleccionaron archivos. Intenta nuevamente.');
            return;
        }
        
        // Limpiar proyecto anterior
        window.CodeEditorManager.projectFiles = [];
        window.CodeEditorManager.openFiles = [];
        window.CodeEditorManager.currentFile = null;
        window.CodeEditorManager.fileTreeStructure = {};
        
        // Limpiar UI
        if (window.CodeEditorManager.fileTreeContent) {
            window.CodeEditorManager.fileTreeContent.innerHTML = '<div style="padding: 4px 0; color: #666;">Cargando...</div>';
        }
        if (window.CodeEditorManager.fileTabs) {
            window.CodeEditorManager.fileTabs.innerHTML = '';
        }
        
        // Obtener nombre del proyecto (primera carpeta del path)
        let projectName = 'Sin Nombre';
        if (filteredFiles.length > 0) {
            const firstPath = filteredFiles[0].webkitRelativePath || filteredFiles[0].name;
            const parts = firstPath.split('/');
            if (parts.length > 1) {
                projectName = parts[0]; // Primera carpeta es el nombre del proyecto
            } else {
                projectName = 'Archivos Sueltos';
            }
        }
        

        
        // Actualizar título del proyecto en el panel
        const projectTitleEl = document.getElementById('project-title');
        if (projectTitleEl) {
            projectTitleEl.textContent = '📁 ' + projectName;
        }
        
        try {
            // Organizar archivos en estructura de árbol
            const fileTree = {};
            const filesArray = filteredFiles; // Usar archivos filtrados
            

            
            // Para proyectos pequeños (<20 archivos), procesar todos juntos
            // Para proyectos grandes, usar lotes
            const USE_BATCHES = filesArray.length > 20;
            const BATCH_SIZE = 5;
            const totalBatches = USE_BATCHES ? Math.ceil(filesArray.length / BATCH_SIZE) : 1;
            

            
            for (let batchIndex = 0; batchIndex < totalBatches; batchIndex++) {
                const start = batchIndex * BATCH_SIZE;
                const end = USE_BATCHES ? Math.min(start + BATCH_SIZE, filesArray.length) : filesArray.length;
                const batch = filesArray.slice(start, end);
                

                
                // Crear promesas para este lote
                const batchPromises = batch.map((file) => {
                    return new Promise((resolve) => {
                        try {
                            const path = file.webkitRelativePath || file.name;
                            const parts = path.split('/');
                            
                            // Construir estructura jerárquica
                            let current = fileTree;
                            for (let i = 0; i < parts.length; i++) {
                                const part = parts[i];
                                if (i === parts.length - 1) {
                                    // Es un archivo
                                    current[part] = {
                                        type: 'file',
                                        fullPath: path,
                                        name: part,
                                        content: null
                                    };
                                } else {
                                    // Es una carpeta
                                    if (!current[part]) {
                                        current[part] = { type: 'folder', children: {} };
                                    }
                                    current = current[part].children;
                                }
                            }
                            

                            const reader = new FileReader();
                            
                            let resolved = false;
                            
                            reader.onload = (e) => {
                                if (resolved) {

                                    return;
                                }
                                resolved = true;
                                

                                const content = e.target.result;
                                
                                // Guardar en la estructura del árbol
                                let treeRef = fileTree;
                                for (let i = 0; i < parts.length - 1; i++) {
                                    if (treeRef[parts[i]] && treeRef[parts[i]].children) {
                                        treeRef = treeRef[parts[i]].children;
                                    } else {
                                        console.warn(`⚠️ Ruta no encontrada para: ${path}`);
                                        resolve();
                                        return;
                                    }
                                }
                                const fileName = parts[parts.length - 1];
                                if (treeRef[fileName]) {
                                    treeRef[fileName].content = content;

                                } else {

                                }
                                
                                // También guardar en projectFiles
                                window.CodeEditorManager.projectFiles.push({
                                    name: file.name,
                                    path: path,
                                    type: 'file',
                                    size: file.size,
                                    content: content
                                });
                                

                                resolve();
                            };
                            
                            reader.onerror = () => {
                                if (resolved) {

                                    return;
                                }
                                resolved = true;
                                
                                console.error(`❌ Error leyendo archivo: ${path} (error code: ${reader.error?.code})`);
                                resolve(); // Resolver igual para continuar
                            };
                            
                            reader.onabort = () => {
                                if (resolved) return;
                                resolved = true;
                                console.warn(`⚠️ Lectura abortada: ${path}`);
                                resolve();
                            };
                            
                            // Timeout individual por archivo (5 segundos)
                            const fileTimeout = setTimeout(() => {
                                if (!resolved) {
                                    resolved = true;
                                    console.error(`⏱️ Timeout leyendo archivo: ${path}`);
                                    resolve();
                                }
                            }, 5000);
                            
                            // Modificar resolve para limpiar timeout
                            const originalResolve = resolve;
                            resolve = () => {
                                clearTimeout(fileTimeout);
                                originalResolve();
                            };
                            
                            try {
                                reader.readAsText(file);
                            } catch (readError) {
                                console.error(`❌ Error al iniciar readAsText: ${file.name}`, readError);
                                if (!resolved) {
                                    resolved = true;
                                    resolve();
                                }
                            }
                        } catch (error) {
                            console.error(`❌ Error procesando archivo ${file.name}:`, error);
                            resolve();
                        }
                    });
                });
                
                // Esperar a que termine este lote antes de continuar con el siguiente
                await Promise.all(batchPromises);
                
                // Pequeña pausa entre lotes para permitir que la UI se actualice
                if (USE_BATCHES && batchIndex < totalBatches - 1) {
                    await new Promise(r => setTimeout(r, 10));
                }
            }
            

            
            // Verificar que haya archivos
            if (window.CodeEditorManager.projectFiles.length === 0) {
                console.error('❌ ERROR: No se cargó ningún archivo');
                alert('❌ Error: No se pudieron cargar los archivos. Revisa la consola para más detalles.');
                
                // Restaurar mensaje inicial
                if (window.CodeEditorManager.fileTreeContent) {
                    window.CodeEditorManager.fileTreeContent.innerHTML = '<div style="padding: 4px 0; color: #666;">Abre un proyecto para ver los archivos</div>';
                }
                return;
            }
            
            // Guardar estructura de árbol
            window.CodeEditorManager.fileTreeStructure = fileTree;
            window.CodeEditorManager.projectName = projectName;
            
            // Renderizar árbol jerárquico
            renderHierarchicalFileTree(fileTree);
        } catch (error) {
            console.error('❌ Error fatal al cargar proyecto:', error);
            alert(`❌ Error al cargar el proyecto: ${error.message}\n\nRevisa la consola para más detalles.`);
            
            // Restaurar mensaje inicial
            if (window.CodeEditorManager.fileTreeContent) {
                window.CodeEditorManager.fileTreeContent.innerHTML = '<div style="padding: 4px 0; color: #666;">Abre un proyecto para ver los archivos</div>';
            }
        }
    };
    
    input.click();
    closeAllMenus();
}

/**
 * Renderizar árbol de archivos jerárquico
 */
function renderHierarchicalFileTree(tree, container = null, level = 0) {
    if (!container) {
        container = window.CodeEditorManager?.fileTreeContent;
        if (!container) return;
        container.innerHTML = '';
    }
    
    const indent = level * 16; // Indentación por nivel
    
    // Ordenar: carpetas primero, luego archivos
    const entries = Object.entries(tree).sort((a, b) => {
        if (a[1].type === 'folder' && b[1].type !== 'folder') return -1;
        if (a[1].type !== 'folder' && b[1].type === 'folder') return 1;
        return a[0].localeCompare(b[0]);
    });
    
    for (const [name, data] of entries) {
        if (data.type === 'folder') {

            
            // Crear carpeta
            const folderDiv = document.createElement('div');
            folderDiv.style.cssText = `padding-left: ${indent}px;`;
            
            const folderHeader = document.createElement('div');
            folderHeader.style.cssText = 'padding: 4px 8px; cursor: pointer; border-radius: 4px; margin: 2px 0; display: flex; align-items: center; gap: 6px; font-weight: 500;';
            folderHeader.innerHTML = `<span>📁</span><span>${name}</span>`;
            
            const childrenContainer = document.createElement('div');
            childrenContainer.style.display = 'none'; // Colapsado por defecto
            
            let isOpen = false;
            
            folderHeader.addEventListener('click', (e) => {
                e.stopPropagation();

                isOpen = !isOpen;
                childrenContainer.style.display = isOpen ? 'block' : 'none';
                folderHeader.querySelector('span:first-child').textContent = isOpen ? '📂' : '📁';
            });
            
            folderHeader.addEventListener('mouseenter', () => {
                folderHeader.style.background = '#e9ecef';
            });
            
            folderHeader.addEventListener('mouseleave', () => {
                folderHeader.style.background = 'transparent';
            });
            
            folderDiv.appendChild(folderHeader);
            folderDiv.appendChild(childrenContainer);
            container.appendChild(folderDiv);
            
            // Renderizar hijos recursivamente
            if (data.children && Object.keys(data.children).length > 0) {

                renderHierarchicalFileTree(data.children, childrenContainer, level + 1);
            } else {

            }
            
        } else {
            // Crear archivo
            const fileDiv = document.createElement('div');
            fileDiv.style.cssText = `padding: 4px 8px 4px ${indent + 24}px; cursor: pointer; border-radius: 4px; margin: 2px 0; display: flex; align-items: center; gap: 6px;`;
            
            // Determinar icono según extensión
            const ext = name.split('.').pop()?.toLowerCase();
            let icon = '📄';
            if (ext === 'py') icon = '🐍';
            else if (ext === 'js') icon = '⚡';
            else if (ext === 'html') icon = '🌐';
            else if (ext === 'css') icon = '🎨';
            else if (ext === 'json') icon = '📋';
            else if (ext === 'md') icon = '📝';
            else if (ext === 'java') icon = '☕';
            else if (ext === 'c' || ext === 'cpp') icon = '⚙️';
            else if (ext === 'xml') icon = '📱';
            
            fileDiv.innerHTML = `<span>${icon}</span><span>${name}</span>`;
            
            fileDiv.addEventListener('mouseenter', () => {
                fileDiv.style.background = '#e9ecef';
            });
            
            fileDiv.addEventListener('mouseleave', () => {
                fileDiv.style.background = 'transparent';
            });
            
            fileDiv.addEventListener('click', async () => {
                // El contenido ya debería estar cargado en data.content
                // Si no está, mostrar mensaje de error
                let content = data.content;
                
                if (!content) {
                    // Buscar en projectFiles por path
                    const projectFile = window.CodeEditorManager?.projectFiles.find(
                        f => f.path === data.fullPath
                    );
                    
                    if (projectFile && projectFile.content) {
                        content = projectFile.content;
                        data.content = content; // Cachear para próxima vez
                    } else {
                        content = '// Error: Contenido no disponible. Intenta abrir el proyecto nuevamente.';
                        console.warn('⚠️ Archivo sin contenido:', data.fullPath);
                    }
                }
                
                // Abrir en editor usando el sistema de pestañas
                if (window.CodeEditorManager) {
                    const filePath = data.fullPath || name;
                    const existingFile = window.CodeEditorManager.openFiles.find(f => f.path === filePath);
                    
                    if (existingFile) {
                        // Si ya está abierto, solo cambiar a esa pestaña
                        window.CodeEditorManager.currentFile = existingFile;
                        window.CodeEditorManager.renderTabs();
                        window.CodeEditorManager.displayFileInEditor(existingFile);
                    } else {
                        // Crear nuevo archivo y agregarlo
                        const newFile = {
                            name: name,
                            path: filePath,
                            type: 'file',
                            content: content
                        };
                        
                        window.CodeEditorManager.openFiles.push(newFile);
                        window.CodeEditorManager.currentFile = newFile;
                        window.CodeEditorManager.renderTabs();
                        window.CodeEditorManager.displayFileInEditor(newFile);
                    }
                    

                }
            });
            
            container.appendChild(fileDiv);
        }
    }
}

/**
 * Guardar proyecto (descargar como ZIP o guardar estado)
 */
function saveProject() {
    if (!window.CodeEditorManager || window.CodeEditorManager.openFiles.length === 0) {
        alert('⚠️ No hay archivos abiertos para guardar');
        return;
    }
    
    // Por ahora, guardamos el estado del proyecto como JSON
    const projectData = {
        name: 'kalin-project',
        timestamp: new Date().toISOString(),
        files: window.CodeEditorManager.openFiles.map(f => ({
            name: f.name,
            path: f.path,
            content: f.content
        }))
    };
    
    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('✅ Proyecto guardado');
    closeAllMenus();
}

/**
 * Cerrar proyecto
 */
function closeProject() {
    if (!window.CodeEditorManager) return;
    
    if (confirm('¿Estás seguro de que deseas cerrar el proyecto? Se perderán los cambios no guardados.')) {
        // Limpiar archivos abiertos
        window.CodeEditorManager.openFiles = [];
        window.CodeEditorManager.currentFile = null;
        window.CodeEditorManager.projectFiles = [];
        window.CodeEditorManager.projectName = null;
        
        // Resetear título del proyecto
        const projectTitleEl = document.getElementById('project-title');
        if (projectTitleEl) {
            projectTitleEl.textContent = 'Sin Proyecto';
        }
        
        // Mostrar placeholder
        window.CodeEditorManager.showPlaceholder();
        
        // Limpiar pestañas
        if (window.CodeEditorManager.fileTabs) {
            window.CodeEditorManager.fileTabs.innerHTML = '';
        }
        
        // Limpiar árbol de archivos
        if (window.CodeEditorManager.fileTreeContent) {
            window.CodeEditorManager.fileTreeContent.innerHTML = '<div style="padding: 4px 0; color: #666;">Abre un proyecto para ver los archivos</div>';
        }
        
        console.log('✅ Proyecto cerrado');
    }
    closeAllMenus();
}

/**
 * Mostrar submenú de Crear Proyecto
 */
function showCreateProjectSubmenu() {
    const submenu = document.getElementById('submenu-create-project');
    if (submenu) {
        submenu.style.display = 'block';
    }
}

/**
 * Ocultar submenú de Crear Proyecto
 */
function hideCreateProjectSubmenu() {
    const submenu = document.getElementById('submenu-create-project');
    if (submenu) {
        // Pequeño delay para permitir mover el mouse al submenú
        setTimeout(() => {
            submenu.style.display = 'none';
        }, 200);
    }
}

/**
 * Crear nuevo proyecto con plantilla
 */
function createProject(language) {
    console.log(`📁 Creando proyecto ${language}...`);
    
    // Plantillas de proyectos por lenguaje
    const templates = {
        python: {
            name: 'python-project',
            files: [
                { path: 'main.py', content: '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\ndef main():\n    print("Hola desde Python!")\n\nif __name__ == "__main__":\n    main()' },
                { path: 'README.md', content: '# Python Project\n\nProyecto Python creado con Kalin.' }
            ]
        },
        javascript: {
            name: 'nodejs-project',
            files: [
                { path: 'index.js', content: '// Node.js Application\n\nconsole.log("Hola desde Node.js!");' },
                { path: 'package.json', content: '{\n  "name": "nodejs-project",\n  "version": "1.0.0",\n  "description": "",\n  "main": "index.js",\n  "scripts": {\n    "start": "node index.js"\n  }\n}' },
                { path: 'README.md', content: '# Node.js Project\n\nProyecto Node.js creado con Kalin.' }
            ]
        },
        html: {
            name: 'web-project',
            files: [
                { path: 'index.html', content: '<!DOCTYPE html>\n<html lang="es">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Mi Web</title>\n    <link rel="stylesheet" href="style.css">\n</head>\n<body>\n    <h1>Hola Mundo!</h1>\n    <script src="script.js"></script>\n</body>\n</html>' },
                { path: 'style.css', content: '/* Estilos principales */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n    background: #f5f5f5;\n}\n\nh1 {\n    color: #333;\n}' },
                { path: 'script.js', content: '// JavaScript principal\nconsole.log("Web cargada correctamente");' },
                { path: 'README.md', content: '# Web Project\n\nProyecto web HTML/CSS/JS creado con Kalin.' }
            ]
        },
        java: {
            name: 'java-project',
            files: [
                { path: 'Main.java', content: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hola desde Java!");\n    }\n}' },
                { path: 'README.md', content: '# Java Project\n\nProyecto Java creado con Kalin.' }
            ]
        },
        c: {
            name: 'c-project',
            files: [
                { path: 'main.c', content: '#include <stdio.h>\n\nint main() {\n    printf("Hola desde C!\\n");\n    return 0;\n}' },
                { path: 'Makefile', content: 'CC=gcc\nCFLAGS=-Wall -g\n\nall: main\n\nmain: main.c\n\t$(CC) $(CFLAGS) -o main main.c\n\nclean:\n\trm -f main' },
                { path: 'README.md', content: '# C Project\n\nProyecto C creado con Kalin.\n\n## Compilar\n```bash\nmake\n```' }
            ]
        },
        cpp: {
            name: 'cpp-project',
            files: [
                { path: 'main.cpp', content: '#include <iostream>\n\nint main() {\n    std::cout << "Hola desde C++!" << std::endl;\n    return 0;\n}' },
                { path: 'README.md', content: '# C++ Project\n\nProyecto C++ creado con Kalin.' }
            ]
        },
        react: {
            name: 'react-app',
            files: [
                { path: 'package.json', content: '{\n  "name": "react-app",\n  "version": "0.1.0",\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0",\n    "react-scripts": "5.0.1"\n  },\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build"\n  }\n}' },
                { path: 'src/App.js', content: 'import React from \'react\';\n\nfunction App() {\n  return (\n    <div className="App">\n      <h1>Hola desde React!</h1>\n    </div>\n  );\n}\n\nexport default App;' },
                { path: 'src/index.js', content: 'import React from \'react\';\nimport ReactDOM from \'react-dom/client\';\nimport App from \'./App\';\n\nconst root = ReactDOM.createRoot(document.getElementById(\'root\'));\nroot.render(<App />);' },
                { path: 'public/index.html', content: '<!DOCTYPE html>\n<html lang="es">\n<head>\n    <meta charset="utf-8" />\n    <title>React App</title>\n</head>\n<body>\n    <div id="root"></div>\n</body>\n</html>' },
                { path: 'README.md', content: '# React App\n\nProyecto React creado con Kalin.\n\n## Ejecutar\n```bash\nnpm start\n```' }
            ]
        },
        android: {
            name: 'android-app',
            files: [
                { path: 'MainActivity.java', content: 'package com.example.myapp;\n\nimport android.app.Activity;\nimport android.os.Bundle;\n\npublic class MainActivity extends Activity {\n    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);\n        setContentView(R.layout.activity_main);\n    }\n}' },
                { path: 'activity_main.xml', content: '<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n    android:layout_width="match_parent"\n    android:layout_height="match_parent"\n    android:orientation="vertical"\n    android:gravity="center">\n\n    <TextView\n        android:layout_width="wrap_content"\n        android:layout_height="wrap_content"\n        android:text="Hola desde Android!"\n        android:textSize="24sp" />\n\n</LinearLayout>' },
                { path: 'AndroidManifest.xml', content: '<?xml version="1.0" encoding="utf-8"?>\n<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n    package="com.example.myapp">\n\n    <application\n        android:allowBackup="true"\n        android:icon="@mipmap/ic_launcher"\n        android:label="@string/app_name">\n        <activity android:name=".MainActivity">\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>\n        </activity>\n    </application>\n\n</manifest>' },
                { path: 'README.md', content: '# Android App\n\nProyecto Android creado con Kalin.' }
            ]
        }
    };
    
    // Obtener plantilla o usar default
    const template = templates[language] || templates.python;
    
    // Crear estructura del proyecto
    const projectFiles = [];
    const fileTree = {};
    
    template.files.forEach(file => {
        const parts = file.path.split('/');
        
        // Construir árbol
        let current = fileTree;
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            if (i === parts.length - 1) {
                current[part] = {
                    type: 'file',
                    fullPath: file.path,
                    name: part,
                    content: file.content
                };
            } else {
                if (!current[part]) {
                    current[part] = { type: 'folder', children: {} };
                }
                current = current[part].children;
            }
        }
        
        // Agregar a lista plana
        projectFiles.push({
            name: parts[parts.length - 1],
            path: file.path,  // Usar el path completo (ej: 'src/App.js')
            type: 'file',
            size: file.content.length,
            content: file.content
        });
    });
    
    // Actualizar estado global
    if (window.CodeEditorManager) {
        window.CodeEditorManager.projectFiles = projectFiles;
        window.CodeEditorManager.fileTreeStructure = fileTree;
        window.CodeEditorManager.projectName = template.name;
        
        // Actualizar UI
        const projectTitleEl = document.getElementById('project-title');
        if (projectTitleEl) {
            projectTitleEl.textContent = '📁 ' + template.name;
        }
        
        // Renderizar árbol
        renderHierarchicalFileTree(fileTree);
        
        // Abrir archivo principal
        const mainFile = projectFiles.find(f => f.path.includes('main') || f.path.includes('index') || f.path.includes('MainActivity'));
        if (mainFile) {
            window.CodeEditorManager.displayGeneratedCode(mainFile.content, mainFile.name);
        }
    }
    
    console.log(`✅ Proyecto ${template.name} creado exitosamente`);
    alert(`✅ Proyecto ${template.name} creado con ${template.files.length} archivos`);
    
    // Cerrar menús
    closeAllMenus();
    hideCreateProjectSubmenu();
}
/**
 * Abrir archivo individual
 */
function openFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.py,.js,.html,.css,.json,.md,.txt,.java,.c,.cpp,.xml';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const content = await file.text();
        if (window.CodeEditorManager) {
            window.CodeEditorManager.displayGeneratedCode(content, file.name);
            
            // Agregar al árbol de archivos
            window.CodeEditorManager.projectFiles.push({
                name: file.name,
                path: file.name,
                type: 'file',
                content: content
            });
            window.CodeEditorManager.renderFileTree();
        }
    };
    
    input.click();
    closeAllMenus();
}

/**
 * Guardar archivo actual
 */
function saveFile() {
    if (!window.CodeEditorManager || !window.CodeEditorManager.currentFile) {
        alert('⚠️ No hay archivo abierto para guardar');
        return;
    }
    
    const file = window.CodeEditorManager.currentFile;
    const blob = new Blob([file.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('✅ Archivo guardado:', file.name);
    closeAllMenus();
}

/**
 * Guardar archivo como...
 */
function saveFileAs() {
    if (!window.CodeEditorManager || !window.CodeEditorManager.codeEditor) {
        alert('⚠️ No hay contenido para guardar');
        return;
    }
    
    const content = window.CodeEditorManager.codeEditor.value;
    const fileName = window.CodeEditorManager.currentFile?.name || 'archivo.txt';
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('✅ Archivo guardado como:', fileName);
    closeAllMenus();
}

/**
 * Cerrar todos los menús desplegables
 */
function closeAllMenus() {
    const submenus = document.querySelectorAll('.dropdown-submenu');
    submenus.forEach(menu => menu.classList.remove('show'));
}

// Verificar que todas las funciones estén disponibles globalmente
console.log('✅ Funciones del menú Archivo registradas:', {
    openProject: typeof openProject === 'function',
    saveProject: typeof saveProject === 'function',
    closeProject: typeof closeProject === 'function',
    openFile: typeof openFile === 'function',
    saveFile: typeof saveFile === 'function',
    saveFileAs: typeof saveFileAs === 'function',
    closeFile: typeof closeFile === 'function',
    copyCode: typeof copyCode === 'function',
    pasteCode: typeof pasteCode === 'function',
    cutCode: typeof cutCode === 'function',
    createProject: typeof createProject === 'function'
});
