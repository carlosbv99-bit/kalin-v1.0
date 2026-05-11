"""
Patch Manager - Sistema de parches/diffs para modificaciones incrementales
Permite editar archivos sin regenerarlos completamente
"""

import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from agent.core.logger import get_logger

logger = get_logger('kalin.patch_manager')


class PatchOperation(Enum):
    """Tipos de operaciones de parche"""
    INSERT = "insert"        # Insertar contenido nuevo
    DELETE = "delete"        # Eliminar contenido existente
    REPLACE = "replace"      # Reemplazar contenido
    APPEND = "append"        # Agregar al final
    PREPEND = "prepend"      # Agregar al inicio


@dataclass
class PatchLocation:
    """Ubicación donde aplicar el parche"""
    line_number: Optional[int] = None           # Número de línea (0-indexed)
    anchor_text: Optional[str] = None           # Texto de referencia para buscar
    anchor_pattern: Optional[str] = None        # Regex pattern para buscar
    position: str = "after"                     # "before", "after", "at", "end", "start"
    
    def __post_init__(self):
        if self.position not in ["before", "after", "at", "end", "start"]:
            raise ValueError(f"Invalid position: {self.position}")


@dataclass
class ProtectedRegion:
    """Región protegida que no debe ser modificada"""
    name: str
    start_marker: str
    end_marker: str
    description: str = ""


@dataclass
class Patch:
    """Un parche que describe una modificación"""
    file_path: str
    operation: PatchOperation
    content: str
    location: Optional[PatchLocation] = None
    description: str = ""
    metadata: Dict = field(default_factory=dict)
    
    # Para tracking
    timestamp: float = field(default_factory=time.time)
    patch_id: str = ""
    
    def __post_init__(self):
        if not self.patch_id:
            self.patch_id = f"patch_{int(self.timestamp)}_{id(self)}"


@dataclass
class Snapshot:
    """Snapshot del estado del proyecto"""
    snapshot_id: str
    timestamp: float
    files: Dict[str, str]  # {file_path: content}
    user_request: str = ""
    diff_summary: str = ""


