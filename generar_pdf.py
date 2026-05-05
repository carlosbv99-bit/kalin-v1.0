from fpdf import FPDF

class InformePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 33, 33)
        self.cell(0, 10, 'Informe Tecnico - Agente-IA2', new_x='LMARGIN', new_y='NEXT', align='C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 5, 'Sistema Autonomo de Desarrollo con IA', new_x='LMARGIN', new_y='NEXT', align='C')
        self.ln(5)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', new_x='LMARGIN', new_y='NEXT', align='C')
    
    def chapter_title(self, num, label):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f'{num}. {label}', new_x='LMARGIN', new_y='NEXT', align='L', fill=True)
        self.ln(4)
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(51, 51, 51)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT', align='L')
        self.ln(2)
    
    def section_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, body)
        self.ln(3)
    
    def add_code_block(self, code):
        self.set_fill_color(245, 245, 245)
        self.set_font('Courier', '', 9)
        self.multi_cell(0, 5, code)
        self.ln(3)

def generar_informe():
    pdf = InformePDF()
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    
    # Título principal
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, 'INFORME TECNICO DEL PROYECTO', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Agente-IA2 - Sistema Autonomo de Desarrollo con IA', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)
    
    # Metadatos
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 6, 'Fecha: 5 de mayo, 2026', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.cell(0, 6, 'Ubicacion: E:\\agente', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.cell(0, 6, 'Version: 1.0', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(10)
    
    # Sección 1
    pdf.chapter_title('1', 'DESCRIPCION GENERAL')
    
    pdf.section_title('1.1 Proposito del Proyecto')
    pdf.section_body(
        "Agente-IA2 es un sistema autonomo de asistencia en desarrollo de "
        "software basado en Inteligencia Artificial. Permite analizar, reparar, "
        "generar y refactorizar codigo de forma automatica mediante el uso de "
        "multiples proveedores de LLM (Large Language Models)."
    )
    
    pdf.section_title('1.2 Casos de Uso Principales')
    pdf.section_body(
        "- Reparacion automatica de errores en codigo\n"
        "- Generacion de codigo desde requerimientos en lenguaje natural\n"
        "- Analisis estatico de archivos y proyectos\n"
        "- Refactorizacion inteligente de codigo existente\n"
        "- Escaneo estructural de proyectos completos"
    )
    
    # Sección 2
    pdf.chapter_title('2', 'ARQUITECTURA DEL SISTEMA')
    
    pdf.section_title('2.1 Stack Tecnologico')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    col_width = 90
    row_height = 7
    
    pdf.cell(col_width, row_height, 'Componente', border=1, align='L', fill=True)
    pdf.cell(col_width, row_height, 'Tecnologia', border=1, align='L', fill=True)
    pdf.ln()
    
    datos = [
        ["Backend Web", "Flask + Flask-CORS"],
        ["API Alternativa", "FastAPI + Pydantic"],
        ["Lenguaje Base", "Python 3.x"],
        ["LLM Local", "Ollama (DeepSeek Coder)"],
        ["LLM Cloud", "OpenAI GPT-4"],
        ["LLM Fallback", "Anthropic Claude 3.5"]
    ]
    
    pdf.set_font('Helvetica', '', 10)
    for item in datos:
        pdf.cell(col_width, row_height, item[0], border=1, align='L')
        pdf.cell(col_width, row_height, item[1], border=1, align='L')
        pdf.ln()
    
    pdf.ln(5)
    
    # Sección 3
    pdf.chapter_title('3', 'COMPONENTES PRINCIPALES')
    
    pdf.section_title('3.1 Sistema de Deteccion de Intenciones (brain.py)')
    pdf.section_body(
        "Funcion: Analiza el mensaje del usuario y determina la accion a realizar.\n\n"
        "Intenciones soportadas:\n"
        "- fix - Reparar codigo\n"
        "- create - Generar nuevo codigo\n"
        "- scan - Escanear proyecto\n"
        "- analyze - Analizar archivo\n"
        "- refactor - Refactorizar codigo\n"
        "- setpath - Configurar ruta\n"
        "- apply - Aplicar cambios pendientes\n"
        "- help - Mostrar ayuda\n"
        "- chat - Conversacion general"
    )
    
    pdf.section_title('3.2 Executor (executor.py)')
    pdf.section_body(
        "Funcion: Implementa la logica especifica para cada intencion.\n\n"
        "Caracteristicas clave:\n"
        "- Modo seguro activado por defecto (requiere /apply)\n"
        "- Busqueda inteligente de archivos\n"
        "- Validacion de codigo generado\n"
        "- Generacion de diffs para revision\n"
        "- Backup automatico antes de cambios"
    )
    
    pdf.section_title('3.3 State Manager (state_manager.py)')
    pdf.section_body(
        "Proposito: Mantener estado persistente entre requests.\n\n"
        "Datos gestionados:\n"
        "- Ruta del proyecto activo\n"
        "- Ultimo archivo procesado\n"
        "- Ultimo fix pendiente de aplicar\n"
        "- Estadisticas de exito/fallo"
    )
    
    pdf.section_title('3.4 Retry Engine (retry_engine.py)')
    pdf.section_body(
        "Funcionalidad: Sistema de reintentos con tolerancia a fallos.\n\n"
        "Estrategia:\n"
        "- Reintentos automaticos ante fallos de LLM\n"
        "- Backoff exponencial\n"
        "- Cambio de proveedor en caso de error persistente"
    )
    
    # Sección 4
    pdf.chapter_title('4', 'SISTEMA MULTI-LLM')
    
    pdf.section_title('4.1 Proveedores Configurados')
    pdf.section_body(
        "Proveedor: Ollama\n"
        "Tipo: Local | Modelo: deepseek-coder | Costo: $0/mes\n\n"
        "Proveedor: OpenAI\n"
        "Tipo: Cloud | Modelo: gpt-4-turbo | Costo: $0.03/1K tokens\n\n"
        "Proveedor: Anthropic\n"
        "Tipo: Cloud | Modelo: claude-3.5-sonnet | Costo: $0.015/1K tokens"
    )
    
    pdf.section_title('4.2 Routing Inteligente')
    pdf.section_body(
        "Casos de uso definidos:\n"
        "- fix -> Prioriza precision (Claude/GPT-4)\n"
        "- create -> Prioriza creatividad (GPT-4)\n"
        "- enhance -> Prioriza calidad (Claude)\n"
        "- design -> Prioriza arquitectura (GPT-4)\n\n"
        "Estrategia de fallback:\n"
        "1. Intenta proveedor primario para el use_case\n"
        "2. Si falla -> prueba siguiente en lista\n"
        "3. Si todos fallan -> retorna None con error"
    )
    
    # Sección 5
    pdf.chapter_title('5', 'ENDPOINTS DE API')
    
    pdf.section_title('5.1 Flask Server (web.py:5000)')
    pdf.section_body(
        "GET /\n"
        "  Descripcion: Interfaz web principal\n\n"
        "GET /help\n"
        "  Descripcion: Lista de comandos disponibles\n\n"
        "GET /health\n"
        "  Descripcion: Estado del servidor y LLMs\n\n"
        "GET /llm-status\n"
        "  Descripcion: Estado detallado de proveedores LLM\n\n"
        "POST /chat\n"
        "  Descripcion: Endpoint principal para comandos"
    )
    
    # Sección 6
    pdf.chapter_title('6', 'COMANDOS DISPONIBLES')
    
    comandos = [
        ("/setpath <ruta>", "Configura la ruta del proyecto"),
        ("/scan", "Escanea la estructura del proyecto"),
        ("/fix <archivo>", "Repara errores en un archivo"),
        ("/apply", "Aplica cambios pendientes"),
        ("/analyze <archivo>", "Analiza un archivo especifico"),
        ("/create <req>", "Genera codigo desde descripcion"),
        ("/refactor <archivo>", "Refactoriza codigo")
    ]
    
    for comando, desc in comandos:
        pdf.set_font('Courier', 'B', 11)
        pdf.cell(0, 7, comando, new_x='LMARGIN', new_y='NEXT', align='L')
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 7, f"  -> {desc}", new_x='LMARGIN', new_y='NEXT', align='L')
        pdf.ln(1)
    
    # Sección 7
    pdf.chapter_title('7', 'CONFIGURACION')
    
    pdf.section_title('7.1 Variables de Entorno para Desarrollo')
    codigo_env = "AGENTE_MODE=local\nOLLAMA_ENDPOINT=http://127.0.0.1:11434\nOLLAMA_MODEL=deepseek-coder"
    pdf.add_code_block(codigo_env)
    
    pdf.section_title('7.2 Variables de Entorno para Produccion')
    codigo_prod = "AGENTE_MODE=cloud\nOPENAI_API_KEY=sk-proj-xxxxxxxxxxxx\nOPENAI_MODEL=gpt-4-turbo\nANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx"
    pdf.add_code_block(codigo_prod)
    
    pdf.section_title('7.3 Ejecucion')
    codigo_run = "# Activar entorno virtual\n.venv\\Scripts\\Activate.ps1\n\n# Ejecutar servidor\npython run.py\n\n# Servidor disponible en:\n# http://localhost:5000"
    pdf.add_code_block(codigo_run)
    
    # Sección 8
    pdf.chapter_title('8', 'ESTRUCTURA DE ARCHIVOS')
    
    pdf.section_body(
        "E:\\agente\\\n"
        "|\n"
        "+-- agent/\n"
        "|   +-- core/          # Componentes centrales\n"
        "|   |   +-- brain.py\n"
        "|   |   +-- orchestrator.py\n"
        "|   |   +-- state_manager.py\n"
        "|   |   +-- retry_engine.py\n"
        "|   |   +-- project_analyzer.py\n"
        "|   |\n"
        "|   +-- llm/           # Sistema multi-LLM\n"
        "|   |   +-- client.py\n"
        "|   |   +-- provider_manager.py\n"
        "|   |   +-- providers/\n"
        "|   |\n"
        "|   +-- actions/       # Acciones ejecutables\n"
        "|       +-- executor.py\n"
        "|       +-- strategies/\n"
        "|       +-- tools/\n"
        "|\n"
        "+-- web.py             # Servidor Flask principal\n"
        "+-- main.py            # API FastAPI alternativa\n"
        "+-- run.py             # Script de inicio\n"
        "+-- .env.example       # Configuracion de ejemplo"
    )
    
    # Sección 9
    pdf.chapter_title('9', 'ANALISIS DE COSTOS')
    
    pdf.section_title('9.1 Estimacion de Costos Mensuales')
    pdf.section_body(
        "Escenario: 1000 requests/mes, 500 tokens promedio por request\n\n"
        "Ollama (local):      $0/mes\n"
        "OpenAI GPT-4 Turbo:  $15/mes\n"
        "Anthropic Claude:    $7.50/mes\n"
        "HuggingFace Llama:   $0.50/mes"
    )
    
    pdf.section_title('9.2 Recomendacion de Optimizacion')
    pdf.section_body(
        "Para desarrollo:\n"
        "- Usar Ollama exclusivamente -> $0/mes\n\n"
        "Para produccion:\n"
        "- 80% requests a Ollama (casos simples)\n"
        "- 15% requests a Anthropic (casos complejos)\n"
        "- 5% requests a OpenAI (casos criticos)\n"
        "- Costo estimado: ~$2-3/mes"
    )
    
    # Sección 10
    pdf.chapter_title('10', 'PROBLEMAS CONOCIDOS')
    
    pdf.section_body(
        "1. Codigo duplicado en web.py (lineas 241-244)\n\n"
        "2. Monkey-patch inusual en run.py (lineas 1-8)\n\n"
        "3. README vacio - falta documentacion de usuario\n\n"
        "4. Implementacion simplificada de diffs\n\n"
        "5. Falta archivo .env configurado\n\n"
        "6. Sin autenticacion en API\n\n"
        "7. Sin rate limiting\n\n"
        "8. Sin persistencia de estado entre reinicios"
    )
    
    # Sección 11
    pdf.chapter_title('11', 'RECOMENDACIONES DE MEJORA')
    
    pdf.section_title('11.1 Corto Plazo (Critico)')
    pdf.section_body(
        "- Eliminar codigo duplicado en web.py\n"
        "- Remover monkey-patch innecesario en run.py\n"
        "- Completar README con guia de usuario\n"
        "- Crear script de instalacion automatizado\n"
        "- Agregar logging estructurado"
    )
    
    pdf.section_title('11.2 Mediano Plazo (Importante)')
    pdf.section_body(
        "- Implementar autenticacion JWT para API\n"
        "- Agregar rate limiting por IP/usuario\n"
        "- Persistir estado en base de datos\n"
        "- Mejorar parser de diffs\n"
        "- Agregar tests unitarios (pytest)"
    )
    
    # Sección 12
    pdf.chapter_title('12', 'CONCLUSION')
    
    pdf.section_body(
        "Agente-IA2 es un sistema prometedor con arquitectura solida y modular. "
        "Su mayor fortaleza es el sistema multi-LLM con fallback automatico, "
        "que garantiza disponibilidad incluso cuando proveedores cloud fallan.\n\n"
        "Puntos fuertes:\n"
        "- Diseño escalable y extensible\n"
        "- Seguridad con modo seguro por defecto\n"
        "- Flexibilidad en proveedores LLM\n"
        "- Analisis contextual de proyectos\n\n"
        "Areas a mejorar:\n"
        "- Documentacion incompleta\n"
        "- Falta de tests automatizados\n"
        "- Ausencia de autenticacion\n"
        "- Codigo duplicado y patches innecesarios\n\n"
        "Recomendacion final:\n"
        "El proyecto esta listo para uso en desarrollo local con Ollama. "
        "Para deployment en produccion, se recomienda implementar las mejoras "
        "de seguridad y estabilidad listadas en la seccion 11."
    )
    
    # Guardar PDF
    nombre_archivo = 'INFORME_PROYECTO.pdf'
    pdf.output(nombre_archivo)
    print(f"\n✅ PDF generado exitosamente!")
    print(f"📄 Archivo: {nombre_archivo}")
    print(f"📍 Ubicacion: E:\\agente\\{nombre_archivo}")
    print(f"\n¡Abre el archivo PDF con cualquier visor de PDF!")

if __name__ == '__main__':
    print("Generando informe PDF...")
    generar_informe()
