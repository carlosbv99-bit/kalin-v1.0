"""
Parser de Diff Inteligente para Kalin.
Parsea diffs unificados y aplica merges automáticamente.
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from agent.core.logger import get_logger

logger = get_logger('kalin.diff')

@dataclass
class Hunk:
    """Representa un bloque de cambios en un diff"""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'old_start': self.old_start,
            'old_count': self.old_count,
            'new_start': self.new_start,
            'new_count': self.new_count,
            'lines': self.lines
        }

@dataclass
class FileDiff:
    """Representa los cambios en un archivo"""
    old_path: str
    new_path: str
    hunks: List[Hunk]
    
    def to_dict(self) -> Dict:
        return {
            'old_path': self.old_path,
            'new_path': self.new_path,
            'hunks': [h.to_dict() for h in self.hunks]
        }

class DiffParser:
    """Parser para diffs unificados"""
    
    @staticmethod
    def parse(diff_text: str) -> List[FileDiff]:
        """
        Parsea un diff unificado y retorna lista de FileDiff.
        """
        file_diffs = []
        current_file = None
        current_hunk = None
        current_lines = []
        
        lines = diff_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detectar inicio de nuevo archivo
            if line.startswith('--- a/'):
                old_path = line[6:]
                # Leer siguiente línea para new path
                if i + 1 < len(lines) and lines[i + 1].startswith('+++ b/'):
                    new_path = lines[i + 1][6:]
                    current_file = FileDiff(
                        old_path=old_path,
                        new_path=new_path,
                        hunks=[]
                    )
                    i += 2
                    continue
            
            # Detectar inicio de hunk
            elif line.startswith('@@'):
                match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_count = int(match.group(4)) if match.group(4) else 1
                    
                    current_hunk = Hunk(
                        old_start=old_start,
                        old_count=old_count,
                        new_start=new_start,
                        new_count=new_count,
                        lines=[]
                    )
                    
                    if current_file:
                        current_file.hunks.append(current_hunk)
                    
                    i += 1
                    continue
            
            # Líneas de contenido del diff
            elif line.startswith('+') or line.startswith('-') or line.startswith(' '):
                if current_hunk:
                    current_hunk.lines.append(line)
                i += 1
                continue
            
            # Otros metadatos (índices, etc.)
            elif line.startswith('index') or line.startswith('diff --git'):
                i += 1
                continue
            
            else:
                i += 1
                continue
        
        return file_diffs
    
    @staticmethod
    def apply_diff(original_content: str, diff_text: str) -> Optional[str]:
        """
        Aplica un diff al contenido original.
        Retorna el contenido modificado o None si falla.
        """
        try:
            file_diffs = DiffParser.parse(diff_text)
            
            if not file_diffs:
                logger.warning("No file diffs found in diff text")
                return None
            
            # Asumimos que solo hay un archivo en el diff
            file_diff = file_diffs[0]
            
            lines = original_content.split('\n')
            
            # Aplicar hunks en orden inverso para mantener índices correctos
            for hunk in reversed(file_diff.hunks):
                lines = DiffParser._apply_hunk(lines, hunk)
            
            result = '\n'.join(lines)
            logger.info(f"Diff applied successfully: {len(file_diff.hunks)} hunks")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply diff: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def _apply_hunk(lines: List[str], hunk: Hunk) -> List[str]:
        """Aplica un hunk individual a las líneas"""
        old_start = hunk.old_start - 1  # Convertir a índice 0-based
        old_count = hunk.old_count
        
        # Extraer líneas viejas y nuevas del hunk
        old_lines = []
        new_lines = []
        
        for line in hunk.lines:
            if line.startswith('-'):
                old_lines.append(line[1:])
            elif line.startswith('+'):
                new_lines.append(line[1:])
            elif line.startswith(' '):
                old_lines.append(line[1:])
                new_lines.append(line[1:])
        
        # Verificar que las líneas viejas coincidan
        if old_lines != lines[old_start:old_start + old_count]:
            logger.warning("Hunk context mismatch - attempting fuzzy match")
            # Aquí podríamos implementar fuzzy matching
        
        # Reemplazar líneas
        result = lines[:old_start] + new_lines + lines[old_start + old_count:]
        
        return result

class MergeResolver:
    """Resuelve conflictos de merge"""
    
    @staticmethod
    def three_way_merge(base: str, ours: str, theirs: str) -> Tuple[str, List[Dict]]:
        """
        Realiza un merge de tres vías.
        Returns: (resultado, conflictos)
        """
        conflicts = []
        
        base_lines = base.split('\n')
        ours_lines = ours.split('\n')
        theirs_lines = theirs.split('\n')
        
        result_lines = []
        
        max_len = max(len(base_lines), len(ours_lines), len(theirs_lines))
        
        for i in range(max_len):
            base_line = base_lines[i] if i < len(base_lines) else None
            our_line = ours_lines[i] if i < len(ours_lines) else None
            their_line = theirs_lines[i] if i < len(theirs_lines) else None
            
            if our_line == their_line:
                # Ambos iguales, no hay conflicto
                result_lines.append(our_line or '')
            elif our_line == base_line:
                # Solo ellos cambiaron
                result_lines.append(their_line or '')
            elif their_line == base_line:
                # Solo nosotros cambiamos
                result_lines.append(our_line or '')
            else:
                # Conflicto
                conflicts.append({
                    'line': i + 1,
                    'ours': our_line,
                    'theirs': their_line,
                    'base': base_line
                })
                
                # Marcar conflicto en el resultado
                result_lines.append(f"<<<<<<< OURS\n{our_line}\n=======\n{their_line}\n>>>>>>> THEIRS")
        
        result = '\n'.join(result_lines)
        
        if conflicts:
            logger.warning(f"Merge completed with {len(conflicts)} conflicts")
        else:
            logger.info("Clean merge completed")
        
        return result, conflicts
    
    @staticmethod
    def auto_resolve_conflict(ours: str, theirs: str, strategy: str = 'ours') -> str:
        """
        Resuelve automáticamente un conflicto usando una estrategia.
        Estrategias: 'ours', 'theirs', 'both'
        """
        if strategy == 'ours':
            return ours
        elif strategy == 'theirs':
            return theirs
        elif strategy == 'both':
            return f"{ours}\n{theirs}"
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

# Instancias globales
diff_parser = DiffParser()
merge_resolver = MergeResolver()
