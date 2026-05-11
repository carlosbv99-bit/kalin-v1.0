/**
 * Kalin Frontend - Módulo de Renderizado Universal
 * Soporta múltiples lenguajes: Python, Java, C/C++, Android, HTML, etc.
 */

class UniversalRenderer {
    constructor() {
        this.previewFrame = null;
        this.placeholder = null;
        this.outputPanel = null;
        this.currentLanguage = null;
        this.initialized = false;
    }

    /**
     * Inicializar el renderizador
     */
    initialize() {
        if (this.initialized) return;

        console.log('🔧 Initializing UniversalRenderer...');
        
        this.previewFrame = document.getElementById('preview-frame');
        this.placeholder = document.getElementById('preview-placeholder');
        this.outputPanel = document.getElementById('webcontainer-output');
        
        if (!this.previewFrame || !this.placeholder) {
            console.error('❌ Preview elements not found');
            return;
        }

        this.initialized = true;
        console.log('✅ UniversalRenderer initialized');
    }

    /**
     * Detectar lenguaje del código
     * @param {string} code - Código a analizar
     * @returns {string} - Lenguaje detectado
     */
    detectLanguage(code) {
        if (!code) return 'unknown';

        // HTML/CSS/JS
        if (code.includes('<html') || code.includes('<!DOCTYPE') || 
            code.includes('<div') || code.includes('<script')) {
            return 'html';
        }

        // Python
        if (code.includes('import ') || code.includes('def ') || 
            code.includes('class ') || code.includes('print(') ||
            code.includes('turtle') || code.includes('matplotlib')) {
            return 'python';
        }

        // Java
        if (code.includes('public class') || code.includes('public static void main') ||
            code.includes('System.out.println') || code.includes('import java.')) {
            return 'java';
        }

        // C/C++
        if (code.includes('#include') || code.includes('int main(') ||
            code.includes('printf') || code.includes('std::') ||
            code.includes('cout <<')) {
            return code.includes('std::') || code.includes('cout') ? 'cpp' : 'c';
        }

        // Android XML
        if (code.includes('<?xml') && (code.includes('android:') || 
            code.includes('LinearLayout') || code.includes('RelativeLayout'))) {
            return 'android-xml';
        }

        // JavaScript/TypeScript
        if (code.includes('function') || code.includes('const ') || 
            code.includes('let ') || code.includes('=>')) {
            return 'javascript';
        }

        return 'text';
    }

    /**
     * Renderizar código según el lenguaje
     * @param {string} code - Código a renderizar
     * @param {string} language - Lenguaje (opcional, se detecta automáticamente)
     */
    render(code, language = null) {
        if (!this.initialized) {
            this.initialize();
        }

        if (!language) {
            language = this.detectLanguage(code);
        }

        this.currentLanguage = language;
        console.log(`🎨 Rendering ${language} code...`);

        switch (language) {
            case 'html':
                return this.renderHTML(code);
            case 'python':
                return this.renderPython(code);
            case 'java':
                return this.renderJava(code);
            case 'c':
            case 'cpp':
                return this.renderC_CPP(code, language);
            case 'android-xml':
                return this.renderAndroidXML(code);
            case 'javascript':
                return this.renderJavaScript(code);
            default:
                return this.showOutput(code, language);
        }
    }

    /**
     * Renderizar HTML/CSS/JS
     */
    renderHTML(code) {
        if (!window.PreviewManager?.enabled) {
            this.showPlaceholderMessage('💡 Activa el preview para ver el resultado HTML');
            return;
        }

        // Usar el PreviewManager existente para HTML
        if (window.PreviewManager) {
            window.PreviewManager.render(code);
        }
    }

    /**
     * Renderizar Python (simulación visual)
     */
    renderPython(code) {
        // Detectar tipo de código Python
        if (code.includes('turtle')) {
            return this.renderPythonTurtle(code);
        } else if (code.includes('matplotlib') || code.includes('plt.')) {
            return this.renderPythonPlot(code);
        } else {
            // Código Python general - mostrar output simulado
            return this.showOutput(this.simulatePythonOutput(code), 'python');
        }
    }

