"""
Experience Memory - Sistema de Aprendizaje Experiencial para Kalin.

Permite al agente aprender de experiencias pasadas, reconocer patrones
y mejorar sus estrategias basándose en tasas de éxito históricas.
"""

import json
import os
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
from agent.core.logger import get_logger

logger = get_logger('kalin.experience')

@dataclass
class Experience:
    """Representa una experiencia individual"""
    experience_id: str
    task_type: str  # 'fix', 'create', 'analyze', 'refactor', etc.
    problem_description: str  # Descripción del problema
    problem_hash: str  # Hash para identificación rápida
    file_type: str  # 'python', 'dart', 'java', etc.
    strategy_used: str  # 'smart', 'aggressive', 'conservative'
    success: bool  # ¿Fue exitoso?
    confidence_score: float  # 0.0 a 1.0
    tokens_used: int = 0
    duration_seconds: float = 0.0
    solution_summary: str = ""  # Resumen de la solución aplicada
    error_message: str = ""  # Si falló, qué error ocurrió
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        return cls(**data)

@dataclass
class PatternInsight:
    """Patrón o insight aprendido"""
    pattern_id: str
    pattern_type: str  # 'recurring_problem', 'successful_strategy', 'common_error'
    description: str
    frequency: int  # Cuántas veces se ha visto
    success_rate: float  # Tasa de éxito (0.0 a 1.0)
    recommended_action: str  # Qué hacer cuando se detecte
    examples: List[str] = field(default_factory=list)  # Ejemplos relacionados
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PatternInsight':
        return cls(**data)

