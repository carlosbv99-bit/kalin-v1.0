"""
Sistema de Diffs y Parches
Aplica cambios incrementales en lugar de reescribir archivos completos

Ventajas:
- Ahorra tokens (solo envía cambios, no archivo completo)
- Reduce errores (menor probabilidad de corrupción)
- Facilita colaboración multiagente (múltiples agentes pueden patchear el mismo archivo)
- Mejora undo/rollback (fácil revertir parches específicos)
"""

import os
import difflib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from agent.core.logger import get_logger

logger = get_logger('kalin.patch_system')


class Patch:
    """Representa un parche/diff para un archivo"""
    
    def __init__(
        self,
        file_path: str,
        original_content: str,
        new_content: str,
        description: str = "",
        author: str = "system"
    ):
        self.file_path = file_path
        self.original_content = original_content
        self.new_content = new_content
        self.description = description
        self.author = author
        self.timestamp = datetime.now().isoformat()
        
        # Generar diff unificado
        self.diff = self._generate_diff()
        self.hunks = self._parse_hunks()
        
        # Metadata
        self.lines_added = sum(1 for line in self.diff if line.startswith('+') and not line.startswith('+++'))
        self.lines_removed = sum(1 for line in self.diff if line.startswith('-') and not line.startswith('---'))
        self.size = len(self.diff)
    
    def _generate_diff(self) -> str:
        """Genera diff unificado"""
        original_lines = self.original_content.splitlines(keepends=True)
        new_lines = self.new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _parse_hunks(self) -> List[Dict]:
        """Parsea los hunks del diff"""
        hunks = []
        current_hunk = None
        
        for line in self.diff.splitlines():
            if line.startswith('@@'):
                if current_hunk:
                    hunks.append(current_hunk)
                
                # Parsear línea @@ -old_start,old_count +new_start,new_count @@
                parts = line.split('@@')
                if len(parts) >= 2:
                    coords = parts[1].strip().split(' ')
                    old_coords = coords[0][1:].split(',')  # -start,count
                    new_coords = coords[1][1:].split(',')  # +start,count
                    
                    current_hunk = {
                        'header': line,
                        'old_start': int(old_coords[0]),
                        'old_count': int(old_coords[1]) if len(old_coords) > 1 else 1,
                        'new_start': int(new_coords[0]),
                        'new_count': int(new_coords[1]) if len(new_coords) > 1 else 1,
                        'changes': []
                    }
            elif current_hunk and (line.startswith('+') or line.startswith('-') or line.startswith(' ')):
                current_hunk['changes'].append(line)
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            'file_path': self.file_path,
            'description': self.description,
            'author': self.author,
            'timestamp': self.timestamp,
            'diff': self.diff,
            'lines_added': self.lines_added,
            'lines_removed': self.lines_removed,
            'hunks': len(self.hunks)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], original_content: str, new_content: str) -> 'Patch':
        """Crea Patch desde diccionario"""
        patch = cls(
            file_path=data['file_path'],
            original_content=original_content,
            new_content=new_content,
            description=data.get('description', ''),
            author=data.get('author', 'system')
        )
        patch.timestamp = data.get('timestamp', patch.timestamp)
        return patch