class PatchManager:
    """
    Gestiona parches y modificaciones incrementales de archivos.
    
    Características:
    - Aplicación de parches con validación
    - Regiones protegidas (locks semánticos)
    - Snapshots para revertir cambios
    - Diffs inteligentes
    """
    
    def __init__(self):
        self.protected_regions: Dict[str, List[ProtectedRegion]] = {}
        self.snapshots: Dict[str, List[Snapshot]] = {}
        self.patch_history: Dict[str, List[Patch]] = {}
        
        logger.info("PatchManager initialized")
    
    def create_snapshot(
        self,
        project_id: str,
        files: Dict[str, str],
        user_request: str = ""
    ) -> Snapshot:
        """Crea un snapshot del estado actual del proyecto"""
        snapshot_id = f"snapshot_{int(time.time())}_{len(self.snapshots.get(project_id, []))}"
        
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            files=files.copy(),
            user_request=user_request
        )
        
        if project_id not in self.snapshots:
            self.snapshots[project_id] = []
        
        self.snapshots[project_id].append(snapshot)
        
        # Mantener solo últimos 10 snapshots por proyecto
        if len(self.snapshots[project_id]) > 10:
            self.snapshots[project_id] = self.snapshots[project_id][-10:]
        
        logger.info(f"Snapshot created: {snapshot_id} ({len(files)} files)")
        return snapshot
    
    def add_protected_region(
        self,
        file_path: str,
        region: ProtectedRegion
    ):
        """Agrega una región protegida a un archivo"""
        if file_path not in self.protected_regions:
            self.protected_regions[file_path] = []
        
        self.protected_regions[file_path].append(region)
        logger.info(f"Protected region added to {file_path}: {region.name}")
    
    def is_region_protected(
        self,
        file_path: str,
        content: str,
        start_line: int,
        end_line: int
    ) -> bool:
        """Verifica si una región está protegida"""
        if file_path not in self.protected_regions:
            return False
        
        lines = content.split('\n')
        
        for region in self.protected_regions[file_path]:
            # Buscar marcadores en el contenido
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if region.start_marker in line:
                    start_idx = i
                if region.end_marker in line:
                    end_idx = i
            
            if start_idx is not None and end_idx is not None:
                # Verificar si la modificación intersecta con la región protegida
                if not (end_line < start_idx or start_line > end_idx):
                    logger.warning(
                        f"Modification blocked: intersects protected region '{region.name}' "
                        f"in {file_path} (lines {start_idx}-{end_idx})"
                    )
                    return True
        
        return False
    
    def apply_patch(
        self,
        current_content: str,
        patch: Patch,
        validate: bool = True
    ) -> Tuple[str, Dict]:
        """
        Aplica un parche al contenido actual.
        
        Returns:
            Tuple de (nuevo_contenido, metadata)
        """
        lines = current_content.split('\n')
        result_lines = lines.copy()
        
        metadata = {
            'success': False,
            'changes_made': False,
            'error': None,
            'lines_affected': []
        }
        
        try:
            if patch.operation == PatchOperation.INSERT:
                result_lines, metadata = self._apply_insert(result_lines, patch)
            
            elif patch.operation == PatchOperation.DELETE:
                result_lines, metadata = self._apply_delete(result_lines, patch)
            
            elif patch.operation == PatchOperation.REPLACE:
                result_lines, metadata = self._apply_replace(result_lines, patch)
            
            elif patch.operation == PatchOperation.APPEND:
                result_lines, metadata = self._apply_append(result_lines, patch)
            
            elif patch.operation == PatchOperation.PREPEND:
                result_lines, metadata = self._apply_prepend(result_lines, patch)
            
            else:
                raise ValueError(f"Unknown operation: {patch.operation}")
            
            # Validar regiones protegidas
            if validate:
                new_content = '\n'.join(result_lines)
                if metadata['lines_affected']:
                    start_line = min(metadata['lines_affected'])
                    end_line = max(metadata['lines_affected'])
                    
                    if self.is_region_protected(patch.file_path, current_content, start_line, end_line):
                        raise PermissionError(
                            f"Cannot modify protected region in {patch.file_path}"
                        )
            
            metadata['success'] = True
            metadata['changes_made'] = result_lines != lines
            
            new_content = '\n'.join(result_lines)
            logger.info(f"Patch applied successfully: {patch.patch_id}")
            
            return new_content, metadata
        
        except Exception as e:
            metadata['error'] = str(e)
            logger.error(f"Failed to apply patch {patch.patch_id}: {e}")
            return current_content, metadata
    
    def _find_anchor_location(
        self,
        lines: List[str],
        location: PatchLocation
    ) -> Optional[int]:
        """Encuentra la ubicación basada en anchor text o pattern"""
        
        if location.anchor_text:
            for i, line in enumerate(lines):
                if location.anchor_text in line:
                    return i + (0 if location.position == "at" else 
                               (1 if location.position == "after" else 0))
        
        if location.anchor_pattern:
            pattern = re.compile(location.anchor_pattern)
            for i, line in enumerate(lines):
                if pattern.search(line):
                    return i + (0 if location.position == "at" else 
                               (1 if location.position == "after" else 0))
        
        if location.line_number is not None:
            return location.line_number
        
        return None
    
    def _apply_insert(
        self,
        lines: List[str],
        patch: Patch
    ) -> Tuple[List[str], Dict]:
        """Aplica operación INSERT"""
        metadata = {'lines_affected': []}
        
        if patch.location:
            insert_pos = self._find_anchor_location(lines, patch.location)
            
            if insert_pos is None:
                # Si no se encuentra el anchor, agregar al final antes de </body> o similar
                for i in range(len(lines) - 1, -1, -1):
                    if '</body>' in lines[i] or '</html>' in lines[i]:
                        insert_pos = i
                        break
                
                if insert_pos is None:
                    insert_pos = len(lines)
            
            new_lines = patch.content.split('\n')
            result = lines[:insert_pos] + new_lines + lines[insert_pos:]
            metadata['lines_affected'] = list(range(insert_pos, insert_pos + len(new_lines)))
            
            return result, metadata
        else:
            # Sin ubicación específica, agregar al final
            new_lines = patch.content.split('\n')
            result = lines + new_lines
            metadata['lines_affected'] = list(range(len(lines), len(result)))
            return result, metadata
    
    def _apply_delete(
        self,
        lines: List[str],
        patch: Patch
    ) -> Tuple[List[str], Dict]:
        """Aplica operación DELETE"""
        metadata = {'lines_affected': []}
        
        if patch.location:
            delete_pos = self._find_anchor_location(lines, patch.location)
            
            if delete_pos is not None:
                # Determinar cuántas líneas eliminar
                lines_to_delete = len(patch.content.split('\n')) if patch.content else 1
                result = lines[:delete_pos] + lines[delete_pos + lines_to_delete:]
                metadata['lines_affected'] = list(range(delete_pos, delete_pos + lines_to_delete))
                return result, metadata
        
        # Si no se puede determinar qué borrar, devolver original
        logger.warning("Delete operation failed: could not determine location")
        return lines, metadata
    
    def _apply_replace(
        self,
        lines: List[str],
        patch: Patch
    ) -> Tuple[List[str], Dict]:
        """Aplica operación REPLACE"""
        metadata = {'lines_affected': []}
        
        if patch.location:
            replace_pos = self._find_anchor_location(lines, patch.location)
            
            if replace_pos is not None:
                old_lines_count = len(patch.metadata.get('old_content', '').split('\n'))
                new_lines = patch.content.split('\n')
                
                result = (
                    lines[:replace_pos] + 
                    new_lines + 
                    lines[replace_pos + old_lines_count:]
                )
                metadata['lines_affected'] = list(range(replace_pos, replace_pos + len(new_lines)))
                return result, metadata
        
        # Fallback: buscar y reemplazar texto exacto
        if patch.metadata.get('old_content'):
            content = '\n'.join(lines)
            old_content = patch.metadata['old_content']
            new_content = patch.content
            
            if old_content in content:
                new_full = content.replace(old_content, new_content, 1)
                return new_full.split('\n'), metadata
        
        logger.warning("Replace operation failed: could not determine location")
        return lines, metadata
    
    def _apply_append(
        self,
        lines: List[str],
        patch: Patch
    ) -> Tuple[List[str], Dict]:
        """Aplica operación APPEND (al final)"""
        new_lines = patch.content.split('\n')
        result = lines + new_lines
        metadata = {'lines_affected': list(range(len(lines), len(result)))}
        return result, metadata
    
    def _apply_prepend(
        self,
        lines: List[str],
        patch: Patch
    ) -> Tuple[List[str], Dict]:
        """Aplica operación PREPEND (al inicio)"""
        new_lines = patch.content.split('\n')
        result = new_lines + lines
        metadata = {'lines_affected': list(range(0, len(new_lines)))}
        return result, metadata
    
    def generate_diff(
        self,
        original: str,
        modified: str,
        file_path: str = ""
    ) -> str:
        """Genera un diff legible entre dos versiones"""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        # Algoritmo simple de diff
        diff_lines = []
        diff_lines.append(f"--- {file_path or 'original'}")
        diff_lines.append(f"+++ {file_path or 'modified'}")
        
        i, j = 0, 0
        while i < len(original_lines) or j < len(modified_lines):
            if i >= len(original_lines):
                diff_lines.append(f"+ {modified_lines[j]}")
                j += 1
            elif j >= len(modified_lines):
                diff_lines.append(f"- {original_lines[i]}")
                i += 1
            elif original_lines[i] == modified_lines[j]:
                diff_lines.append(f"  {original_lines[i]}")
                i += 1
                j += 1
            else:
                # Línea cambiada
                diff_lines.append(f"- {original_lines[i]}")
                diff_lines.append(f"+ {modified_lines[j]}")
                i += 1
                j += 1
        
        return '\n'.join(diff_lines)
    
    def revert_to_snapshot(
        self,
        project_id: str,
        snapshot_id: str
    ) -> Optional[Dict[str, str]]:
        """Revierte el proyecto a un snapshot anterior"""
        if project_id not in self.snapshots:
            logger.error(f"No snapshots found for project: {project_id}")
            return None
        
        for snapshot in self.snapshots[project_id]:
            if snapshot.snapshot_id == snapshot_id:
                logger.info(f"Reverted to snapshot: {snapshot_id}")
                return snapshot.files.copy()
        
        logger.error(f"Snapshot not found: {snapshot_id}")
        return None
    
    def get_patch_history(
        self,
        project_id: str,
        limit: int = 20
    ) -> List[Patch]:
        """Obtiene el historial de parches aplicados"""
        if project_id not in self.patch_history:
            return []
        
        history = self.patch_history[project_id]
        return history[-limit:]
    
    def record_patch(
        self,
        project_id: str,
        patch: Patch
    ):
        """Registra un parche en el historial"""
        if project_id not in self.patch_history:
            self.patch_history[project_id] = []
        
        self.patch_history[project_id].append(patch)
        
        # Mantener solo últimos 50 parches
        if len(self.patch_history[project_id]) > 50:
            self.patch_history[project_id] = self.patch_history[project_id][-50:]


# Singleton
_patch_manager_instance = None


def get_patch_manager() -> PatchManager:
    """Obtiene la instancia singleton del PatchManager"""
    global _patch_manager_instance
    if _patch_manager_instance is None:
        _patch_manager_instance = PatchManager()
    return _patch_manager_instance
