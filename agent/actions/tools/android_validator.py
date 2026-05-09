"""
Android Syntax Validator - Validador de sintaxis básico para Android

Detecta errores comunes en:
- Archivos Java/Kotlin (imports, clases, métodos)
- Layouts XML (tags, atributos, estructura)
- AndroidManifest.xml (declaraciones, permisos)

Uso:
    from agent.actions.tools.android_validator import validate_android_code
    
    errors = validate_android_code("java", codigo_java)
    # Retorna lista de errores encontrados
"""

import re
from typing import List, Dict, Tuple


class AndroidSyntaxValidator:
    """Validador de sintaxis básico para código Android"""
    
    def __init__(self):
        self.java_keywords = {
            'public', 'private', 'protected', 'static', 'final', 'class',
            'interface', 'extends', 'implements', 'import', 'package',
            'void', 'int', 'String', 'boolean', 'float', 'double', 'long',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'return', 'try', 'catch', 'finally', 'throw', 'throws',
            'new', 'this', 'super', 'null', 'true', 'false'
        }
        
        self.android_components = {
            'Activity', 'Fragment', 'Service', 'BroadcastReceiver',
            'ContentProvider', 'View', 'ViewGroup', 'Context',
            'Intent', 'Bundle', 'SharedPreferences', 'TextView',
            'Button', 'EditText', 'ImageView', 'RecyclerView',
            'ListView', 'GridView', 'ScrollView', 'LinearLayout',
            'RelativeLayout', 'ConstraintLayout', 'FrameLayout'
        }
    
    def validate(self, language: str, code: str) -> Dict[str, List[str]]:
        """
        Validar código Android
        
        Args:
            language: 'java', 'kotlin', 'xml', 'manifest'
            code: Código a validar
            
        Returns:
            Diccionario con {'errors': [...], 'warnings': [...], 'suggestions': [...]}
        """
        result = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if language.lower() in ['java', 'kotlin']:
            result = self._validate_java_kotlin(code, language.lower())
        elif language.lower() == 'xml':
            result = self._validate_xml_layout(code)
        elif language.lower() == 'manifest':
            result = self._validate_manifest(code)
        
        return result
    
    def _validate_java_kotlin(self, code: str, language: str) -> Dict[str, List[str]]:
        """Validar código Java o Kotlin"""
        errors = []
        warnings = []
        suggestions = []
        
        lines = code.split('\n')
        
        # 1. Verificar package declaration
        if not any('package ' in line for line in lines[:5]):
            errors.append("Falta declaración de package al inicio del archivo")
        
        # 2. Verificar imports básicos para Android
        has_imports = any('import ' in line for line in lines)
        if not has_imports and any(comp in code for comp in ['Activity', 'Fragment', 'View']):
            warnings.append("No se encontraron imports. ¿Faltan imports de Android?")
        
        # 3. Verificar clase principal
        class_pattern = r'(?:public\s+)?class\s+(\w+)'
        classes = re.findall(class_pattern, code)
        
        if not classes:
            errors.append("No se encontró declaración de clase")
        else:
            class_name = classes[0]
            
            # Verificar que el nombre de clase coincida con el archivo (si es Activity/Fragment)
            if any(comp in code for comp in ['extends Activity', 'extends AppCompatActivity']):
                if not class_name.endswith('Activity'):
                    suggestions.append(f"Convención: Las Activities suelen terminar en 'Activity'. Considera renombrar '{class_name}' a '{class_name}Activity'")
            
            if any(comp in code for comp in ['extends Fragment']):
                if not class_name.endswith('Fragment'):
                    suggestions.append(f"Convención: Los Fragments suelen terminar en 'Fragment'. Considera renombrar '{class_name}' a '{class_name}Fragment'")
        
        # 4. Verificar método onCreate (para Activities/Fragments)
        if any(comp in code for comp in ['extends Activity', 'extends AppCompatActivity', 'extends Fragment']):
            if 'onCreate' not in code:
                errors.append("Falta método onCreate() requerido para Activities/Fragments")
            elif 'setContentView' not in code and 'extends Activity' in code:
                warnings.append("Activity sin setContentView() - no tendrá UI")
        
        # 5. Verificar balance de llaves {}
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Desequilibrio de llaves: {open_braces} abiertas, {close_braces} cerradas")
        
        # 6. Verificar puntos y coma faltantes (básico)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Ignorar comentarios, líneas vacías, declaraciones de clase/método
            if (not stripped or 
                stripped.startswith('//') or 
                stripped.startswith('/*') or
                stripped.startswith('*') or
                stripped.endswith('{') or
                stripped.endswith('}') or
                any(kw in stripped for kw in ['class ', 'interface ', 'public ', 'private ', 'protected ', 'import ', 'package '])):
                continue
            
            # Verificar sentencias que deberían terminar en ;
            if (any(stripped.endswith(keyword) for keyword in [')', '++', '--']) and
                not stripped.endswith(';') and
                not stripped.startswith('if ') and
                not stripped.startswith('for ') and
                not stripped.startswith('while ') and
                'return ' not in stripped and
                'throw ' not in stripped):
                
                # Excepciones comunes
                if not any(exc in stripped for exc in ['@Override', '@SuppressLint', 'Log.', 'System.out']):
                    warnings.append(f"Línea {i}: Posible punto y coma faltante")
        
        # 7. Verificar findViewById sin cast (Android antiguo)
        if 'findViewById' in code and 'R.id.' in code:
            if '<' not in code:  # No tiene generics (findViewById<T>)
                warnings.append("findViewById sin type casting. Considera usar findViewById<Type>() o View Binding")
        
        # 8. Verificar uso de deprecated APIs
        deprecated_patterns = [
            (r'new\s+AsyncTask', 'AsyncTask está deprecated desde API 30. Usa Coroutines o Executor'),
            (r'\.startActivityForResult\(', 'startActivityForResult está deprecated. Usa Activity Result API'),
            (r'getFragmentManager\(\)', 'getFragmentManager() puede causar problemas. Usa getSupportFragmentManager()'),
        ]
        
        for pattern, message in deprecated_patterns:
            if re.search(pattern, code):
                warnings.append(f"API deprecated: {message}")
        
        # 9. Verificar manejo de nulls básico
        if 'getString(' in code or 'findViewById(' in code:
            if '.toString()' in code and 'null' not in code and '?' not in code:
                suggestions.append("Considera verificar null antes de llamar .toString()")
        
        # 10. Verificar imports duplicados
        import_lines = [line.strip() for line in lines if line.strip().startswith('import ')]
        if len(import_lines) != len(set(import_lines)):
            warnings.append("Se encontraron imports duplicados")
        
        # 11. Sugerir uso de constants para strings hardcodeados
        string_literals = re.findall(r'"[^"]{10,}"', code)
        if len(string_literals) > 5:
            suggestions.append("Muchos strings hardcodeados. Considera moverlos a res/values/strings.xml")
        
        # 12. Verificar logging adecuado
        if 'System.out.println' in code:
            suggestions.append("Usa Log.d(TAG, message) en lugar de System.out.println para Android")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _validate_xml_layout(self, xml_code: str) -> Dict[str, List[str]]:
        """Validar layout XML de Android"""
        errors = []
        warnings = []
        suggestions = []
        
        lines = xml_code.split('\n')
        
        # 1. Verificar declaración XML
        if not xml_code.strip().startswith('<?xml'):
            errors.append("Falta declaración XML al inicio: <?xml version=\"1.0\" encoding=\"utf-8\"?>")
        
        # 2. Verificar tag raíz
        root_tags = ['LinearLayout', 'RelativeLayout', 'ConstraintLayout', 
                     'FrameLayout', 'CoordinatorLayout', 'ScrollView',
                     'DrawerLayout', 'NestedScrollView']
        
        has_root = any(tag in xml_code for tag in root_tags)
        if not has_root:
            errors.append("No se encontró layout root válido")
        
        # 3. Verificar namespace android
        if 'xmlns:android=' not in xml_code:
            errors.append("Falta namespace xmlns:android=\"http://schemas.android.com/apk/res/android\"")
        
        # 4. Verificar balance de tags
        open_tags = len(re.findall(r'<[A-Z][^/>]*>', xml_code))
        close_tags = len(re.findall(r'</[A-Z][^>]*>', xml_code))
        self_closing = len(re.findall(r'/>', xml_code))
        
        # Tags que se cierran solos cuentan como ambos
        total_open = open_tags
        total_close = close_tags + self_closing
        
        if total_open != total_close:
            errors.append(f"Desequilibrio de tags: {total_open} abiertos, {total_close} cerrados")
        
        # 5. Verificar IDs válidos
        id_pattern = r'android:id="@\+?id/(\w+)"'
        ids = re.findall(id_pattern, xml_code)
        
        if ids:
            # Verificar IDs duplicados
            if len(ids) != len(set(ids)):
                duplicates = [id for id in ids if ids.count(id) > 1]
                errors.append(f"IDs duplicados encontrados: {', '.join(set(duplicates))}")
            
            # Verificar naming convention
            for id_name in ids:
                if not id_name[0].islower():
                    warnings.append(f"ID '{id_name}' debería empezar con minúscula (convención: lowerCamelCase)")
        
        # 6. Verificar atributos required comunes
        view_elements = re.findall(r'<(Button|TextView|EditText|ImageView|ImageButton)[^>]*>', xml_code)
        
        for element in view_elements:
            # Buscar el tag completo
            pattern = rf'<{element}[^>]*/?>'
            matches = re.finditer(pattern, xml_code)
            
            for match in matches:
                tag = match.group(0)
                
                # Verificar layout_width y layout_height
                if 'layout_width' not in tag:
                    errors.append(f"{element} sin android:layout_width")
                if 'layout_height' not in tag:
                    errors.append(f"{element} sin android:layout_height")
        
        # 7. Verificar textSize sin unidad
        text_sizes = re.findall(r'android:textSize="([^"]*)"', xml_code)
        for size in text_sizes:
            if size and not any(unit in size for unit in ['sp', 'dp', 'px', 'pt']):
                warnings.append(f"textSize \"{size}\" sin unidad. Usa 'sp' para texto")
        
        # 8. Verificar colors hardcodeados
        hardcoded_colors = re.findall(r'android:(?:textColor|background)="#[0-9A-Fa-f]{{6}}"', xml_code)
        if hardcoded_colors:
            suggestions.append("Colors hardcodeados detectados. Considera usar res/values/colors.xml")
        
        # 9. Verificar padding/margin sin unidad
        spacing_attrs = ['padding', 'margin', 'layout_margin', 'layout_padding']
        for attr in spacing_attrs:
            pattern = rf'android:{attr}="(\d+)"'
            matches = re.findall(pattern, xml_code)
            for value in matches:
                warnings.append(f"{attr}=\"{value}\" sin unidad. Usa 'dp'")
        
        # 10. Sugerir usar ConstraintLayout para layouts complejos
        if len(view_elements) > 5 and 'ConstraintLayout' not in xml_code:
            suggestions.append("Layout con muchos elementos. Considera usar ConstraintLayout para mejor performance")
        
        # 11. Verificar accessibility (contentDescription en ImageView)
        image_views = re.findall(r'<ImageView[^>]*>', xml_code)
        for img_tag in image_views:
            if 'contentDescription' not in img_tag and 'android:src' in img_tag:
                warnings.append("ImageView sin contentDescription (accessibility)")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _validate_manifest(self, manifest_code: str) -> Dict[str, List[str]]:
        """Validar AndroidManifest.xml"""
        errors = []
        warnings = []
        suggestions = []
        
        # 1. Verificar estructura básica
        if '<manifest' not in manifest_code:
            errors.append("Falta tag <manifest>")
        
        if 'xmlns:android=' not in manifest_code:
            errors.append("Falta namespace xmlns:android")
        
        if '<application' not in manifest_code:
            errors.append("Falta tag <application>")
        
        # 2. Verificar package
        package_match = re.search(r'package="([^"]+)"', manifest_code)
        if not package_match:
            errors.append("Falta atributo package en <manifest>")
        else:
            package_name = package_match.group(1)
            if not package_name.count('.') >= 1:
                warnings.append(f"Package name '{package_name}' debería tener al menos 2 partes (com.example.app)")
        
        # 3. Verificar LAUNCHER activity
        if 'android.intent.action.MAIN' in manifest_code:
            if 'android.intent.category.LAUNCHER' not in manifest_code:
                warnings.append("Tiene MAIN action pero falta LAUNCHER category")
        else:
            warnings.append("No se encontró activity con intent-filter MAIN/LAUNCHER")
        
        # 4. Verificar activities declaradas
        activities = re.findall(r'<activity[^>]*android:name="([^"]+)"', manifest_code)
        for activity in activities:
            if not activity.startswith('.'):
                warnings.append(f"Activity '{activity}' debería empezar con '.' para nombre relativo")
        
        # 5. Verificar permisos comunes
        dangerous_permissions = [
            'CAMERA', 'READ_CONTACTS', 'WRITE_EXTERNAL_STORAGE',
            'ACCESS_FINE_LOCATION', 'RECORD_AUDIO'
        ]
        
        for perm in dangerous_permissions:
            if perm in manifest_code:
                suggestions.append(f"Permiso {perm} requiere runtime permission check en Android 6.0+")
        
        # 6. Verificar exported attribute (Android 12+)
        activity_tags = re.findall(r'<activity[^>]*>', manifest_code)
        for tag in activity_tags:
            if 'android:exported' not in tag:
                if '<intent-filter>' in manifest_code:
                    warnings.append("Activities con intent-filter deben tener android:exported explícito (Android 12+)")
        
        # 7. Verificar versión mínima SDK
        min_sdk = re.search(r'android:minSdkVersion="(\d+)"', manifest_code)
        if min_sdk:
            sdk_version = int(min_sdk.group(1))
            if sdk_version < 21:
                warnings.append(f"minSdkVersion {sdk_version} es muy bajo. Considera API 21+ (Android 5.0)")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def format_report(self, result: Dict[str, List[str]], filename: str = "") -> str:
        """
        Formatear reporte de validación como texto legible
        
        Args:
            result: Resultado de validate()
            filename: Nombre del archivo (opcional)
            
        Returns:
            Reporte formateado
        """
        report = []
        
        if filename:
            report.append(f"\n📄 Validando: {filename}")
            report.append("=" * 60)
        
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        suggestions = result.get('suggestions', [])
        
        if errors:
            report.append(f"\n❌ ERRORES ({len(errors)}):")
            for i, error in enumerate(errors, 1):
                report.append(f"  {i}. {error}")
        
        if warnings:
            report.append(f"\n⚠️ ADVERTENCIAS ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                report.append(f"  {i}. {warning}")
        
        if suggestions:
            report.append(f"\n💡 SUGERENCIAS ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f"  {i}. {suggestion}")
        
        if not errors and not warnings and not suggestions:
            report.append("\n✅ ¡Código limpio! No se encontraron problemas.")
        
        # Resumen
        total_issues = len(errors) + len(warnings) + len(suggestions)
        report.append(f"\n📊 Total: {total_issues} issues encontrados")
        
        return '\n'.join(report)


# Función de conveniencia para uso directo
def validate_android_code(language: str, code: str) -> Dict[str, List[str]]:
    """
    Validar código Android
    
    Args:
        language: 'java', 'kotlin', 'xml', 'manifest'
        code: Código a validar
        
    Returns:
        Diccionario con errors, warnings, suggestions
    """
    validator = AndroidSyntaxValidator()
    return validator.validate(language, code)


def validate_and_format(language: str, code: str, filename: str = "") -> str:
    """
    Validar y formatear reporte
    
    Args:
        language: 'java', 'kotlin', 'xml', 'manifest'
        code: Código a validar
        filename: Nombre del archivo (opcional)
        
    Returns:
        Reporte formateado como string
    """
    validator = AndroidSyntaxValidator()
    result = validator.validate(language, code)
    return validator.format_report(result, filename)
