/**
 * Kalin Frontend - Módulo de Utilidades Android
 * Funciones específicas para soporte de desarrollo Android
 */

class AndroidUtils {
    constructor() {
        this.supportedComponents = window.AppConfig?.ANDROID_COMPONENTS || {};
    }

    /**
     * Detectar si el mensaje es una solicitud de componente Android
     * @param {string} message - Mensaje del usuario
     * @returns {Object|null} - { type, name } o null
     */
    detectAndroidComponentRequest(message) {
        const lowerMessage = message.toLowerCase();

        // Mapeo de keywords a tipos de componentes
        const componentPatterns = {
            'activity': ['actividad', 'activity'],
            'fragment': ['fragment', 'fragmento'],
            'adapter': ['adapter', 'adaptador', 'recyclerview', 'recycler view'],
            'custom_view': ['custom view', 'vista personalizada', 'view personalizado'],
            'service': ['service', 'servicio', 'background service'],
            'broadcast_receiver': ['broadcast receiver', 'receiver', 'receptor']
        };

        // Buscar tipo de componente
        let componentType = null;
        for (const [type, keywords] of Object.entries(componentPatterns)) {
            if (keywords.some(keyword => lowerMessage.includes(keyword))) {
                componentType = type;
                break;
            }
        }

        if (!componentType) return null;

        // Extraer nombre del componente
        const componentName = this.extractComponentName(message);

        return {
            type: componentType,
            name: componentName || this.generateDefaultName(componentType)
        };
    }

    /**
     * Extraer nombre del componente del mensaje
     * @param {string} message - Mensaje del usuario
     * @returns {string|null}
     */
    extractComponentName(message) {
        const patterns = [
            /llamada\s+(\w+)/i,
            /named\s+(\w+)/i,
            /llamado\s+(\w+)/i,
            /con nombre\s+(\w+)/i,
            /para\s+(\w+)/i
        ];

        for (const pattern of patterns) {
            const match = message.match(pattern);
            if (match && match[1]) {
                // Capitalizar primera letra
                return match[1].charAt(0).toUpperCase() + match[1].slice(1);
            }
        }

        return null;
    }

    /**
     * Generar nombre por defecto para componente
     * @param {string} type - Tipo de componente
     * @returns {string}
     */
    generateDefaultName(type) {
        const suffixes = {
            'activity': 'Activity',
            'fragment': 'Fragment',
            'adapter': 'Adapter',
            'custom_view': 'View',
            'service': 'Service',
            'broadcast_receiver': 'Receiver'
        };

        return `My${suffixes[type] || 'Component'}`;
    }

    /**
     * Formatear reporte de validación Android
     * @param {Object} report - Reporte de validación
     * @returns {string}
     */
    formatValidationReport(report) {
        if (!report) return '';

        let formatted = '\n📊 REPORTE DE VALIDACIÓN ANDROID\n';
        formatted += '='.repeat(80) + '\n';

        if (report.errors && report.errors.length > 0) {
            formatted += `\n❌ ERRORES (${report.errors.length}):\n`;
            report.errors.forEach((error, i) => {
                formatted += `  ${i + 1}. ${error}\n`;
            });
        }

        if (report.warnings && report.warnings.length > 0) {
            formatted += `\n⚠️ ADVERTENCIAS (${report.warnings.length}):\n`;
            report.warnings.forEach((warning, i) => {
                formatted += `  ${i + 1}. ${warning}\n`;
            });
        }

        if (report.suggestions && report.suggestions.length > 0) {
            formatted += `\n💡 SUGERENCIAS (${report.suggestions.length}):\n`;
            report.suggestions.forEach((suggestion, i) => {
                formatted += `  ${i + 1}. ${suggestion}\n`;
            });
        }

        const totalIssues = (report.errors?.length || 0) + 
                           (report.warnings?.length || 0) + 
                           (report.suggestions?.length || 0);

        formatted += `\n📊 Total: ${totalIssues} issues encontrados\n`;

        return formatted;
    }

    /**
     * Detectar lenguaje de archivo Android
     * @param {string} filename - Nombre del archivo
     * @returns {string} - 'java', 'kotlin', 'xml', 'manifest'
     */
    detectAndroidFileType(filename) {
        if (filename.endsWith('.java')) return 'java';
        if (filename.endsWith('.kt')) return 'kotlin';
        if (filename.endsWith('.xml') && filename.includes('layout')) return 'xml';
        if (filename.toLowerCase().includes('manifest')) return 'manifest';
        return 'unknown';
    }

    /**
     * Verificar si el código es Android
     * @param {string} code - Código a verificar
     * @returns {boolean}
     */
    isAndroidCode(code) {
        const androidIndicators = [
            'import android.',
            'extends Activity',
            'extends Fragment',
            'extends Service',
            'android:id=',
            'xmlns:android=',
            'R.layout.',
            'R.id.',
            '@Override',
            'onCreate(',
            'setContentView('
        ];

        return androidIndicators.some(indicator => code.includes(indicator));
    }

    /**
     * Obtener icono para tipo de componente
     * @param {string} type - Tipo de componente
     * @returns {string}
     */
    getComponentIcon(type) {
        const icons = {
            'activity': '📱',
            'fragment': '🧩',
            'adapter': '📋',
            'custom_view': '🎨',
            'service': '⚙️',
            'broadcast_receiver': '📡'
        };

        return icons[type] || '📦';
    }

    /**
     * Crear snippet de código con syntax highlighting básico
     * @param {string} code - Código
     * @param {string} language - Lenguaje
     * @returns {string} - HTML con highlighting
     */
    createCodeSnippet(code, language) {
        const escaped = this.escapeHTML(code);
        
        // Syntax highlighting básico (puede mejorarse con Prism.js o highlight.js)
        let highlighted = escaped;

        if (language === 'java' || language === 'kotlin') {
            // Resaltar keywords
            const keywords = ['public', 'private', 'protected', 'class', 'void', 'int', 'String', 'import', 'package'];
            keywords.forEach(keyword => {
                const regex = new RegExp(`\\b${keyword}\\b`, 'g');
                highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`);
            });
        }

        return `<pre class="code-snippet"><code class="language-${language}">${highlighted}</code></pre>`;
    }

    /**
     * Escapar HTML
     * @param {string} html - HTML a escapar
     * @returns {string}
     */
    escapeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
}

// Exportar como singleton
const androidUtils = new AndroidUtils();

if (typeof window !== 'undefined') {
    window.AndroidUtils = androidUtils;
}
