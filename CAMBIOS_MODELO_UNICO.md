# Optimización de Modelos LLM - Eliminación de Doble Modelo

## Resumen de Cambios

Se ha eliminado la configuración de doble modelo (qwen2.5-coder + llama3.2) para optimizar el uso de RAM y mejorar el rendimiento del sistema. Ahora **todos** los casos de uso (código y chat) utilizan un único modelo: **deepseek-coder**.

## Archivos Modificados

### 1. `.env`
- **Cambio principal**: Unificación de modelos
  - `OLLAMA_MODEL=deepseek-coder:latest` (para código)
  - `OLLAMA_CHAT_MODEL=deepseek-coder:latest` (para chat)
- **Beneficio**: Solo se carga un modelo en memoria, reduciendo significativamente el consumo de RAM

### 2. `agent/llm/config.py`
- **Eliminado**: `ProviderType.OLLAMA_CHAT` como tipo separado
- **Simplificado**: La configuración ahora solo tiene un proveedor OLLAMA
- **Actualizado**: Método `is_configured()` para verificar solo `ProviderType.OLLAMA`

### 3. `agent/llm/provider_manager.py`
- **Eliminado**: Lógica especial de routing para chat vs código
- **Simplificado**: Todos los casos de uso usan el mismo proveedor primario
- **Unificado**: Mensajes de debug ahora muestran un único formato
- **Permitido**: Fallback habilitado para todas las tareas

### 4. `.env.example`
- **Agregada**: Nota explicativa sobre el uso de un único modelo para optimizar RAM

## Modos de Uso

El sistema ahora trabaja con deepseek-coder en dos modos conceptuales:

### Modo "code"
- Casos de uso: `fix`, `create`, `enhance`, `analyze`, `design`, `test`, `doc`
- Tokens máximos: Según configuración en `USE_CASE_ROUTER`
- Ejemplo: `/fix archivo.py` → usa deepseek-coder

### Modo "chat"
- Casos de uso: `chat`, `greeting`, `help`
- Tokens máximos: Default (1200 tokens)
- Ejemplo: Mensajes conversacionales → usa deepseek-coder

## Beneficios

1. **Reducción de RAM**: De ~14GB (dos modelos 7B) a ~7GB (un modelo)
2. **Mejor rendimiento**: No hay cambio de contexto entre modelos
3. **Simplicidad**: Configuración más clara y mantenible
4. **Consistencia**: El mismo modelo maneja todo, mejor coherencia en respuestas

## Verificación

Para verificar que los cambios funcionan correctamente:

```bash
# Verificar configuración actual
python -c "from agent.llm.config import LLMConfig; print(LLMConfig.get_env_summary())"

# Ver estado de proveedores
python -c "from agent.llm.client import get_provider_status; print(get_provider_status())"
```

## Notas Importantes

- **No se requiere descargar nuevos modelos**: deepseek-coder ya estaba instalado
- **Backward compatible**: La API no cambia, todo sigue funcionando igual
- **Fallback disponible**: Si deepseek-coder falla, puede usar proveedores cloud (si están configurados)

## Migración

Si deseas volver a usar múltiples modelos en el futuro:

1. Edita `.env` y establece diferentes valores para `OLLAMA_MODEL` y `OLLAMA_CHAT_MODEL`
2. Restaura `ProviderType.OLLAMA_CHAT` en `config.py`
3. Restaura la lógica de routing en `provider_manager.py`

**Recomendación**: Mantener un único modelo a menos que tengas RAM abundante (>32GB).