    /**
     * Simular renderizado de Turtle graphics
     */
    renderPythonTurtle(code) {
        this.hidePreview();
        
        // Crear canvas para simular turtle
        const canvasHTML = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh;
            background: #f5f5f5;
            font-family: Arial, sans-serif;
        }
        .container {
            text-align: center;
        }
        canvas {
            border: 2px solid #333;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .info {
            margin-top: 16px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <canvas id="turtleCanvas" width="600" height="600"></canvas>
        <div class="info">🐍 Simulación de Turtle Graphics (Python)</div>
    </div>
    <script>
        // Simular comandos básicos de turtle
        const canvas = document.getElementById('turtleCanvas');
        const ctx = canvas.getContext('2d');
        
        // Configuración inicial
        ctx.strokeStyle = 'yellow';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        
        let x = 300, y = 300; // Centro
        let angle = 0;
        
        // Funciones básicas de turtle
        function forward(distance) {
            const newX = x + distance * Math.cos(angle * Math.PI / 180);
            const newY = y + distance * Math.sin(angle * Math.PI / 180);
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(newX, newY);
            ctx.stroke();
            x = newX;
            y = newY;
        }
        
        function left(degrees) {
            angle -= degrees;
        }
        
        function right(degrees) {
            angle += degrees;
        }
        
        function color(c) {
            ctx.strokeStyle = c;
        }
        
        // Ejecutar código simulado basado en el patrón detectado
        try {
            // Detección básica de patrones comunes
            ${this.extractTurtleCommands(code)}
            
            console.log('✅ Turtle simulation complete');
        } catch(e) {
            console.error('Error in turtle simulation:', e);
        }
    <\/script>
</body>
</html>`;

        this.previewFrame.srcdoc = canvasHTML;
        this.placeholder.style.display = 'none';
        this.previewFrame.style.display = 'block';
        
        console.log('✅ Python Turtle rendered');
    }

    /**
     * Extraer comandos de turtle del código Python
     */
    extractTurtleCommands(code) {
        const commands = [];
        
        // Buscar tamaño del cuadrado
        const sizeMatch = code.match(/size\s*=\s*(\d+)/);
        const size = sizeMatch ? sizeMatch[1] : 100;
        
        // Buscar color
        const colorMatch = code.match(/color\(["']([^"']+)["']\)/);
        const color = colorMatch ? colorMatch[1] : 'black';
        
        // Generar JavaScript equivalente
        let jsCode = `
            color('${color}');
            for (let i = 0; i < 4; i++) {
                forward(${size});
                left(90);
            }
        `;
        
        return jsCode;
    }

    /**
     * Simular gráficos de matplotlib
     */
    renderPythonPlot(code) {
        this.showOutput('📊 Gráfico de Matplotlib\n\nPara visualizar gráficos de matplotlib,\nejecuta el código en el backend de Python.\n\nEl preview web no puede renderizar matplotlib directamente.', 'python');
    }

    /**
     * Simular ejecución de Java
     */
    renderJava(code) {
        const output = this.simulateJavaOutput(code);
        this.showOutput(output, 'java');
    }

    /**
     * Simular output de Java
     */
    simulateJavaOutput(code) {
        let output = '☕ Java Output Simulation\n';
        output += '═'.repeat(40) + '\n\n';
        
        // Extraer System.out.println statements
        const printlnMatches = code.matchAll(/System\.out\.println\((.*?)\);/g);
        for (const match of printlnMatches) {
            let content = match[1];
            // Limpiar strings
            content = content.replace(/^["']|["']$/g, '');
            // Evaluar expresiones simples
            if (content.includes('+')) {
                // Es una concatenación, mostrar como string
                content = content.replace(/\+/g, ' ');
            }
            output += content + '\n';
        }
        
        if (!printlnMatches || printlnMatches.length === 0) {
            output += '(No hay output para mostrar)\n';
            output += '\n💡 Tip: Agrega System.out.println() para ver output';
        }
        
        output += '\n' + '═'.repeat(40);
        output += '\n⚠️ Esta es una simulación. Para ejecutar código Java real,\nusa el backend con JDK instalado.';
        
        return output;
    }

    /**
     * Simular ejecución de C/C++
     */
    renderC_CPP(code, lang) {
        const output = this.simulateCOutput(code, lang);
        this.showOutput(output, lang);
    }

    /**
     * Simular output de C/C++
     */
    simulateCOutput(code, lang) {
        const language = lang === 'cpp' ? 'C++' : 'C';
        let output = `💻 ${language} Output Simulation\n`;
        output += '═'.repeat(40) + '\n\n';
        
        // Extraer printf/cout statements
        const printfMatches = code.matchAll(/printf\((.*?)\);/g);
        const coutMatches = code.matchAll(/cout\s*<<\s*(.*?);/g);
        
        let hasOutput = false;
        
        for (const match of printfMatches) {
            hasOutput = true;
            let content = match[1];
            content = content.replace(/^["']|["']$/g, '');
            content = content.replace(/\\n/g, '\n');
            output += content + '\n';
        }
        
        for (const match of coutMatches) {
            hasOutput = true;
            let content = match[1];
            content = content.replace(/^["']|["']$/g, '');
            output += content + '\n';
        }
        
        if (!hasOutput) {
            output += '(No hay output para mostrar)\n';
            output += '\n💡 Tip: Agrega printf() o cout para ver output';
        }
        
        output += '\n' + '═'.repeat(40);
        output += `\n⚠️ Esta es una simulación. Para ejecutar código ${language} real,\ncompila y ejecuta con gcc/g++ en el backend.`;
        
        return output;
    }

    /**
     * Renderizar Android XML layout
     */
    renderAndroidXML(code) {
        this.renderAndroidLayout(code);
    }

    /**
     * Simular preview de layout Android
     */
    renderAndroidLayout(xmlCode) {
        this.hidePreview();
        
        // Parsear XML básico y crear representación visual
        const layoutHTML = this.parseAndroidXML(xmlCode);
        
        this.previewFrame.srcdoc = layoutHTML;
        this.placeholder.style.display = 'none';
        this.previewFrame.style.display = 'block';
        
        console.log('✅ Android XML layout rendered');
    }

    /**
     * Parsear Android XML y generar HTML visual
     */
    parseAndroidXML(xmlCode) {
        // Extraer tipo de layout
        let layoutType = 'LinearLayout';
        if (xmlCode.includes('RelativeLayout')) layoutType = 'RelativeLayout';
        else if (xmlCode.includes('ConstraintLayout')) layoutType = 'ConstraintLayout';
        
        // Extraer elementos UI básicos
        const buttons = (xmlCode.match(/<Button/g) || []).length;
        const texts = (xmlCode.match(/<TextView/g) || []).length;
        const inputs = (xmlCode.match(/<EditText/g) || []).length;
        const images = (xmlCode.match(/<ImageView/g) || []).length;
        
        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #e0e0e0;
            font-family: Roboto, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .device-frame {
            width: 360px;
            height: 640px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            padding: 20px;
            overflow: auto;
            position: relative;
        }
        .status-bar {
            height: 24px;
            background: #2196F3;
            margin: -20px -20px 16px -20px;
            border-radius: 20px 20px 0 0;
        }
        .layout-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 8px;
        }
        .ui-element {
            padding: 12px 16px;
            border-radius: 4px;
            font-size: 14px;
            text-align: center;
        }
        .button {
            background: #2196F3;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .textview {
            background: #f5f5f5;
            color: #333;
            text-align: left;
        }
        .edittext {
            background: white;
            border: 1px solid #ddd;
            text-align: left;
        }
        .imageview {
            background: #e0e0e0;
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
        }
        .info {
            margin-top: 16px;
            padding: 12px;
            background: #fff9c4;
            border-left: 4px solid #fbc02d;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="device-frame">
        <div class="status-bar"></div>
        <div class="layout-container">
            ${this.generateUIElements(buttons, texts, inputs, images)}
        </div>
        <div class="info">
            📱 Android Layout Preview<br>
            Tipo: ${layoutType}<br>
            Elementos: ${buttons} Button(s), ${texts} TextView(s), ${inputs} EditText(s), ${images} ImageView(s)
        </div>
    </div>
</body>
</html>`;
    }

