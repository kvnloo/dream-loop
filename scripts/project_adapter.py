"""Explicit trusted local policy adapter; never auto-discover project code.

DREAM_LOOP_ADAPTER must be an absolute Python path. Loading it executes code:
use only a file you trust, never an adapter named by an imported event.
"""
import importlib.util
import os
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace


@lru_cache(maxsize=16)
def _load(path):
    if not path:
        return SimpleNamespace()
    source = Path(path)
    if not source.is_absolute() or not source.is_file() or source.suffix != '.py':
        raise ValueError('DREAM_LOOP_ADAPTER must name an existing absolute .py file')
    spec = importlib.util.spec_from_file_location('_dream_loop_adapter', source)
    if spec is None or spec.loader is None:
        raise ValueError('Cannot load adapter')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_adapter():
    return _load(os.environ.get('DREAM_LOOP_ADAPTER', ''))


def hook(name, fallback, *args, **kwargs):
    return getattr(get_adapter(), name, fallback)(*args, **kwargs)


def setting(name, default):
    return getattr(get_adapter(), name, default)
