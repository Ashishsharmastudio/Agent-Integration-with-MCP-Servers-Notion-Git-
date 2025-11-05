# tests/test_reasoning.py
from src.agent_core.reasoning import ReasoningEngine

def test_analyze_query_without_api_key(monkeypatch):
    # No OPENAI_API_KEY -> passthrough
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    eng = ReasoningEngine()
    res = eng.analyze_query("compare features")
    assert isinstance(res["notion_query"], str)
    assert isinstance(res["git_query"], str)