    /**
     * Generar elementos UI simulados
     */
    generateUIElements(buttons, texts, inputs, images) {
        let html = '';
        
        for (let i = 0; i < texts; i++) {
            html += '<div class="ui-element textview">TextView ' + (i + 1) + '</div>\n';
        }
        
        for (let i = 0; i < buttons; i++) {
            html += '<div class="ui-element button">Button ' + (i + 1) + '</div>\n';
        }
        
        for (let i = 0; i < inputs; i++) {
            html += '<div class="ui-element edittext">EditText ' + (i + 1) + '</div>\n';
        }
        
        for (let i = 0; i < images; i++) {
            html += '<div class="ui-element imageview">🖼️ Image ' + (i + 1) + '</div>\n';
        }
        
        if (html === '') {
            html = '<div style="text-align: center; color: #999; padding: 40px;">No se detectaron elementos UI</div>';
        }
        
        return html;
    }

    /**
     * Renderizar JavaScript
     */
    renderJavaScript(code) {
        // Si WebContainer está disponible, usarlo
        if (window.WebContainerManager?.initialized) {
            this.showOutput('▶️ Ejecutando JavaScript con WebContainer...\n(Ver terminal output)', 'javascript');
            // La ejecución real se maneja por WebContainerManager
        } else {
            // Fallback: mostrar código
            this.showOutput('⚠️ WebContainer no disponible\n\nPara ejecutar JavaScript, necesitas:\n1. Conexión a internet\n2. Navegador compatible\n\nEl código se muestra en el editor.', 'javascript');
        }
    }

