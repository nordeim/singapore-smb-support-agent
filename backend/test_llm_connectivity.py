"""Simple LLM connectivity test without database dependency.

This test focuses on verifying:
1. OpenRouter API key validity
2. LLM client instantiation
3. ChatOpenAI connectivity to OpenRouter
4. Model availability
5. Response generation capability
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from app.config import settings

    print(f"\n{'=' * 60}")
    print(f"LLM CONNECTIVITY TEST - {datetime.now().isoformat()}")
    print(f"{'=' * 60}")

    # Environment Check
    print(f"\n[ENVIRONMENT CHECK]")
    print(f"{'=' * 50}")
    print(
        f"OpenRouter API Key: {settings.OPENROUTER_API_KEY[:20]}...{settings.OPENROUTER_API_KEY[-4:]}"
    )
    print(f"OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"LLM Model Primary: {settings.LLM_MODEL_PRIMARY}")
    print(f"LLM Temperature: {settings.LLM_TEMPERATURE}")
    print(f"\n{'=' * 50}")

    # LLM Initialization Test
    print(f"\n[LLM INITIALIZATION]")
    print(f"{'=' * 50}")

    llm = ChatOpenAI(
        model=settings.LLM_MODEL_PRIMARY,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
    )

    print(f"✓ ChatOpenAI client initialized")
    print(f"✓ Model: {llm.model_name}")
    print(f"✓ Temperature: {llm.temperature}")
    print(f"\n{'=' * 50}")

    # Test Query
    test_query = "Hello, can you tell me about your services?"

    print(f"\n[CONNECTIVITY TEST]")
    print(f"{'=' * 50}")
    print(f"Test Query: '{test_query}'")
    print(f"\n{'=' * 50}")

    # Invoke LLM
    print(f"Sending request to OpenRouter...")
    print(f"{'=' * 50}")

    response = llm.invoke(test_query)

    print(f"\n{'=' * 50}")
    print(f"[RESPONSE RECEIVED]")
    print(f"{'=' * 50}")
    print(f"✓ LLM Response Received Successfully!")
    print(f"\n{'=' * 50}")

    # Response Details
    print(f"Response Type: {type(response).__name__}")
    print(f"Response Length: {len(response.content)} characters")
    print(f"Response Content: {response.content[:200]}")
    if len(response.content) > 200:
        print(f"    ... ({len(response.content) - 200} more characters)")
    print(f"\n{'=' * 50}")

    # Success Indicators
    print(f"\n[SUCCESS CRITERIA]")
    print(f"{'=' * 50}")
    print(f"✓ OpenRouter API Key: VALID")
    print(f"✓ Base URL: ACCESSIBLE")
    print(f"✓ LLM Model: AVAILABLE")
    print(f"✓ Response Generation: WORKING")
    print(f"\n{'=' * 50}")

    print(f"\n[TEST SUMMARY]")
    print(f"{'=' * 50}")
    print(f"Status: ✅ LLM CONNECTIVITY VERIFIED")
    print(f"Result: Singapore SMB Support Agent can communicate with OpenRouter API")
    print(f"Next Step: Agent ready for knowledge retrieval testing")
    print(f"{'=' * 60}")

except ImportError as e:
    print(f"\n[IMPORT ERROR]")
    print(f"{'=' * 50}")
    print(f"✗ Failed to import ChatOpenAI: {str(e)}")
    print(f"\nTroubleshooting:")
    print(f"  1. Install: pip install langchain-openai")
    print(f"  2. Check Python version: {__import__('sys').version}")
    print(f"{'=' * 60}")

except Exception as e:
    print(f"\n[CONNECTIVITY ERROR]")
    print(f"{'=' * 50}")
    print(f"✗ Failed to connect to OpenRouter API")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print(f"\nTroubleshooting:")
    print(f"  1. Check API Key: {settings.OPENROUTER_API_KEY[:20]}...")
    print(f"  2. Check internet connection")
    print(f"  3. Verify OpenRouter status: https://status.openrouter.ai")
    print(f"  4. Check model availability: {settings.LLM_MODEL_PRIMARY}")
    print(f"{'=' * 60}")

print(f"\n{'=' * 60}")
print(f"[TEST COMPLETE]")
print(f"{'=' * 60}")