class PatchManager:
    """
    Gestiona aplicación, reversión y historial de parches
    
    Uso:
        patch_mgr = PatchManager()
        patch = patch_mgr.create_patch(file_path, original, modified)
        success = patch_mgr.apply_patch(patch)
    """
    
    def __init__(self):
        self.patch_history: List[Patch] = []
        self.applied_patches: Dict[str, List[Patch]] = {}  # file_path -> [patches]
        self.rollback_stack: List[Patch] = []  # Para undo
        
        logger.info("PatchManager initialized")
    
    def create_patch(
        self,
        file_path: str,
        original_content: str,
        new_content: str,
        description: str = "",
        author: str = "system"
    ) -> Patch:
        """
        Crea un parche comparando contenido original vs modificado
        
        Args:
            file_path: Ruta del archivo
            original_content: Contenido original
            new_content: Contenido modificado
            description: Descripción del cambio
            author: Autor del cambio
        
        Returns:
            Objeto Patch
        """
        patch = Patch(
            file_path=file_path,
            original_content=original_content,
            new_content=new_content,
            description=description,
            author=author
        )
        
        logger.info(f"Patch created: {patch.lines_added} additions, {patch.lines_removed} deletions")
        return patch
    
    def apply_patch(self, patch: Patch, verify: bool = True) -> bool:
        """
        Aplica un parche a un archivo
        
        Args:
            patch: Objeto Patch a aplicar
            verify: Verificar que el contenido actual coincide con original
        
        Returns:
            True si se aplicó exitosamente
        """
        try:
            file_path = patch.file_path
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Verificar que el contenido actual coincide con el original del patch
            if verify and current_content != patch.original_content:
                logger.warning(f"Content mismatch for {file_path}. Attempting smart apply...")
                
                # Intentar aplicar diff directamente
                result = self._apply_diff_smart(file_path, current_content, patch.diff)
                if not result:
                    logger.error("Smart apply failed. Content has diverged.")
                    return False
            else:
                # Aplicar directamente
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(patch.new_content)
            
            # Registrar en historial
            self.patch_history.append(patch)
            
            if file_path not in self.applied_patches:
                self.applied_patches[file_path] = []
            self.applied_patches[file_path].append(patch)
            
            # Agregar a stack de rollback
            self.rollback_stack.append(patch)
            
            # Emitir evento
            from agent.core.event_bus import get_event_bus, EVENT_PATCH_APPLIED
            event_bus = get_event_bus()
            event_bus.emit(EVENT_PATCH_APPLIED, {
                'file_path': patch.file_path,
                'lines_added': patch.lines_added,
                'lines_removed': patch.lines_removed,
                'author': patch.author
            }, source='patch_system')
            
            logger.info(f"Patch applied successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying patch: {e}")
            return False
    
    def _apply_diff_smart(self, file_path: str, current_content: str, diff: str) -> bool:
        """
        Intenta aplicar diff incluso si el contenido ha cambiado
        
        Usa patch/unpatch logic para aplicar cambios de forma inteligente
        """
        try:
            import subprocess
            import tempfile
            
            # Crear archivo temporal con el diff
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False, encoding='utf-8') as f:
                f.write(diff)
                patch_file = f.name
            
            try:
                # Aplicar patch usando comando system
                result = subprocess.run(
                    ['patch', '-p0', '--forward', '--no-backup-if-mismatch', file_path, patch_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return result.returncode == 0
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(patch_file):
                    os.remove(patch_file)
        
        except Exception as e:
            logger.error(f"Smart apply failed: {e}")
            return False
    
    def undo_last_patch(self, file_path: str = None) -> bool:
        """
        Revierte el último parche aplicado
        
        Args:
            file_path: Si se especifica, solo revierte parches de ese archivo
        
        Returns:
            True si se revirtió exitosamente
        """
        if not self.rollback_stack:
            logger.warning("No patches to undo")
            return False
        
        # Encontrar el último parche relevante
        if file_path:
            patches_for_file = [p for p in reversed(self.rollback_stack) if p.file_path == file_path]
            if not patches_for_file:
                logger.warning(f"No patches to undo for {file_path}")
                return False
            patch_to_undo = patches_for_file[0]
        else:
            patch_to_undo = self.rollback_stack[-1]
        
        try:
            # Revertir aplicando el contenido original
            with open(patch_to_undo.file_path, 'w', encoding='utf-8') as f:
                f.write(patch_to_undo.original_content)
            
            # Remover del stack
            self.rollback_stack.remove(patch_to_undo)
            
            logger.info(f"Patch undone: {patch_to_undo.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing patch: {e}")
            return False
    
    def get_patch_history(self, file_path: str = None, limit: int = None) -> List[Dict]:
        """
        Obtiene historial de parches
        
        Args:
            file_path: Filtrar por archivo específico
            limit: Límite de resultados
        
        Returns:
            Lista de parches en formato dict
        """
        if file_path:
            history = [p.to_dict() for p in self.patch_history if p.file_path == file_path]
        else:
            history = [p.to_dict() for p in self.patch_history]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_file_patches(self, file_path: str) -> List[Patch]:
        """Obtiene todos los parches aplicados a un archivo"""
        return self.applied_patches.get(file_path, [])
    
    def generate_incremental_patch(
        self,
        file_path: str,
        changes: List[Dict[str, Any]]
    ) -> Optional[Patch]:
        """
        Genera un parche incremental a partir de cambios específicos
        
        Args:
            file_path: Ruta del archivo
            changes: Lista de cambios [{line_number, action, content}]
                     action: 'add', 'delete', 'modify'
        
        Returns:
            Patch generado o None si falla
        """
        try:
            # Leer contenido actual
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Aplicar cambios incrementalmente
            offset = 0
            for change in sorted(changes, key=lambda x: x['line_number']):
                line_num = change['line_number'] + offset
                action = change['action']
                content = change.get('content', '')
                
                if action == 'delete':
                    if 0 <= line_num < len(lines):
                        lines.pop(line_num)
                        offset -= 1
                
                elif action == 'add':
                    lines.insert(line_num, content + '\n')
                    offset += 1
                
                elif action == 'modify':
                    if 0 <= line_num < len(lines):
                        lines[line_num] = content + '\n'
            
            new_content = ''.join(lines)
            
            # Leer original para comparar
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Crear patch
            return self.create_patch(
                file_path=file_path,
                original_content=original_content,
                new_content=new_content,
                description=f"Incremental patch: {len(changes)} changes"
            )
        
        except Exception as e:
            logger.error(f"Error generating incremental patch: {e}")
            return None
    
    def merge_patches(self, patches: List[Patch]) -> Optional[Patch]:
        """
        Fusiona múltiples parches en uno solo
        
        Útil cuando múltiples agentes modifican el mismo archivo
        
        Args:
            patches: Lista de parches a fusionar
        
        Returns:
            Patch fusionado o None si hay conflictos
        """
        if not patches:
            return None
        
        if len(patches) == 1:
            return patches[0]
        
        # Verificar que todos son del mismo archivo
        file_path = patches[0].file_path
        if not all(p.file_path == file_path for p in patches):
            logger.error("Cannot merge patches from different files")
            return None
        
        # Aplicar secuencialmente para obtener contenido final
        current_content = patches[0].original_content
        
        for patch in patches:
            if patch.original_content != current_content:
                logger.warning(f"Conflict detected in patch sequence for {file_path}")
                # Intentar continuar de todas formas
            current_content = patch.new_content
        
        # Crear patch consolidado
        return self.create_patch(
            file_path=file_path,
            original_content=patches[0].original_content,
            new_content=current_content,
            description=f"Merged patch: {len(patches)} patches combined"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del sistema de parches"""
        total_patches = len(self.patch_history)
        total_additions = sum(p.lines_added for p in self.patch_history)
        total_deletions = sum(p.lines_removed for p in self.patch_history)
        
        return {
            'total_patches': total_patches,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'files_modified': len(self.applied_patches),
            'rollback_available': len(self.rollback_stack)
        }


# Singleton global
_patch_manager = None


def get_patch_manager() -> PatchManager:
    """Obtiene instancia singleton del PatchManager"""
    global _patch_manager
    if _patch_manager is None:
        _patch_manager = PatchManager()
    return _patch_manager
