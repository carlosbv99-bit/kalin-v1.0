#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar index.html - elimina TODO el código JavaScript inline corrupto
y mantiene solo HTML/CSS limpio + carga de módulos modulares
"""

def clean_index_html():
    input_file = 'templates/index.html'
    output_file = 'templates/index_clean.html'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la línea donde está el cierre </body></html> CORRECTO
    # (después de los scripts modulares)
    html_end_line = None
    
    for i in range(len(lines) - 1, -1, -1):
        if '</html>' in lines[i].strip():
            # Verificar que sea después de los módulos modulares
            if i > 1090:  # Los módulos están alrededor de 1073-1100
                html_end_line = i
                break
    
    if html_end_line is None:
        print("❌ No se encontró </html> válido")
        return False
    
    print(f"✅ Encontrado </html> en línea {html_end_line + 1}")
    
    # Tomar SOLO hasta </html> inclusive
    clean_lines = lines[:html_end_line + 1]
    
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
        print("📝 Ahora ejecuta:")
        print("   Move-Item templates\\index.html templates\\index_old_backup.html")
        print("   Move-Item templates\\index_clean.html templates\\index.html")
    else:
        print("\n❌ Error durante la limpieza")
