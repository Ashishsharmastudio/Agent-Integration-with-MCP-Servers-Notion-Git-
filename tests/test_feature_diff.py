# tests/test_feature_diff.py
from src.integrations.feature_diff import extract_features_from_text, compare_feature_sets

def test_extract_features_basic():
    text = """
# Features
- User login
- [x] Password reset
* Email notifications
1. Analytics dashboard
"""
    feats = extract_features_from_text(text)
    assert "user login" in feats
    assert "password reset" in feats
    assert "email notifications" in feats
    assert "analytics dashboard" in feats

def test_compare_sets():
    notion = "- login\n- reset password\n- search\n"
    code = "- login\n- search\n- export\n"
    only_n, only_c, overlap = compare_feature_sets(notion, code)
    assert "reset password" in only_n
    assert "export" in only_c
    assert "login" in overlap and "search" in overlap
