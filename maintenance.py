"""
Script de Optimización y Mantenimiento para Kalin.
Previene fallos de memoria, mejora rendimiento y limpia datos antiguos.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def run_maintenance():
    """Ejecuta tareas de mantenimiento completo"""
    
    print("\n" + "="*80)
    print("🔧 MANTENIMIENTO Y OPTIMIZACIÓN - KALIN")
    print("="*80)
    print()
    
    try:
        from agent.core.stability import (
            config_validator, 
            health_monitor,
            sqlite_optimizer,
            performance_optimizer
        )
        
        # 1. Verificar requisitos del sistema
        print("1️⃣  VERIFICANDO REQUISITOS DEL SISTEMA...")
        requirements = performance_optimizer.check_system_requirements()
        
        if requirements['meets_minimum']:
            print("   ✅ Sistema cumple requisitos mínimos")
        else:
            print("   ❌ Sistema NO cumple requisitos mínimos:")
            for warning in requirements['warnings']:
                print(f"      {warning}")
        
        for rec in requirements.get('recommendations', []):
            print(f"   💡 {rec}")
        
        print()
        
        # 2. Verificar salud del sistema
        print("2️⃣  VERIFICANDO SALUD DEL SISTEMA...")
        health_status = health_monitor.check_health()
        
        status_icon = {
            'healthy': '✅',
            'degraded': '⚠️',
            'critical': '❌',
            'unknown': '❓'
        }.get(health_status['status'], '❓')
        
        print(f"   {status_icon} Estado: {health_status['status'].upper()}")
        
        for check_name, check_result in health_status.get('checks', {}).items():
            icon = '✅' if check_result else '❌'
            print(f"   {icon} {check_name}: {'OK' if check_result else 'FALLÓ'}")
        
        # Sugerencias de recuperación si hay problemas
        suggestions = health_monitor.get_recovery_suggestions(health_status)
        if suggestions:
            print("\n   🔧 SUGERENCIAS DE RECUPERACIÓN:")
            for suggestion in suggestions:
                print(f"      {suggestion}")
        
        print()
        
        # 3. Optimizar base de datos
        print("3️⃣  OPTIMIZANDO BASE DE DATOS...")
        
        sessions_dir = os.path.join(os.path.dirname(__file__), 'sessions')
        os.makedirs(sessions_dir, exist_ok=True)
        
        db_path = os.path.join(sessions_dir, 'sessions.db')
        
        # Crear tabla optimizada
        if sqlite_optimizer.create_session_table(db_path):
            print("   ✅ Tabla de sesiones verificada/creada")
        
        # Aplicar optimizaciones
        if sqlite_optimizer.optimize_database(db_path):
            print("   ✅ Base de datos optimizada (WAL mode, cache, índices)")
        
        # Limpiar sesiones antiguas
        deleted = sqlite_optimizer.cleanup_old_sessions(db_path, max_age_days=30)
        if deleted > 0:
            print(f"   🗑️  Sesiones antiguas eliminadas: {deleted}")
        else:
            print("   ✅ No hay sesiones antiguas que limpiar")
        
        print()
        
        # 4. Validar configuración
        print("4️⃣  VALIDANDO CONFIGURACIÓN...")
        
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            # Cargar configuración actual
            from dotenv import load_dotenv
            load_dotenv(env_path)
            
            current_config = {
                'KALIN_MODE': os.getenv('KALIN_MODE'),
                'FLASK_HOST': os.getenv('FLASK_HOST', '127.0.0.1'),
                'FLASK_PORT': os.getenv('FLASK_PORT', '5000'),
                'FLASK_DEBUG': os.getenv('FLASK_DEBUG', '0')
            }
            
            is_valid, messages = config_validator.validate_config(current_config)
            
            if is_valid:
                print("   ✅ Configuración válida")
            else:
                print("   ⚠️  Problemas de configuración detectados:")
                for msg in messages:
                    print(f"      - {msg}")
        else:
            print("   ⚠️  Archivo .env no encontrado")
        
        print()
        
        # 5. Consejos de rendimiento
        print("5️⃣  CONSEJOS DE RENDIMIENTO:")
        tips = performance_optimizer.get_performance_tips()
        for tip in tips:
            print(f"   {tip}")
        
        print()
        
        # Resumen final
        print("="*80)
        print("📊 RESUMEN DE MANTENIMIENTO")
        print("="*80)
        
        overall_status = "✅ SALUDABLE" if health_status['status'] == 'healthy' else "⚠️ REQUIERE ATENCIÓN"
        print(f"Estado general: {overall_status}")
        print(f"Sesiones limpiadas: {deleted}")
        print(f"Configuración: {'Válida' if is_valid else 'Problemas detectados'}")
        print("="*80)
        
        if health_status['status'] == 'critical':
            print("\n🚨 ADVERTENCIA: Sistema en estado crítico")
            print("   Ejecuta las sugerencias de recuperación arriba")
            return False
        else:
            print("\n✅ Mantenimiento completado exitosamente")
            return True
        
    except Exception as e:
        print(f"\n❌ Error durante el mantenimiento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_maintenance()
    sys.exit(0 if success else 1)
