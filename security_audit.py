"""
Script de Auditoría de Seguridad para Kalin.
Verifica vulnerabilidades críticas antes del despliegue.
"""

import sys
import os
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def run_security_audit():
    """Ejecuta auditoría completa de seguridad"""
    
    print("\n" + "="*80)
    print("🔒 AUDITORÍA DE SEGURIDAD - KALIN")
    print("="*80)
    print()
    
    try:
        from agent.core.security_hardening import security_auditor
        
        # Ejecutar auditoría
        results = security_auditor.run_full_audit()
        
        # Mostrar resultados
        print(f"📅 Timestamp: {results['timestamp']}")
        print()
        
        for check_name, check_result in results['checks'].items():
            status = "✅ PASÓ" if check_result.get('passed', True) else "❌ FALLÓ"
            print(f"\n{check_name.upper().replace('_', ' ')}: {status}")
            
            if 'errors' in check_result and check_result['errors']:
                for error in check_result['errors']:
                    print(f"  ⚠️  {error}")
            
            if 'warnings' in check_result and check_result['warnings']:
                for warning in check_result['warnings']:
                    print(f"  ⚠️  {warning}")
            
            if check_name == 'plugins':
                total = check_result.get('total_plugins', 0)
                print(f"  📦 Total plugins: {total}")
                
                for report in check_result.get('reports', []):
                    plugin_status = "✅ SEGURO" if report['safe_to_load'] else "❌ RIESGOSO"
                    print(f"    - {report['plugin']}: {plugin_status} ({report['alert_count']} alertas)")
        
        # Resumen final
        print("\n" + "="*80)
        summary = results['summary']
        print(f"📊 RESUMEN DE SEGURIDAD")
        print("="*80)
        print(f"  Checks totales: {summary['total_checks']}")
        print(f"  Pasaron: {summary['passed']}")
        print(f"  Fallaron: {summary['failed']}")
        print(f"  Puntuación: {summary['security_score']}")
        print("="*80)
        
        if summary['failed'] > 0:
            print("\n⚠️  ADVERTENCIA: Se detectaron problemas de seguridad.")
            print("   Revisa los errores arriba y corrige antes de desplegar.")
            return False
        else:
            print("\n✅ SISTEMA SEGURO - Listo para producción")
            return True
        
    except Exception as e:
        print(f"\n❌ Error durante la auditoría: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_security_audit()
    sys.exit(0 if success else 1)
