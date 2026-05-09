"""
Android Common Error Detector - Detector de errores comunes en Android

Detecta patrones específicos de bugs y problemas frecuentes:
- NullPointerExceptions comunes
- Memory leaks típicos
- Threading issues (UI thread violations)
- Lifecycle problems
- Permission handling errors
- Resource leaks
- Deprecated patterns

Uso:
    from agent.actions.tools.android_error_detector import detect_common_errors
    
    errors = detect_common_errors("java", codigo_java)
    # Retorna lista de errores comunes encontrados con explicaciones
"""

import re
from typing import List, Dict, Tuple


class AndroidErrorDetector:
    """Detector de errores comunes en código Android"""
    
    def __init__(self):
        self.error_patterns = {
            'java': self._detect_java_errors,
            'kotlin': self._detect_kotlin_errors,
            'xml': self._detect_xml_errors,
        }
    
    def detect(self, language: str, code: str) -> List[Dict[str, str]]:
        """
        Detectar errores comunes en código Android
        
        Args:
            language: 'java', 'kotlin', 'xml'
            code: Código a analizar
            
        Returns:
            Lista de diccionarios con {'type': 'error'|'warning', 'category': str, 'message': str, 'line': int, 'fix': str}
        """
        detector = self.error_patterns.get(language.lower())
        
        if not detector:
            return []
        
        return detector(code)
    
    def _detect_java_errors(self, code: str) -> List[Dict[str, str]]:
        """Detectar errores comunes en Java Android"""
        errors = []
        lines = code.split('\n')
        
        # 1. NullPointerException potencial - findViewById sin null check
        findviewbyid_pattern = r'(\w+)\s*=\s*findViewById\(R\.id\.\w+\);'
        for i, line in enumerate(lines, 1):
            match = re.search(findviewbyid_pattern, line)
            if match:
                var_name = match.group(1)
                # Verificar si hay null check posterior
                next_lines = '\n'.join(lines[i:min(i+10, len(lines))])
                if f'if ({var_name} != null)' not in next_lines and f'{var_name}?' not in next_lines:
                    errors.append({
                        'type': 'warning',
                        'category': 'NullPointerException',
                        'message': f"Variable '{var_name}' de findViewById() no tiene null check",
                        'line': i,
                        'fix': f"Agrega: if ({var_name} != null) {{ /* usar {var_name} */ }}"
                    })
        
        # 2. Memory Leak - Contexto estático o retenido incorrectamente
        static_context_patterns = [
            (r'static\s+(Context|Activity)\s+\w+', 'Context/Activity declarado como static puede causar memory leak'),
            (r'static\s+View\s+\w+', 'View declarado como static puede causar memory leak'),
        ]
        
        for pattern, message in static_context_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    errors.append({
                        'type': 'error',
                        'category': 'Memory Leak',
                        'message': message,
                        'line': i,
                        'fix': 'Usa WeakReference o elimina el modificador static'
                    })
        
        # 3. UI Thread Violation - Operaciones pesadas en main thread
        ui_thread_violations = [
            (r'Thread\.sleep\(\d+\)', 'Thread.sleep() bloquea el UI thread. Usa Handler.postDelayed()'),
            (r'\.get\(\)\s*;.*http', 'Network call en UI thread. Usa AsyncTask, Coroutines o Executor'),
            (r'SQLiteOpenHelper.*\.getWritableDatabase\(\)', 'Database operation en UI thread. Usa background thread'),
        ]
        
        for pattern, message in ui_thread_violations:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append({
                        'type': 'error',
                        'category': 'Threading',
                        'message': message,
                        'line': i,
                        'fix': 'Mueve esta operación a un background thread'
                    })
        
        # 4. Resource Leak - Cursor, Stream, Bitmap sin cerrar
        resource_leak_patterns = [
            (r'Cursor\s+\w+\s*=\s*', 'Cursor abierto sin close() explícito'),
            (r'InputStream\s+\w+\s*=\s*', 'InputStream sin close() en finally block'),
            (r'OutputStream\s+\w+\s*=\s*', 'OutputStream sin close() en finally block'),
            (r'BitmapFactory\.decode', 'Bitmap grande puede causar OOM. Usa inSampleSize'),
        ]
        
        for pattern, message in resource_leak_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Verificar si hay try-finally con close
                    surrounding = '\n'.join(lines[max(0,i-5):min(i+15, len(lines))])
                    if 'finally' not in surrounding or '.close()' not in surrounding:
                        errors.append({
                            'type': 'error',
                            'category': 'Resource Leak',
                            'message': message,
                            'line': i,
                            'fix': 'Usa try-with-resources o cierra en finally block'
                        })
        
        # 5. Hardcoded Values - Strings, dimensions, colors hardcodeados
        hardcoded_strings = re.findall(r'"[^"]{5,}"', code)
        if len(hardcoded_strings) > 10:
            errors.append({
                'type': 'warning',
                'category': 'Best Practice',
                'message': f"Demasiados strings hardcodeados ({len(hardcoded_strings)}). Dificulta internacionalización",
                'line': 0,
                'fix': 'Mueve strings a res/values/strings.xml para soporte multi-idioma'
            })
        
        # 6. Missing Super Calls - Lifecycle methods sin super
        lifecycle_methods = ['onCreate', 'onStart', 'onResume', 'onPause', 'onStop', 'onDestroy']
        for method in lifecycle_methods:
            pattern = rf'@Override\s+public\s+void\s+{method}\s*\([^)]*\)\s*\{{'
            if re.search(pattern, code):
                # Verificar si hay super call
                method_pattern = rf'public\s+void\s+{method}\s*\([^)]*\)\s*\{{([^}}]*)\}}'
                match = re.search(method_pattern, code, re.DOTALL)
                if match:
                    method_body = match.group(1)
                    if f'super.{method}(' not in method_body:
                        errors.append({
                            'type': 'error',
                            'category': 'Lifecycle',
                            'message': f"Método {method}() sin llamada a super.{method}()",
                            'line': 0,
                            'fix': f'Agrega al inicio: super.{method}(savedInstanceState);'
                        })
        
        # 7. Deprecated API Usage
        deprecated_apis = [
            (r'new\s+AsyncTask', 'AsyncTask deprecated desde API 30'),
            (r'\.startActivityForResult\(', 'startActivityForResult deprecated'),
            (r'getFragmentManager\(\)', 'Usa getSupportFragmentManager()'),
            (r'new\s+Handler\(\)', 'Handler() sin Looper es deprecated'),
        ]
        
        for pattern, message in deprecated_apis:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    errors.append({
                        'type': 'warning',
                        'category': 'Deprecated API',
                        'message': message,
                        'line': i,
                        'fix': 'Usa la alternativa moderna mencionada'
                    })
        
        # 8. Intent sin Action/Data especificado correctamente
        intent_issues = [
            (r'new\s+Intent\(\)\s*;', 'Intent creado sin action o component definido'),
            (r'startActivity\(intent\)', 'Verifica que intent tenga action/component antes de startActivity'),
        ]
        
        for pattern, message in intent_issues:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    errors.append({
                        'type': 'warning',
                        'category': 'Intent',
                        'message': message,
                        'line': i,
                        'fix': 'Asegúrate de configurar el Intent correctamente antes de usarlo'
                    })
        
        # 9. Toast sin show()
        toast_without_show = re.search(r'Toast\.makeText\([^)]+\)[^;]*$', code, re.MULTILINE)
        if toast_without_show and '.show()' not in code:
            errors.append({
                'type': 'error',
                'category': 'Common Bug',
                'message': 'Toast.makeText() creado pero .show() no llamado',
                'line': 0,
                'fix': 'Agrega .show() al final: Toast.makeText(...).show();'
            })
        
        # 10. RecyclerView sin Adapter set
        if 'RecyclerView' in code and 'setAdapter' not in code:
            errors.append({
                'type': 'warning',
                'category': 'RecyclerView',
                'message': 'RecyclerView encontrado pero setAdapter() no llamado',
                'line': 0,
                'fix': 'Llama recyclerView.setAdapter(adapter) después de configurar el adapter'
            })
        
        # 11. ListView sin Adapter
        if 'ListView' in code and 'setAdapter' not in code:
            errors.append({
                'type': 'warning',
                'category': 'ListView',
                'message': 'ListView encontrado pero setAdapter() no llamado',
                'line': 0,
                'fix': 'Llama listView.setAdapter(adapter)'
            })
        
        # 12. SharedPreferences sin apply/commit
        if 'SharedPreferences.Editor' in code or '.edit()' in code:
            if '.apply()' not in code and '.commit()' not in code:
                errors.append({
                    'type': 'error',
                    'category': 'SharedPreferences',
                    'message': 'SharedPreferences editado pero sin apply() o commit()',
                    'line': 0,
                    'fix': 'Llama editor.apply() o editor.commit() para guardar cambios'
                })
        
        # 13. String comparison con == en lugar de .equals()
        string_comparison = re.findall(r'if\s*\(\s*\w+\s*==\s*"[^"]*"', code)
        if string_comparison:
            errors.append({
                'type': 'error',
                'category': 'String Comparison',
                'message': 'Comparación de String con == en lugar de .equals()',
                'line': 0,
                'fix': 'Usa: if (string.equals("value")) en lugar de =='
            })
        
        # 14. Logging excesivo en producción
        log_count = len(re.findall(r'Log\.(d|i|v|w|e)\(', code))
        if log_count > 20:
            errors.append({
                'type': 'warning',
                'category': 'Performance',
                'message': f'Demasiados logs ({log_count}). Puede afectar performance',
                'line': 0,
                'fix': 'Usa BuildConfig.DEBUG para logs de desarrollo: if (BuildConfig.DEBUG) Log.d(...)'
            })
        
        # 15. Empty catch blocks
        empty_catch = re.findall(r'catch\s*\([^)]+\)\s*\{\s*\}', code)
        if empty_catch:
            errors.append({
                'type': 'error',
                'category': 'Error Handling',
                'message': f'Catch block vacío encontrado ({len(empty_catch)} veces). Silencia errores',
                'line': 0,
                'fix': 'Agrega Log.e(TAG, "Error", e) o maneja la excepción apropiadamente'
            })
        
        return errors
    
    def _detect_kotlin_errors(self, code: str) -> List[Dict[str, str]]:
        """Detectar errores comunes en Kotlin Android"""
        errors = []
        lines = code.split('\n')
        
        # 1. !! operator usage (force unwrap)
        force_unwrap = re.findall(r'\w+!!', code)
        if force_unwrap:
            errors.append({
                'type': 'warning',
                'category': 'Null Safety',
                'message': f'Operador !! encontrado ({len(force_unwrap)} veces). Puede causar NullPointerException',
                'line': 0,
                'fix': 'Usa ?.let {} o ?: run {} para null safety'
            })
        
        # 2. lateinit sin inicialización check
        if 'lateinit var' in code and 'isInitialized' not in code:
            errors.append({
                'type': 'warning',
                'category': 'Lateinit',
                'message': 'lateinit var usado sin verificación isInitialized',
                'line': 0,
                'fix': 'Verifica con: if (::variable.isInitialized) antes de usar'
            })
        
        # 3. GlobalScope usage (deprecated)
        if 'GlobalScope.launch' in code or 'GlobalScope.async' in code:
            errors.append({
                'type': 'error',
                'category': 'Coroutines',
                'message': 'GlobalScope está deprecated. Causa memory leaks',
                'line': 0,
                'fix': 'Usa lifecycleScope o viewModelScope en su lugar'
            })
        
        # 4. runOnUiThread innecesario en coroutines
        if 'runOnUiThread' in code and ('lifecycleScope' in code or 'viewModelScope' in code):
            errors.append({
                'type': 'warning',
                'category': 'Coroutines',
                'message': 'runOnUiThread innecesario cuando usas coroutines',
                'line': 0,
                'fix': 'Las coroutines ya ejecutan en el thread correcto con Dispatchers.Main'
            })
        
        # 5. MutableStateFlow sin initialValue
        if 'MutableStateFlow()' in code:
            errors.append({
                'type': 'error',
                'category': 'StateFlow',
                'message': 'MutableStateFlow requiere valor inicial',
                'line': 0,
                'fix': 'Usa: MutableStateFlow<T>(initialValue)'
            })
        
        return errors
    
    def _detect_xml_errors(self, code: str) -> List[Dict[str, str]]:
        """Detectar errores comunes en XML layouts"""
        errors = []
        lines = code.split('\n')
        
        # 1. wrap_content en listas grandes (performance issue)
        if 'RecyclerView' in code or 'ListView' in code:
            if 'android:layout_height="wrap_content"' in code:
                errors.append({
                    'type': 'warning',
                    'category': 'Performance',
                    'message': 'RecyclerView/ListView con layout_height="wrap_content" causa recálculos',
                    'line': 0,
                    'fix': 'Usa android:layout_height="match_parent" o dimensión fija'
                })
        
        # 2. Nested weights (performance issue)
        weight_count = len(re.findall(r'android:layout_weight=', code))
        if weight_count > 3:
            errors.append({
                'type': 'warning',
                'category': 'Performance',
                'message': f'Muchos layout_weight ({weight_count}). Puede causar múltiples measure passes',
                'line': 0,
                'fix': 'Considera usar ConstraintLayout para layouts complejos'
            })
        
        # 3. ImageView sin scaleType
        image_views = re.findall(r'<ImageView[^>]*>', code)
        for img_tag in image_views:
            if 'scaleType' not in img_tag and 'android:src' in img_tag:
                errors.append({
                    'type': 'warning',
                    'category': 'Image Display',
                    'message': 'ImageView sin scaleType especificado',
                    'line': 0,
                    'fix': 'Agrega android:scaleType="centerCrop" o el tipo apropiado'
                })
        
        # 4. TextView sin maxLines o ellipsize (text overflow)
        text_views = re.findall(r'<TextView[^>]*>', code)
        for tv_tag in text_views:
            if 'maxLines' not in tv_tag and 'ellipsize' not in tv_tag:
                if 'layout_width="match_parent"' in tv_tag or 'layout_width="0dp"' in tv_tag:
                    errors.append({
                        'type': 'warning',
                        'category': 'Text Overflow',
                        'message': 'TextView puede desbordarse con texto largo',
                        'line': 0,
                        'fix': 'Agrega android:maxLines="2" y android:ellipsize="end"'
                    })
        
        # 5. Button sin onClick o click listener setup
        buttons = re.findall(r'<Button[^>]*>', code)
        for btn_tag in buttons:
            if 'onClick' not in btn_tag:
                # Verificar si hay ID para setup programático
                id_match = re.search(r'android:id="@\+?id/(\w+)"', btn_tag)
                if not id_match:
                    errors.append({
                        'type': 'warning',
                        'category': 'User Interaction',
                        'message': 'Button sin onClick definido ni ID para listener',
                        'line': 0,
                        'fix': 'Agrega android:onClick="methodName" o android:id para setup en código'
                    })
        
        # 6. EditText sin inputType
        edit_texts = re.findall(r'<EditText[^>]*>', code)
        for et_tag in edit_texts:
            if 'inputType' not in et_tag:
                errors.append({
                    'type': 'warning',
                    'category': 'Input Validation',
                    'message': 'EditText sin inputType. Teclado genérico mostrado',
                    'line': 0,
                    'fix': 'Agrega android:inputType="textEmailAddress" o el tipo apropiado'
                })
        
        # 7. ScrollView con layout_height="wrap_content"
        if '<ScrollView' in code and 'android:layout_height="wrap_content"' in code:
            errors.append({
                'type': 'warning',
                'category': 'Layout',
                'message': 'ScrollView con layout_height="wrap_content" puede causar problemas',
                'line': 0,
                'fix': 'Usa android:layout_height="match_parent" para ScrollView'
            })
        
        # 8. Missing contentDescription para accessibility
        clickable_views = re.findall(r'<(?:Button|ImageButton|ImageView)[^>]*>', code)
        for view_tag in clickable_views:
            if 'contentDescription' not in view_tag:
                errors.append({
                    'type': 'warning',
                    'category': 'Accessibility',
                    'message': 'View clicable sin contentDescription para screen readers',
                    'line': 0,
                    'fix': 'Agrega android:contentDescription="@string/description" o @null si decorativo'
                })
        
        return errors
    
    def format_report(self, errors: List[Dict[str, str]], filename: str = "") -> str:
        """
        Formatear reporte de errores comunes
        
        Args:
            errors: Lista de errores detectados
            filename: Nombre del archivo (opcional)
            
        Returns:
            Reporte formateado
        """
        if not errors:
            return "\n✅ No se encontraron errores comunes."
        
        report = []
        
        if filename:
            report.append(f"\n🔍 Análisis de Errores Comunes: {filename}")
            report.append("=" * 70)
        
        # Agrupar por categoría
        by_category = {}
        for error in errors:
            category = error['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(error)
        
        # Mostrar por categoría
        for category, category_errors in by_category.items():
            report.append(f"\n📌 {category} ({len(category_errors)}):")
            
            for i, error in enumerate(category_errors, 1):
                icon = '❌' if error['type'] == 'error' else '⚠️'
                report.append(f"  {icon} {error['message']}")
                if error.get('line', 0) > 0:
                    report.append(f"     📍 Línea {error['line']}")
                report.append(f"     🔧 Fix: {error['fix']}")
        
        # Resumen
        total_errors = sum(1 for e in errors if e['type'] == 'error')
        total_warnings = sum(1 for e in errors if e['type'] == 'warning')
        
        report.append(f"\n📊 Resumen:")
        report.append(f"  ❌ Errores: {total_errors}")
        report.append(f"  ⚠️ Advertencias: {total_warnings}")
        report.append(f"  📝 Total: {len(errors)} issues")
        
        return '\n'.join(report)


# Función de conveniencia para uso directo
def detect_common_errors(language: str, code: str) -> List[Dict[str, str]]:
    """
    Detectar errores comunes en código Android
    
    Args:
        language: 'java', 'kotlin', 'xml'
        code: Código a analizar
        
    Returns:
        Lista de errores detectados
    """
    detector = AndroidErrorDetector()
    return detector.detect(language, code)


def detect_and_format(language: str, code: str, filename: str = "") -> str:
    """
    Detectar errores y formatear reporte
    
    Args:
        language: 'java', 'kotlin', 'xml'
        code: Código a analizar
        filename: Nombre del archivo (opcional)
        
    Returns:
        Reporte formateado
    """
    detector = AndroidErrorDetector()
    errors = detector.detect(language, code)
    return detector.format_report(errors, filename)
