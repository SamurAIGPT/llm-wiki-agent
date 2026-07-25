from __future__ import annotations

import sys
import types

from tools import _utils

_ATLAS_ENV_NAMES = (
    "ATLASCLOUD_API_KEY",
    "ATLAS_CLOUD_API_KEY",
    "ATLASCLOUD_BASE_URL",
    "ATLAS_CLOUD_BASE_URL",
    "ATLAS_BASE_URL",
)


class _Message:
    content = "atlas response"


class _Choice:
    message = _Message()


class _Response:
    choices = [_Choice()]


def _install_fake_litellm(monkeypatch):
    calls = []
    fake = types.ModuleType("litellm")

    def completion(**kwargs):
        calls.append(kwargs)
        return _Response()

    fake.completion = completion
    monkeypatch.setitem(sys.modules, "litellm", fake)
    return calls


def _clear_atlas_env(monkeypatch):
    for name in _ATLAS_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_atlas_cloud_model_alias_sets_openai_compatible_kwargs(monkeypatch):
    _clear_atlas_env(monkeypatch)
    calls = _install_fake_litellm(monkeypatch)
    monkeypatch.setenv("LLM_MODEL", "atlascloud/deepseek-ai/deepseek-v4-pro")
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "atlas-key")
    monkeypatch.setenv("ATLASCLOUD_BASE_URL", "https://example.test/v1/")

    result = _utils.call_llm("summarize this", max_tokens=128)

    assert result == "atlas response"
    assert calls == [
        {
            "model": "openai/deepseek-ai/deepseek-v4-pro",
            "api_base": "https://example.test/v1",
            "api_key": "atlas-key",
            "messages": [{"role": "user", "content": "summarize this"}],
            "max_tokens": 128,
        }
    ]


def test_atlas_cloud_short_alias_uses_default_model_and_env_key_alias(
    monkeypatch,
):
    _clear_atlas_env(monkeypatch)
    calls = _install_fake_litellm(monkeypatch)
    monkeypatch.setenv("LLM_MODEL", "atlas")
    monkeypatch.setenv("ATLAS_CLOUD_API_KEY", "alias-key")

    _utils.call_llm("query", max_tokens=0)

    assert calls == [
        {
            "model": "openai/qwen/qwen3.5-flash",
            "api_base": "https://api.atlascloud.ai/v1",
            "api_key": "alias-key",
            "messages": [{"role": "user", "content": "query"}],
        }
    ]


def test_non_atlas_model_preserves_existing_litellm_model(monkeypatch):
    _clear_atlas_env(monkeypatch)
    calls = _install_fake_litellm(monkeypatch)
    monkeypatch.setenv("LLM_MODEL", "claude-3-5-sonnet-latest")
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "unused")

    _utils.call_llm("query", max_tokens=32)

    assert calls[0]["model"] == "claude-3-5-sonnet-latest"
    assert "api_base" not in calls[0]
    assert "api_key" not in calls[0]
