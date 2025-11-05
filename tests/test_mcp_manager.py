# tests/test_mcp_manager.py
import os
import importlib
import types

def test_split_owner_repo(monkeypatch):
    monkeypatch.setenv("GITHUB_REPO", "owner/name")
    mcp_mod = importlib.import_module("src.integrations.mcp_manager")
    m = mcp_mod.get_mcp_manager()
    assert m._split_owner_repo("owner/name") == ("owner", "name")

def test_no_startup_without_env(monkeypatch):
    # Ensure start methods raise when tokens missing
    monkeypatch.delenv("GITHUB_PERSONAL_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    mcp_mod = importlib.import_module("src.integrations.mcp_manager")
    m = mcp_mod.get_mcp_manager()
    try:
        m.start_github()
        assert False, "Expected RuntimeError when token missing"
    except RuntimeError:
        pass
    try:
        m.start_notion()
        assert False, "Expected RuntimeError when token missing"
    except RuntimeError:
        pass