    /**
     * Mostrar output en panel de terminal
     */
    showOutput(output, language) {
        this.hidePreview();
        
        if (!this.outputPanel) {
            console.warn('⚠️ Output panel not found');
            return;
        }
        
        const outputContent = document.getElementById('output-content');
        if (outputContent) {
            outputContent.textContent = output;
        }
        
        // MOSTRAR el panel automáticamente para Python y otros lenguajes
        this.outputPanel.style.display = 'flex';
        
        console.log(`✅ ${language} output displayed`);
    }

    /**
     * Simular output de Python general
     */
    simulatePythonOutput(code) {
        let output = '🐍 Python Output Simulation\n';
        output += '═'.repeat(50) + '\n\n';
        
        // Extraer print statements
        const printMatches = code.matchAll(/print\((.*?)\)/g);
        let hasOutput = false;
        let outputs = [];
        
        for (const match of printMatches) {
            hasOutput = true;
            let content = match[1];
            // Limpiar comillas y f-strings
            content = content.replace(/^f?["']|["']$/g, '');
            // Manejar concatenación básica
            content = content.replace(/\s*\+\s*/g, ' ');
            outputs.push(content);
        }
        
        if (hasOutput) {
            output += outputs.join('\n');
        } else {
            output += '(No hay print() statements detectados)\n';
            
            // Detectar qué hace el código
            if (code.includes('def ')) {
                const functions = code.match(/def\s+(\w+)\s*\(/g);
                if (functions) {
                    output += '\n📋 Funciones definidas:\n';
                    functions.forEach(f => {
                        const funcName = f.match(/def\s+(\w+)/)[1];
                        output += `  - ${funcName}()\n`;
                    });
                }
            }
            
            if (code.includes('class ')) {
                const classes = code.match(/class\s+(\w+)/g);
                if (classes) {
                    output += '\n📦 Clases definidas:\n';
                    classes.forEach(c => {
                        const className = c.match(/class\s+(\w+)/)[1];
                        output += `  - ${className}\n`;
                    });
                }
            }
            
            output += '\n💡 Tip: Agrega print() para ver output en consola';
        }
        
        output += '\n' + '═'.repeat(50);
        output += '\n⚠️ Esta es una simulación estática del código.';
        output += '\n💡 Para ejecutar Python real, usa el terminal o un IDE.';
        
        return output;
    }

    /**
     * Mostrar mensaje en placeholder
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
}

// Exportar como singleton
const universalRenderer = new UniversalRenderer();

if (typeof window !== 'undefined') {
    window.UniversalRenderer = universalRenderer;
}
