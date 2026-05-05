"""
Language Server Protocol (LSP) para Kalin.
Proporciona autocompletado, diagnósticos y sugerencias en tiempo real.
"""

import json
import sys
from typing import Dict, List, Optional, Any
from agent.core.logger import get_logger
from agent.analyzer import analizar_codigo

logger = get_logger('kalin.lsp')

class LanguageServer:
    """Servidor de lenguaje básico para Kalin"""
    
    def __init__(self):
        self.capabilities = {
            'textDocumentSync': {
                'openClose': True,
                'change': 1,  # Incremental
                'willSave': False,
                'didSave': True
            },
            'completionProvider': {
                'resolveProvider': True,
                'triggerCharacters': ['.', ':']
            },
            'hoverProvider': True,
            'definitionProvider': True,
            'referencesProvider': True,
            'documentSymbolProvider': True,
            'workspaceSymbolProvider': True,
            'diagnosticProvider': {
                'interFileDependencies': False,
                'workspaceDiagnostics': False
            }
        }
        
        self.documents: Dict[str, str] = {}
        self.diagnostics: Dict[str, List[Dict]] = {}
    
    def handle_message(self, message: Dict) -> Optional[Dict]:
        """Procesa un mensaje LSP"""
        method = message.get('method')
        msg_id = message.get('id')
        
        if method == 'initialize':
            return self._handle_initialize(msg_id)
        
        elif method == 'textDocument/didOpen':
            return self._handle_did_open(message)
        
        elif method == 'textDocument/didChange':
            return self._handle_did_change(message)
        
        elif method == 'textDocument/didClose':
            return self._handle_did_close(message)
        
        elif method == 'textDocument/completion':
            return self._handle_completion(msg_id, message)
        
        elif method == 'textDocument/hover':
            return self._handle_hover(msg_id, message)
        
        elif method == 'textDocument/publishDiagnostics':
            return self._handle_diagnostics(message)
        
        elif method == 'shutdown':
            return self._handle_shutdown(msg_id)
        
        elif method == 'exit':
            sys.exit(0)
        
        return None
    
    def _handle_initialize(self, msg_id: int) -> Dict:
        """Maneja initialize request"""
        logger.info("LSP initialized")
        
        return {
            'jsonrpc': '2.0',
            'id': msg_id,
            'result': {
                'capabilities': self.capabilities
            }
        }
    
    def _handle_did_open(self, message: Dict) -> None:
        """Maneja documento abierto"""
        params = message['params']
        uri = params['textDocument']['uri']
        text = params['textDocument']['text']
        
        self.documents[uri] = text
        
        # Analizar y generar diagnósticos
        diagnostics = self._analyze_document(uri, text)
        self.diagnostics[uri] = diagnostics
        
        logger.info(f"Document opened: {uri}")
    
    def _handle_did_change(self, message: Dict) -> None:
        """Maneja cambios en documento"""
        params = message['params']
        uri = params['textDocument']['uri']
        
        if uri not in self.documents:
            return
        
        # Aplicar cambios incrementales
        for change in params['contentChanges']:
            if 'range' in change:
                # Cambio incremental (no implementado completamente)
                pass
            else:
                # Cambio completo
                self.documents[uri] = change['text']
        
        # Re-analizar
        diagnostics = self._analyze_document(uri, self.documents[uri])
        self.diagnostics[uri] = diagnostics
        
        # Publicar diagnósticos
        self._publish_diagnostics(uri, diagnostics)
    
    def _handle_did_close(self, message: Dict) -> None:
        """Maneja documento cerrado"""
        params = message['params']
        uri = params['textDocument']['uri']
        
        if uri in self.documents:
            del self.documents[uri]
        
        logger.info(f"Document closed: {uri}")
    
    def _handle_completion(self, msg_id: int, message: Dict) -> Dict:
        """Maneja autocompletado"""
        params = message['params']
        uri = params['textDocument']['uri']
        position = params['position']
        
        # Generar sugerencias basadas en contexto
        suggestions = self._generate_completions(uri, position)
        
        return {
            'jsonrpc': '2.0',
            'id': msg_id,
            'result': {
                'isIncomplete': False,
                'items': suggestions
            }
        }
    
    def _handle_hover(self, msg_id: int, message: Dict) -> Dict:
        """Maneja hover (mostrar información al pasar el mouse)"""
        params = message['params']
        uri = params['textDocument']['uri']
        position = params['position']
        
        info = self._get_hover_info(uri, position)
        
        return {
            'jsonrpc': '2.0',
            'id': msg_id,
            'result': {
                'contents': {
                    'kind': 'markdown',
                    'value': info
                }
            }
        }
    
    def _handle_diagnostics(self, message: Dict) -> None:
        """Publica diagnósticos"""
        pass
    
    def _handle_shutdown(self, msg_id: int) -> Dict:
        """Maneja shutdown"""
        logger.info("LSP shutting down")
        
        return {
            'jsonrpc': '2.0',
            'id': msg_id,
            'result': None
        }
    
    def _analyze_document(self, uri: str, text: str) -> List[Dict]:
        """Analiza un documento y genera diagnósticos"""
        diagnostics = []
        
        try:
            # Usar analyzer existente
            analysis = analizar_codigo(text)
            
            # Convertir análisis a formato LSP
            lines = text.split('\n')
            
            # Ejemplo: detectar líneas muy largas
            for i, line in enumerate(lines):
                if len(line) > 120:
                    diagnostics.append({
                        'range': {
                            'start': {'line': i, 'character': 0},
                            'end': {'line': i, 'character': len(line)}
                        },
                        'severity': 2,  # Warning
                        'message': f'Línea demasiado larga ({len(line)} caracteres)',
                        'source': 'kalin'
                    })
            
            # Detectar TODOs y FIXMEs
            for i, line in enumerate(lines):
                if 'TODO' in line or 'FIXME' in line:
                    diagnostics.append({
                        'range': {
                            'start': {'line': i, 'character': 0},
                            'end': {'line': i, 'character': len(line)}
                        },
                        'severity': 4,  # Info
                        'message': line.strip(),
                        'source': 'kalin'
                    })
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
        
        return diagnostics
    
    def _publish_diagnostics(self, uri: str, diagnostics: List[Dict]):
        """Envía diagnósticos al cliente"""
        message = {
            'jsonrpc': '2.0',
            'method': 'textDocument/publishDiagnostics',
            'params': {
                'uri': uri,
                'diagnostics': diagnostics
            }
        }
        
        self._send_message(message)
    
    def _generate_completions(self, uri: str, position: Dict) -> List[Dict]:
        """Genera sugerencias de autocompletado"""
        # Implementación básica - puede extenderse
        return [
            {
                'label': 'print',
                'kind': 3,  # Function
                'detail': 'print(*args, sep=" ", end="\\n")',
                'documentation': 'Imprime valores'
            },
            {
                'label': 'def',
                'kind': 14,  # Keyword
                'detail': 'def function_name(params):',
                'documentation': 'Define una función'
            }
        ]
    
    def _get_hover_info(self, uri: str, position: Dict) -> str:
        """Obtiene información para hover"""
        if uri not in self.documents:
            return ""
        
        return "Información no disponible"
    
    def _send_message(self, message: Dict):
        """Envía un mensaje LSP al cliente"""
        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"
        sys.stdout.write(header + content)
        sys.stdout.flush()

def run_language_server():
    """Ejecuta el servidor de lenguaje"""
    logger.info("Starting Kalin Language Server")
    
    server = LanguageServer()
    
    # Leer mensajes desde stdin
    content_length = 0
    
    while True:
        line = sys.stdin.readline()
        
        if not line:
            break
        
        if line.startswith('Content-Length:'):
            content_length = int(line.split(':')[1].strip())
        
        elif line == '\r\n' and content_length > 0:
            # Leer contenido del mensaje
            content = sys.stdin.read(content_length)
            
            try:
                message = json.loads(content)
                response = server.handle_message(message)
                
                if response:
                    server._send_message(response)
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            
            content_length = 0

if __name__ == '__main__':
    run_language_server()