class ExperienceMemory:
    """
    Sistema de memoria experiencial que permite a Kalin aprender y mejorar.
    
    Características:
    - Registra todas las experiencias (éxitos y fallos)
    - Detecta patrones recurrentes
    - Sugiere estrategias óptimas basadas en historial
    - Construye base de conocimiento reusable
    - Adapta comportamiento con el tiempo
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'experience_memory'
            )
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Archivos de persistencia
        self.experiences_file = os.path.join(self.storage_dir, 'experiences.json')
        self.patterns_file = os.path.join(self.storage_dir, 'patterns.json')
        self.statistics_file = os.path.join(self.storage_dir, 'statistics.json')
        
        # Memoria en memoria (cache)
        self.experiences: List[Experience] = []
        self.patterns: Dict[str, PatternInsight] = {}
        self.statistics: Dict[str, Any] = {
            'total_experiences': 0,
            'total_successes': 0,
            'total_failures': 0,
            'success_rate_by_type': {},
            'success_rate_by_strategy': {},
            'success_rate_by_file_type': {},
            'average_confidence': 0.0,
            'most_common_problems': [],
            'best_strategies': {},
            'learning_started_at': time.time(),
            'last_updated': time.time()
        }
        
        # Índices para búsqueda rápida
        self._problem_index: Dict[str, List[str]] = defaultdict(list)  # hash -> [experience_ids]
        self._type_index: Dict[str, List[str]] = defaultdict(list)  # task_type -> [experience_ids]
        self._file_type_index: Dict[str, List[str]] = defaultdict(list)  # file_type -> [experience_ids]
        
        # Cargar datos existentes
        self._load()
        
        logger.info(f"ExperienceMemory initialized: {len(self.experiences)} experiencias cargadas")
    
    def record_experience(
        self,
        task_type: str,
        problem_description: str,
        file_type: str,
        strategy_used: str,
        success: bool,
        confidence_score: float,
        tokens_used: int = 0,
        duration_seconds: float = 0.0,
        solution_summary: str = "",
        error_message: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Registra una nueva experiencia.
        
        Args:
            task_type: Tipo de tarea ('fix', 'create', 'analyze', etc.)
            problem_description: Descripción del problema resuelto/intentado
            file_type: Tipo de archivo ('python', 'dart', etc.)
            strategy_used: Estrategia utilizada
            success: ¿Fue exitoso?
            confidence_score: Confianza en la solución (0.0-1.0)
            tokens_used: Tokens consumidos
            duration_seconds: Duración de la operación
            solution_summary: Resumen de la solución
            error_message: Mensaje de error si falló
            metadata: Metadatos adicionales
        
        Returns:
            ID de la experiencia registrada
        """
        import uuid
        
        # Generar hash único del problema
        problem_hash = hashlib.md5(
            f"{task_type}:{problem_description[:100]}:{file_type}".encode()
        ).hexdigest()
        
        experience_id = str(uuid.uuid4())[:12]
        
        experience = Experience(
            experience_id=experience_id,
            task_type=task_type,
            problem_description=problem_description[:500],  # Limitar longitud
            problem_hash=problem_hash,
            file_type=file_type,
            strategy_used=strategy_used,
            success=success,
            confidence_score=confidence_score,
            tokens_used=tokens_used,
            duration_seconds=duration_seconds,
            solution_summary=solution_summary[:300],
            error_message=error_message[:200] if error_message else "",
            metadata=metadata or {}
        )
        
        # Agregar a memoria
        self.experiences.append(experience)
        
        # Actualizar índices
        self._problem_index[problem_hash].append(experience_id)
        self._type_index[task_type].append(experience_id)
        self._file_type_index[file_type].append(experience_id)
        
        # Actualizar estadísticas
        self._update_statistics(experience)
        
        # Detectar patrones
        self._detect_patterns()
        
        # Guardar periódicamente (cada 10 experiencias)
        if len(self.experiences) % 10 == 0:
            self.save()
        
        logger.info(
            f"Experience recorded: id={experience_id}, type={task_type}, "
            f"success={success}, confidence={confidence_score:.2f}"
        )
        
        return experience_id
    
    def get_best_strategy(
        self,
        task_type: str,
        file_type: str = "",
        problem_description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Sugiere la mejor estrategia basada en experiencia previa.
        
        Args:
            task_type: Tipo de tarea
            file_type: Tipo de archivo (opcional)
            problem_description: Descripción del problema (opcional)
        
        Returns:
            Diccionario con estrategia recomendada y confianza, o None
        """
        # Filtrar experiencias relevantes
        relevant = [
            exp for exp in self.experiences
            if exp.task_type == task_type
        ]
        
        if not relevant:
            return None
        
        # Si hay descripción del problema, buscar problemas similares
        if problem_description:
            problem_hash = hashlib.md5(
                f"{task_type}:{problem_description[:100]}:{file_type}".encode()
            ).hexdigest()
            
            similar_experiences = [
                exp for exp in relevant
                if exp.problem_hash == problem_hash
            ]
            
            if similar_experiences:
                # Calcular tasa de éxito por estrategia para este problema específico
                strategy_stats = defaultdict(lambda: {'successes': 0, 'total': 0, 'avg_confidence': 0.0})
                
                for exp in similar_experiences:
                    stats = strategy_stats[exp.strategy_used]
                    stats['total'] += 1
                    if exp.success:
                        stats['successes'] += 1
                    stats['avg_confidence'] += exp.confidence_score
                
                # Encontrar mejor estrategia
                best_strategy = None
                best_score = -1
                
                for strategy, stats in strategy_stats.items():
                    success_rate = stats['successes'] / stats['total'] if stats['total'] > 0 else 0
                    avg_confidence = stats['avg_confidence'] / stats['total'] if stats['total'] > 0 else 0
                    score = (success_rate * 0.7) + (avg_confidence * 0.3)  # Ponderación
                    
                    if score > best_score:
                        best_score = score
                        best_strategy = {
                            'strategy': strategy,
                            'confidence': score,
                            'success_rate': success_rate,
                            'sample_size': stats['total'],
                            'recommendation': f"Usar estrategia '{strategy}' (éxito: {success_rate:.0%})"
                        }
                
                return best_strategy
        
        # Si no hay problema específico, usar estadísticas generales por tipo
        if file_type:
            relevant = [exp for exp in relevant if exp.file_type == file_type]
        
        if not relevant:
            return None
        
        # Calcular mejor estrategia general
        strategy_stats = defaultdict(lambda: {'successes': 0, 'total': 0})
        
        for exp in relevant:
            stats = strategy_stats[exp.strategy_used]
            stats['total'] += 1
            if exp.success:
                stats['successes'] += 1
        
        best_strategy = None
        best_success_rate = 0
        
        for strategy, stats in strategy_stats.items():
            success_rate = stats['successes'] / stats['total'] if stats['total'] > 0 else 0
            
            if success_rate > best_success_rate and stats['total'] >= 3:  # Mínimo 3 muestras
                best_success_rate = success_rate
                best_strategy = {
                    'strategy': strategy,
                    'confidence': success_rate,
                    'success_rate': success_rate,
                    'sample_size': stats['total'],
                    'recommendation': f"Estrategia '{strategy}' tiene {success_rate:.0%} de éxito"
                }
        
        return best_strategy
    
    def get_similar_experiences(
        self,
        task_type: str,
        problem_description: str,
        limit: int = 5
    ) -> List[Experience]:
        """
        Busca experiencias similares a un problema actual.
        
        Args:
            task_type: Tipo de tarea
            problem_description: Descripción del problema
            limit: Máximo número de resultados
        
        Returns:
            Lista de experiencias similares ordenadas por relevancia
        """
        problem_hash = hashlib.md5(
            f"{task_type}:{problem_description[:100]}".encode()
        ).hexdigest()
        
        # Buscar por hash exacto primero
        exact_matches = [
            exp for exp in self.experiences
            if exp.problem_hash == problem_hash
        ]
        
        if exact_matches:
            # Ordenar por fecha (más recientes primero) y devolver los más exitosos
            sorted_exp = sorted(
                exact_matches,
                key=lambda x: (x.success, x.timestamp),
                reverse=True
            )
            return sorted_exp[:limit]
        
        # Si no hay coincidencias exactas, buscar por tipo de tarea
        similar = [
            exp for exp in self.experiences
            if exp.task_type == task_type
        ]
        
        # Ordenar por confianza y éxito
        sorted_exp = sorted(
            similar,
            key=lambda x: (x.success, x.confidence_score, x.timestamp),
            reverse=True
        )
        
        return sorted_exp[:limit]
    
    def get_patterns(self, pattern_type: str = "") -> List[PatternInsight]:
        """
        Obtiene patrones aprendidos.
        
        Args:
            pattern_type: Filtrar por tipo (opcional)
        
        Returns:
            Lista de patrones
        """
        if pattern_type:
            return [
                p for p in self.patterns.values()
                if p.pattern_type == pattern_type
            ]
        return list(self.patterns.values())
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen completo del aprendizaje.
        
        Returns:
            Diccionario con estadísticas y insights
        """
        total = self.statistics['total_experiences']
        successes = self.statistics['total_successes']
        failures = self.statistics['total_failures']
        
        overall_success_rate = successes / total if total > 0 else 0
        
        return {
            'total_experiences': total,
            'total_successes': successes,
            'total_failures': failures,
            'overall_success_rate': overall_success_rate,
            'success_rate_by_type': self.statistics['success_rate_by_type'],
            'success_rate_by_strategy': self.statistics['success_rate_by_strategy'],
            'success_rate_by_file_type': self.statistics['success_rate_by_file_type'],
            'patterns_detected': len(self.patterns),
            'learning_duration_hours': (time.time() - self.statistics['learning_started_at']) / 3600,
            'top_insights': self._get_top_insights(),
            'recommendations': self._generate_recommendations()
        }
    
    def _update_statistics(self, experience: Experience):
        """Actualiza estadísticas con nueva experiencia"""
        self.statistics['total_experiences'] += 1
        self.statistics['last_updated'] = time.time()
        
        if experience.success:
            self.statistics['total_successes'] += 1
        else:
            self.statistics['total_failures'] += 1
        
        # Actualizar tasa de éxito por tipo de tarea
        task_type = experience.task_type
        if task_type not in self.statistics['success_rate_by_type']:
            self.statistics['success_rate_by_type'][task_type] = {
                'successes': 0,
                'total': 0
            }
        
        stats = self.statistics['success_rate_by_type'][task_type]
        stats['total'] += 1
        if experience.success:
            stats['successes'] += 1
        stats['rate'] = stats['successes'] / stats['total']
        
        # Actualizar tasa de éxito por estrategia
        strategy = experience.strategy_used
        if strategy not in self.statistics['success_rate_by_strategy']:
            self.statistics['success_rate_by_strategy'][strategy] = {
                'successes': 0,
                'total': 0
            }
        
        strat_stats = self.statistics['success_rate_by_strategy'][strategy]
        strat_stats['total'] += 1
        if experience.success:
            strat_stats['successes'] += 1
        strat_stats['rate'] = strat_stats['successes'] / strat_stats['total']
        
        # Actualizar tasa de éxito por tipo de archivo
        file_type = experience.file_type
        if file_type not in self.statistics['success_rate_by_file_type']:
            self.statistics['success_rate_by_file_type'][file_type] = {
                'successes': 0,
                'total': 0
            }
        
        file_stats = self.statistics['success_rate_by_file_type'][file_type]
        file_stats['total'] += 1
        if experience.success:
            file_stats['successes'] += 1
        file_stats['rate'] = file_stats['successes'] / file_stats['total']
        
        # Actualizar confianza promedio
        total_exp = self.statistics['total_experiences']
        current_avg = self.statistics['average_confidence']
        self.statistics['average_confidence'] = (
            (current_avg * (total_exp - 1) + experience.confidence_score) / total_exp
        )
    
    def _detect_patterns(self):
        """Detecta patrones recurrentes en las experiencias"""
        # Detectar problemas recurrentes
        problem_counts = defaultdict(lambda: {'count': 0, 'successes': 0, 'examples': []})
        
        for exp in self.experiences:
            key = exp.problem_hash
            problem_counts[key]['count'] += 1
            if exp.success:
                problem_counts[key]['successes'] += 1
            if len(problem_counts[key]['examples']) < 3:
                problem_counts[key]['examples'].append(exp.experience_id)
        
        # Crear patrones para problemas frecuentes (>= 3 ocurrencias)
        for problem_hash, data in problem_counts.items():
            if data['count'] >= 3:
                pattern_id = f"recurring_{problem_hash[:8]}"
                
                if pattern_id not in self.patterns:
                    success_rate = data['successes'] / data['count']
                    
                    pattern = PatternInsight(
                        pattern_id=pattern_id,
                        pattern_type='recurring_problem',
                        description=f"Problema recurrente detectado ({data['count']} ocurrencias)",
                        frequency=data['count'],
                        success_rate=success_rate,
                        recommended_action=self._generate_pattern_recommendation(success_rate),
                        examples=data['examples']
                    )
                    
                    self.patterns[pattern_id] = pattern
                    logger.info(f"Pattern detected: {pattern_id}")
    
    def _generate_pattern_recommendation(self, success_rate: float) -> str:
        """Genera recomendación basada en tasa de éxito del patrón"""
        if success_rate >= 0.8:
            return "Este problema se resuelve exitosamente la mayoría de las veces"
        elif success_rate >= 0.5:
            return "Tasa de éxito moderada, considerar estrategias alternativas"
        else:
            return "Baja tasa de éxito, revisar enfoque o solicitar intervención humana"
    
    def _get_top_insights(self, limit: int = 5) -> List[Dict]:
        """Obtiene los insights más importantes"""
        insights = []
        
        # Mejor estrategia global
        if self.statistics['success_rate_by_strategy']:
            best_strategy = max(
                self.statistics['success_rate_by_strategy'].items(),
                key=lambda x: x[1].get('rate', 0)
            )
            insights.append({
                'type': 'best_strategy',
                'message': f"Mejor estrategia: {best_strategy[0]} "
                          f"({best_strategy[1].get('rate', 0):.0%} éxito)"
            })
        
        # Tipo de tarea más exitoso
        if self.statistics['success_rate_by_type']:
            best_type = max(
                self.statistics['success_rate_by_type'].items(),
                key=lambda x: x[1].get('rate', 0)
            )
            insights.append({
                'type': 'best_task_type',
                'message': f"Tarea más exitosa: {best_type[0]} "
                          f"({best_type[1].get('rate', 0):.0%} éxito)"
            })
        
        # Patrones detectados
        recurring_patterns = [
            p for p in self.patterns.values()
            if p.pattern_type == 'recurring_problem'
        ]
        
        if recurring_patterns:
            insights.append({
                'type': 'patterns',
                'message': f"{len(recurring_patterns)} patrones recurrentes detectados"
            })
        
        return insights[:limit]
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en el aprendizaje"""
        recommendations = []
        
        total = self.statistics['total_experiences']
        
        if total < 10:
            recommendations.append(
                f"Sigue usando Kalin. Con más experiencia ({total}/50), "
                f"las recomendaciones serán más precisas."
            )
        else:
            # Recomendar mejor estrategia
            if self.statistics['success_rate_by_strategy']:
                best = max(
                    self.statistics['success_rate_by_strategy'].items(),
                    key=lambda x: x[1].get('rate', 0)
                )
                recommendations.append(
                    f"Para mejores resultados, usa estrategia '{best[0]}' "
                    f"({best[1].get('rate', 0):.0%} éxito)"
                )
            
            # Alertar sobre bajas tasas de éxito
            for task_type, stats in self.statistics['success_rate_by_type'].items():
                rate = stats.get('rate', 0)
                if rate < 0.5 and stats.get('total', 0) >= 5:
                    recommendations.append(
                        f"Baja tasa de éxito en '{task_type}' ({rate:.0%}). "
                        f"Considera revisar el enfoque."
                    )
        
        return recommendations
    
    def save(self):
        """Guarda toda la memoria en disco"""
        try:
            # Guardar experiencias
            with open(self.experiences_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [exp.to_dict() for exp in self.experiences],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            
            # Guardar patrones
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {k: v.to_dict() for k, v in self.patterns.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            
            # Guardar estadísticas
            with open(self.statistics_file, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Experience memory saved: {len(self.experiences)} experiences")
        
        except Exception as e:
            logger.error(f"Error saving experience memory: {e}")
    
    def _load(self):
        """Carga memoria desde disco"""
        try:
            # Cargar experiencias
            if os.path.exists(self.experiences_file):
                with open(self.experiences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.experiences = [Experience.from_dict(d) for d in data]
                    
                    # Reconstruir índices
                    for exp in self.experiences:
                        self._problem_index[exp.problem_hash].append(exp.experience_id)
                        self._type_index[exp.task_type].append(exp.experience_id)
                        self._file_type_index[exp.file_type].append(exp.experience_id)
            
            # Cargar patrones
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = {k: PatternInsight.from_dict(v) for k, v in data.items()}
            
            # Cargar estadísticas
            if os.path.exists(self.statistics_file):
                with open(self.statistics_file, 'r', encoding='utf-8') as f:
                    self.statistics = json.load(f)
            
            logger.info(f"Experience memory loaded: {len(self.experiences)} experiences")
        
        except Exception as e:
            logger.error(f"Error loading experience memory: {e}")
    
    def clear(self):
        """Limpia toda la memoria (útil para testing)"""
        self.experiences.clear()
        self.patterns.clear()
        self._problem_index.clear()
        self._type_index.clear()
        self._file_type_index.clear()
        self.statistics = {
            'total_experiences': 0,
            'total_successes': 0,
            'total_failures': 0,
            'success_rate_by_type': {},
            'success_rate_by_strategy': {},
            'success_rate_by_file_type': {},
            'average_confidence': 0.0,
            'most_common_problems': [],
            'best_strategies': {},
            'learning_started_at': time.time(),
            'last_updated': time.time()
        }
        self.save()
        logger.info("Experience memory cleared")


# Instancia global singleton
_instance = None

def get_experience_memory() -> ExperienceMemory:
    """Obtiene la instancia global de ExperienceMemory"""
    global _instance
    if _instance is None:
        _instance = ExperienceMemory()
    return _instance
