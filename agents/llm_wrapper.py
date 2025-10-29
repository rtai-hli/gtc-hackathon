"""
LLM Wrapper with Reasoning Token Support

Provides a clean interface for agents to use LLMs with thinking/reasoning capabilities.
Specifically optimized for nvidia-nemotron-nano-9b-v2 with streaming reasoning content.
"""

import os
from typing import Optional, Dict, Any, AsyncIterator
from openai import AsyncOpenAI

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass


class ReasoningLLM:
    """
    Wrapper for LLMs with reasoning token support

    Features:
    - Streaming reasoning content display
    - Configurable thinking token budgets
    - Automatic model selection
    - Clean async interface
    """

    def __init__(
        self,
        model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        min_thinking_tokens: int = 512,
        max_thinking_tokens: int = 2048
    ):
        """
        Initialize LLM wrapper

        Args:
            model: Model identifier (default: nvidia/llama-3.3-nemotron-super-49b-v1.5)
            base_url: API base URL (default: NVIDIA integrate API)
            api_key: API key (default: from NVIDIA_API_KEY env var)
            min_thinking_tokens: Minimum tokens for reasoning
            max_thinking_tokens: Maximum tokens for reasoning
        """
        self.model = model
        self.min_thinking_tokens = min_thinking_tokens
        self.max_thinking_tokens = max_thinking_tokens

        # Configure client
        if base_url is None:
            base_url = "https://integrate.api.nvidia.com/v1"

        if api_key is None:
            api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY")

        if not api_key:
            raise ValueError(
                "No API key found. Set NVIDIA_API_KEY or NGC_API_KEY environment variable"
            )

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )

    async def think_and_respond(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.6,
        top_p: float = 0.95,
        max_tokens: int = 2048,
        stream: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate response with thinking process

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum response tokens
            stream: Whether to stream the response

        Yields:
            Dicts with 'type' ('reasoning' or 'content') and 'text'
        """

        # Add system message for thinking mode if not present
        if not any(msg.get("role") == "system" for msg in messages):
            messages = [{"role": "system", "content": "/think"}] + messages

        # Create completion
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream,
            extra_body={
                "min_thinking_tokens": self.min_thinking_tokens,
                "max_thinking_tokens": self.max_thinking_tokens
            }
        )

        if stream:
            async for chunk in completion:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Handle reasoning content
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    yield {
                        "type": "reasoning",
                        "text": reasoning,
                        "model": self.model
                    }

                # Handle regular content
                if delta.content:
                    yield {
                        "type": "content",
                        "text": delta.content,
                        "model": self.model
                    }
        else:
            # Non-streaming mode
            response = completion.choices[0].message

            # Check for reasoning content
            reasoning = getattr(response, "reasoning_content", None)
            if reasoning:
                yield {
                    "type": "reasoning",
                    "text": reasoning,
                    "model": self.model
                }

            if response.content:
                yield {
                    "type": "content",
                    "text": response.content,
                    "model": self.model
                }

    async def simple_query(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple synchronous query (non-streaming, returns just content)

        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional arguments for think_and_respond

        Returns:
            Response content as string
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        content_parts = []
        async for chunk in self.think_and_respond(messages, stream=True, **kwargs):
            if chunk["type"] == "content":
                content_parts.append(chunk["text"])

        return "".join(content_parts)


# Convenience function for creating instances
def create_reasoning_llm(
    model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    **kwargs
) -> ReasoningLLM:
    """
    Create a ReasoningLLM instance with sensible defaults

    Args:
        model: Model identifier
        **kwargs: Additional arguments for ReasoningLLM

    Returns:
        Configured ReasoningLLM instance
    """
    return ReasoningLLM(model=model, **kwargs)
