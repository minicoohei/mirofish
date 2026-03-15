"""
CLI tools for MiroFish CC Layer.

All CLIs follow the same contract:
- Input: argparse arguments (JSON strings or file paths)
- Output: stdout JSON (success) or stderr log + exit code 1 (failure)
"""
import sys
import types

# Provide a stub for 'openai' if not installed, so modules that import
# `from openai import OpenAI` at module level don't crash.  The stub's
# OpenAI class will raise on instantiation, but module-level import succeeds.
if 'openai' not in sys.modules:
    try:
        import openai as _openai  # noqa: F401 — real package available
    except ImportError:
        _openai_stub = types.ModuleType('openai')

        class _OpenAIStub:
            def __init__(self, *a, **kw):
                raise ImportError(
                    "openai package is not installed. "
                    "Install it with: pip install openai"
                )

        _openai_stub.OpenAI = _OpenAIStub
        sys.modules['openai'] = _openai_stub

# Provide a stub for 'tavily' if not installed.
if 'tavily' not in sys.modules:
    try:
        import tavily as _tavily  # noqa: F401
    except ImportError:
        _tavily_stub = types.ModuleType('tavily')

        class _TavilyClientStub:
            def __init__(self, *a, **kw):
                raise ImportError(
                    "tavily-python package is not installed. "
                    "Install it with: pip install tavily-python"
                )

        _tavily_stub.TavilyClient = _TavilyClientStub
        sys.modules['tavily'] = _tavily_stub
