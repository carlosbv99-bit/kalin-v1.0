from typing import Dict
from agent.llm.provider_manager import get_manager


def generate(prompt: str, max_tokens: int = 300, use_case: str = "fix") -> str:
    manager = get_manager()
    response = manager.generate(prompt, use_case=use_case, max_tokens=max_tokens)
    return response.text if response else ""


def is_available() -> bool:
    manager = get_manager()
    status = manager.get_provider_status()
    return any(status.values())


def get_stats() -> Dict:
    manager = get_manager()
    return manager.get_stats()


def get_provider_status() -> Dict[str, bool]:
    manager = get_manager()
    return manager.get_provider_status()
