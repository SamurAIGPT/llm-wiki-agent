"""Unit tests for llm_provider module."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm_provider import (
    create_chat_model,
    clamp_temperature,
    PROVIDER_OPENAI,
    PROVIDER_MINIMAX,
    SUPPORTED_PROVIDERS,
    DEFAULT_MODELS,
    AVAILABLE_MODELS,
    MINIMAX_API_BASE,
)


class TestConstants(unittest.TestCase):
    """Test provider constants are properly defined."""

    def test_supported_providers_includes_openai(self):
        self.assertIn(PROVIDER_OPENAI, SUPPORTED_PROVIDERS)

    def test_supported_providers_includes_minimax(self):
        self.assertIn(PROVIDER_MINIMAX, SUPPORTED_PROVIDERS)

    def test_default_models_defined(self):
        self.assertIn(PROVIDER_OPENAI, DEFAULT_MODELS)
        self.assertIn(PROVIDER_MINIMAX, DEFAULT_MODELS)

    def test_minimax_default_model(self):
        self.assertEqual(DEFAULT_MODELS[PROVIDER_MINIMAX], "MiniMax-M2.5")

    def test_available_models_minimax(self):
        models = AVAILABLE_MODELS[PROVIDER_MINIMAX]
        self.assertIn("MiniMax-M2.5", models)
        self.assertIn("MiniMax-M2.5-highspeed", models)

    def test_minimax_api_base(self):
        self.assertEqual(MINIMAX_API_BASE, "https://api.minimax.io/v1")


class TestClampTemperature(unittest.TestCase):
    """Test temperature clamping for different providers."""

    def test_openai_no_clamp(self):
        self.assertEqual(clamp_temperature(1.5, PROVIDER_OPENAI), 1.5)

    def test_minimax_clamp_high(self):
        self.assertEqual(clamp_temperature(1.5, PROVIDER_MINIMAX), 1.0)

    def test_minimax_clamp_low(self):
        self.assertEqual(clamp_temperature(-0.5, PROVIDER_MINIMAX), 0.0)

    def test_minimax_valid_temp(self):
        self.assertEqual(clamp_temperature(0.5, PROVIDER_MINIMAX), 0.5)

    def test_minimax_zero_temp(self):
        self.assertEqual(clamp_temperature(0.0, PROVIDER_MINIMAX), 0.0)

    def test_minimax_one_temp(self):
        self.assertEqual(clamp_temperature(1.0, PROVIDER_MINIMAX), 1.0)

    def test_openai_zero_temp(self):
        self.assertEqual(clamp_temperature(0.0, PROVIDER_OPENAI), 0.0)


class TestCreateChatModel(unittest.TestCase):
    """Test create_chat_model factory function."""

    @patch('llm_provider.ChatOpenAI')
    def test_default_provider_is_openai(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(api_key="sk-test")
        mock_chat.assert_called_once_with(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_openai_provider(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(provider="openai", api_key="sk-test", temperature=0.5)
        mock_chat.assert_called_once_with(
            model_name="gpt-3.5-turbo",
            temperature=0.5,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_minimax_provider(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(
            provider="minimax",
            api_key="mm-test-key",
            temperature=0.3,
        )
        mock_chat.assert_called_once_with(
            openai_api_key="mm-test-key",
            openai_api_base="https://api.minimax.io/v1",
            model_name="MiniMax-M2.5",
            temperature=0.3,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_minimax_custom_model(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(
            provider="minimax",
            api_key="mm-key",
            model_name="MiniMax-M2.5-highspeed",
        )
        mock_chat.assert_called_once_with(
            openai_api_key="mm-key",
            openai_api_base="https://api.minimax.io/v1",
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.2,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_minimax_temp_clamped(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(
            provider="minimax",
            api_key="mm-key",
            temperature=1.5,
        )
        mock_chat.assert_called_once_with(
            openai_api_key="mm-key",
            openai_api_base="https://api.minimax.io/v1",
            model_name="MiniMax-M2.5",
            temperature=1.0,
        )

    def test_unsupported_provider_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_chat_model(provider="unsupported")
        self.assertIn("Unsupported provider", str(ctx.exception))

    @patch('llm_provider.ChatOpenAI')
    @patch.dict(os.environ, {"MINIMAX_API_KEY": "env-mm-key"})
    def test_minimax_env_fallback(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(provider="minimax")
        mock_chat.assert_called_once_with(
            openai_api_key="env-mm-key",
            openai_api_base="https://api.minimax.io/v1",
            model_name="MiniMax-M2.5",
            temperature=0.2,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_none_provider_defaults_openai(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(provider=None, api_key="sk-test")
        mock_chat.assert_called_once_with(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
        )

    @patch('llm_provider.ChatOpenAI')
    def test_openai_custom_model(self, mock_chat):
        mock_chat.return_value = MagicMock()
        create_chat_model(provider="openai", api_key="sk-test", model_name="gpt-4")
        mock_chat.assert_called_once_with(
            model_name="gpt-4",
            temperature=0.2,
        )


class TestProviderModelLists(unittest.TestCase):
    """Test that model lists are consistent."""

    def test_default_model_in_available(self):
        for provider in SUPPORTED_PROVIDERS:
            self.assertIn(
                DEFAULT_MODELS[provider],
                AVAILABLE_MODELS[provider],
                f"Default model for {provider} not in available models",
            )

    def test_all_providers_have_defaults(self):
        for provider in SUPPORTED_PROVIDERS:
            self.assertIn(provider, DEFAULT_MODELS)

    def test_all_providers_have_available_models(self):
        for provider in SUPPORTED_PROVIDERS:
            self.assertIn(provider, AVAILABLE_MODELS)
            self.assertGreater(len(AVAILABLE_MODELS[provider]), 0)


if __name__ == '__main__':
    unittest.main()
