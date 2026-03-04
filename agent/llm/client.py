"""LLM client — OpenAI with Bedrock fallback on 429."""

import json
import logging
import os
from typing import Optional

from openai import APIError, AsyncOpenAI, RateLimitError
from openai import RateLimitError, APIError

logger = logging.getLogger(__name__)

_openai_client = None
_bedrock_available = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    return _openai_client


def _bedrock_available_check():
    global _bedrock_available
    if _bedrock_available is None:
        enabled = os.environ.get("BEDROCK_FALLBACK_ENABLED", "false").lower() == "true"
        has_aws = bool(os.environ.get("AWS_REGION"))
        _bedrock_available = enabled and has_aws
    return _bedrock_available


async def _call_bedrock(model_id: str, messages: list, temperature: float, max_tokens: int) -> str:
    """Call Amazon Bedrock (Claude) as fallback."""
    import asyncio
    try:
        import boto3
        from botocore.config import Config

        config = Config(retries={"mode": "standard", "max_attempts": 2})
        client = boto3.client("bedrock-runtime", region_name=os.environ.get("BEDROCK_REGION", "us-east-1"), config=config)

        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            else:
                parts.append(content)
        prompt = "\n\n".join(parts)

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            ),
        )
        result = json.loads(response["body"].read())
        text = result["content"][0]["text"]
        return text
    except Exception as e:
        logger.error("Bedrock fallback failed: %s", e)
        raise


async def chat_completion(
    model: str,
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    response_format: Optional[dict] = None,
) -> str:
    """
    Call LLM (OpenAI first, Bedrock fallback on 429).
    Returns the content string.
    """
    try:
        client = _get_openai()
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except (RateLimitError, APIError) as e:
        if _bedrock_available_check():
            logger.warning("OpenAI failed (%s), falling back to Bedrock", e)
            bedrock_model = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
            return await _call_bedrock(bedrock_model, messages, temperature, max_tokens)
        raise
