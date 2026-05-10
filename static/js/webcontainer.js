/**
 * Kalin Frontend - Módulo de WebContainers
 * Integra StackBlitz WebContainers para ejecutar código Node.js en el navegador
 */

class WebContainerManager {
    constructor() {
        this.webcontainer = null;
        this.initialized = false;
        this.isRunning = false;
        this.currentProcess = null;
        this.outputCallback = null; // Callback para mostrar output
    }

    /**
     * Inicializar WebContainer
     */
    async initialize() {
        if (this.initialized) {
            console.warn('⚠️ WebContainer ya está inicializado');
            return;
        }

        try {
            console.log('🚀 Inicializando WebContainer...');
            
            // Verificar que la API esté disponible
            if (!window.WebContainer) {
                console.warn('⚠️ WebContainer API no disponible. Solo código JavaScript podrá ejecutarse localmente.');
                console.warn('💡 Para Python, el código se mostrará en el editor pero requerirá el backend para ejecución.');
                this.initialized = false;
                return; // No lanzar error, solo advertir
            }

            // Crear instancia de WebContainer
            this.webcontainer = await window.WebContainer.boot();
            
            this.initialized = true;
            console.log('✅ WebContainer inicializado correctamente');
            
            // Configurar sistema de archivos inicial
            await this.setupFileSystem();
            
        } catch (error) {
            console.error('❌ Error inicializando WebContainer:', error);
            console.warn('⚠️ WebContainer no disponible. La ejecución de código JavaScript no estará disponible.');
            this.initialized = false;
        }
    }

    /**
     * Configurar sistema de archivos inicial
     */
    async setupFileSystem() {
        if (!this.webcontainer) return;

        try {
            // Crear estructura básica de proyecto
            await this.webcontainer.fs.mkdir('/project', { recursive: true });
            
            // Crear package.json por defecto
            await this.webcontainer.fs.writeFile('/project/package.json', JSON.stringify({
                name: 'kalin-project',
                version: '1.0.0',
                description: 'Proyecto generado por Kalin AI',
                main: 'index.js',
                scripts: {
                    start: 'node index.js'
                }
            }, null, 2));

            console.log('✅ Sistema de archivos configurado');
        } catch (error) {
            console.error('❌ Error configurando sistema de archivos:', error);
        }
    }

    /**
     * Escribir archivo en WebContainer
     * @param {string} filePath - Ruta del archivo
     * @param {string} content - Contenido del archivo
     */
    async writeFile(filePath, content) {
        if (!this.webcontainer) {
            throw new Error('WebContainer no está inicializado');
        }

        try {
            const fullPath = `/project/${filePath}`;
            await this.webcontainer.fs.writeFile(fullPath, content);
            console.log(`✅ Archivo escrito: ${fullPath}`);
            return true;
        } catch (error) {
            console.error(`❌ Error escribiendo archivo ${filePath}:`, error);
            throw error;
        }
    }

    /**
     * Leer archivo desde WebContainer
     * @param {string} filePath - Ruta del archivo
     * @returns {Promise<string>}
     */
    async readFile(filePath) {
        if (!this.webcontainer) {
            throw new Error('WebContainer no está inicializado');
        }

        try {
            const fullPath = `/project/${filePath}`;
            const content = await this.webcontainer.fs.readFile(fullPath, 'utf-8');
            return content;
        } catch (error) {
            console.error(`❌ Error leyendo archivo ${filePath}:`, error);
            throw error;
        }
    }

    /**
     * Ejecutar comando en WebContainer
     * @param {string} command - Comando a ejecutar (ej: 'npm install', 'node index.js')
     * @param {Function} onOutput - Callback para output en tiempo real
     */
    async runCommand(command, onOutput = null) {
        if (!this.webcontainer) {
            throw new Error('WebContainer no está inicializado');
        }

        if (this.isRunning) {
            throw new Error('Ya hay un proceso en ejecución');
        }

        try {
            console.log(`▶️ Ejecutando comando: ${command}`);
            this.isRunning = true;
            this.outputCallback = onOutput;

            // Dividir comando y argumentos
            const [cmd, ...args] = command.split(' ');

            // Ejecutar proceso
            this.currentProcess = await this.webcontainer.spawn(cmd, args, {
                cwd: '/project'
            });

            // Capturar output
            this.currentProcess.output.pipeTo(new WritableStream({
                write(data) {
                    console.log('OUTPUT:', data);
                    if (onOutput) {
                        onOutput(data);
                    }
                }
            }));

            // Esperar a que termine
            const exitCode = await this.currentProcess.exit;
            this.isRunning = false;
            this.currentProcess = null;

            console.log(`✅ Proceso completado con código: ${exitCode}`);
            return exitCode;

        } catch (error) {
            console.error('❌ Error ejecutando comando:', error);
            this.isRunning = false;
            this.currentProcess = null;
            throw error;
        }
    }

    /**
     * Detener proceso actual
     */
    async stopProcess() {
        if (this.currentProcess) {
            try {
                await this.currentProcess.kill();
                this.isRunning = false;
                this.currentProcess = null;
                console.log('⏹️ Proceso detenido');
            } catch (error) {
                console.error('❌ Error deteniendo proceso:', error);
            }
        }
    }

    /**
     * Instalar dependencias npm
     * @param {Array<string>} packages - Lista de paquetes a instalar
     */
    async installPackages(packages = []) {
        if (packages.length === 0) {
            // Instalar desde package.json
            return await this.runCommand('npm', 'install');
        } else {
            // Instalar paquetes específicos
            return await this.runCommand('npm', 'install', ...packages);
        }
    }

    /**
     * Ejecutar servidor de desarrollo
     * @param {string} entryPoint - Archivo de entrada (ej: 'index.js')
     */
    async runServer(entryPoint = 'index.js') {
        return await this.runCommand('node', entryPoint);
    }

    /**
     * Obtener lista de archivos del proyecto
     * @returns {Promise<Array>}
     */
    async listFiles(dir = '/project') {
        if (!this.webcontainer) {
            throw new Error('WebContainer no está inicializado');
        }

        try {
            const entries = await this.webcontainer.fs.readdir(dir, { withFileTypes: true });
            return entries.map(entry => ({
                name: entry.name,
                path: `${dir}/${entry.name}`,
                isDirectory: entry.isDirectory()
            }));
        } catch (error) {
            console.error('❌ Error listando archivos:', error);
            throw error;
        }
    }

    /**
     * Eliminar archivo
     * @param {string} filePath - Ruta del archivo
     */
    async deleteFile(filePath) {
        if (!this.webcontainer) {
            throw new Error('WebContainer no está inicializado');
        }

        try {
            const fullPath = `/project/${filePath}`;
            await this.webcontainer.fs.rm(fullPath);
            console.log(`🗑️ Archivo eliminado: ${fullPath}`);
            return true;
        } catch (error) {
            console.error(`❌ Error eliminando archivo ${filePath}:`, error);
            throw error;
        }
    }

    /**
     * Mostrar error al usuario
     * @param {string} message - Mensaje de error
     */
    showError(message) {
        if (window.ChatManager) {
            window.ChatManager.addMessage('❌ ' + message, 'assistant');
        } else {
            alert('Error: ' + message);
        }
    }

    /**
     * Verificar estado del WebContainer
     * @returns {Object}
     */
    getStatus() {
        return {
            initialized: this.initialized,
            isRunning: this.isRunning,
            hasProcess: !!this.currentProcess
        };
    }
}

// Exportar como singleton
const webContainerManager = new WebContainerManager();

if (typeof window !== 'undefined') {
    window.WebContainerManager = webContainerManager;
}
