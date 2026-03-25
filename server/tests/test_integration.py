"""Integration tests for MiniMax LLM provider.

These tests verify the MiniMax integration works end-to-end.
They require a valid MINIMAX_API_KEY environment variable.
Skip with: pytest -m "not integration"
"""

import os
import sys
import unittest

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')


def requires_minimax_key(func):
    """Skip test if MINIMAX_API_KEY is not set."""
    return unittest.skipUnless(
        MINIMAX_API_KEY,
        "MINIMAX_API_KEY not set"
    )(func)


class TestMiniMaxIntegration(unittest.TestCase):
    """Integration tests for MiniMax provider via create_chat_model."""

    @requires_minimax_key
    def test_minimax_chat_completion(self):
        """Test that MiniMax can handle a basic chat completion."""
        from llm_provider import create_chat_model
        from langchain.schema import HumanMessage

        model = create_chat_model(
            provider="minimax",
            api_key=MINIMAX_API_KEY,
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.1,
        )
        response = model([HumanMessage(content="Say hello in one word.")])
        self.assertIsNotNone(response.content)
        self.assertGreater(len(response.content), 0)

    @requires_minimax_key
    def test_minimax_multi_turn(self):
        """Test that MiniMax handles multi-turn conversations."""
        from llm_provider import create_chat_model
        from langchain.schema import HumanMessage, SystemMessage

        model = create_chat_model(
            provider="minimax",
            api_key=MINIMAX_API_KEY,
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.1,
        )
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is 2+2? Answer with just the number."),
        ]
        response = model(messages)
        self.assertIn("4", response.content)

    @requires_minimax_key
    def test_minimax_camel_agent_flow(self):
        """Test MiniMax works with the CAMELAgent class."""
        from llm_provider import create_chat_model
        from langchain.schema import HumanMessage, SystemMessage

        model = create_chat_model(
            provider="minimax",
            api_key=MINIMAX_API_KEY,
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.2,
        )

        # Simulate CAMELAgent init + step
        sys_msg = SystemMessage(content="You are a helpful coding assistant.")
        stored_messages = [sys_msg]

        input_msg = HumanMessage(content="Write a Python hello world one-liner.")
        stored_messages.append(input_msg)

        output = model(stored_messages)
        stored_messages.append(output)

        self.assertIsNotNone(output.content)
        self.assertGreater(len(output.content), 0)
        self.assertEqual(len(stored_messages), 3)


if __name__ == '__main__':
    unittest.main()
