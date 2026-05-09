#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar index.html - elimina código JavaScript inline corrupto
y mantiene solo HTML/CSS limpio + carga de módulos modulares
"""

def clean_index_html():
    input_file = 'templates/index.html'
    output_file = 'templates/index_clean.html'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la línea donde termina el HTML válido (</html>)
    html_end_line = None
    for i, line in enumerate(lines):
        if '</html>' in line.strip():
            html_end_line = i
            break
    
    if html_end_line is None:
        print("❌ No se encontró </html> en el archivo")
        return False
    
    print(f"✅ Encontrado </html> en línea {html_end_line + 1}")
    
    # Tomar solo hasta </html> inclusive
    clean_lines = lines[:html_end_line + 1]
    
    # Verificar que tengamos la sección de módulos modulares
    has_modular_scripts = any('static/js/config.js' in line for line in clean_lines)
    
    if not has_modular_scripts:
        print("⚠️ Advertencia: No se encontraron los scripts modulares")
        # Agregar los módulos modulares antes de </body>
        modular_scripts = """
    <!-- ===== CARGA DE MÓDULOS MODULARES ===== -->
    <!-- Incluye la nueva arquitectura modular de Kalin AI -->
    <!-- Ver static/js/README.md para documentación -->
    
    <!-- 1. Configuración Centralizada -->
    <script src="/static/js/config.js"></script>
    
    <!-- 2. UI Manager (manejo de interfaz y sidebar) -->
    <script src="/static/js/ui-manager.js"></script>
    
    <!-- 3. Módulo de Preview (renderizado seguro) -->
    <script src="/static/js/preview.js"></script>
    
    <!-- 4. Módulo de Chat (comunicación backend) -->
    <script src="/static/js/chat.js"></script>
    
    <!-- 5. Utilidades Android (soporte desarrollo móvil) -->
    <script src="/static/js/android-utils.js"></script>
    
    <!-- 6. Paneles Redimensionables (ajuste de tamaños) -->
    <script src="/static/js/resizable-panels.js"></script>
    
    <!-- 7. Aplicación Principal (coordina todos los módulos) -->
    <script src="/static/js/app.js"></script>
    
    <!-- 8. Compatibilidad Legacy (mantiene funciones existentes temporalmente) -->
    <script src="/static/js/legacy-compat.js"></script>

  </body>
</html>
"""
        # Encontrar </body> y reemplazar hasta </html>
        body_end_idx = None
        for i in range(len(clean_lines) - 1, -1, -1):
            if '</body>' in clean_lines[i].strip():
                body_end_idx = i
                break
        
        if body_end_idx:
            clean_lines = clean_lines[:body_end_idx]
            clean_lines.append(modular_scripts)
    
    # Escribir archivo limpio
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ Archivo limpio creado: {output_file}")
    print(f"   Líneas originales: {len(lines)}")
    print(f"   Líneas limpiadas: {len(clean_lines)}")
    print(f"   Líneas eliminadas: {len(lines) - len(clean_lines)}")
    
    return True

if __name__ == '__main__':
    success = clean_index_html()
    if success:
        print("\n✅ ¡Limpieza completada!")
        print("📝 Revisa templates/index_clean.html y si está correcto, renómbralo a index.html")
    else:
        print("\n❌ Error durante la limpieza")
