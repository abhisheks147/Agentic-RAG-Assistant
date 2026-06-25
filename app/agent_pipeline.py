import os
import json
from app.vectorstore import retrieve
from app.config import settings
from openai import OpenAI, RateLimitError


def get_llm_client(api_key: str | None = None):
    api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    print("🔥 GEMINI KEY LOADED:", bool(api_key))
    if api_key:
        print("🔥 Gemini API key received")

    if not api_key or api_key.strip() == "" or "your_" in api_key:
        raise ValueError("Invalid or missing GEMINI_API_KEY")

    llm = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model_name = settings.LLM_MODEL

    if "gemini" not in model_name.lower():
        model_name = "gemini-1.5-flash"

    print(f"✅ Using Gemini model: {model_name}")

    return llm, model_name


def retrieval_agent(query: str, k: int = 5):
    return retrieve(query, k=k)


def reasoning_agent(query: str, context_docs: list[dict], llm: OpenAI, model_name: str):
    context_text = (
        "No relevant context found in vector database."
        if not context_docs
        else "\n\n---\n\n".join(
            f"Document {i+1}: {d['text']}"
            for i, d in enumerate(context_docs)
        )
    )

    prompt = f"""
You are an expert educational assistant.

Use ONLY the provided context to answer.

Requirements:
- Give a detailed answer.
- Explain concepts thoroughly.
- Include examples whenever possible.
- Use bullet points and headings.
- Do not give one-line answers.
- If generating MCQs, provide all questions completely.
- If summarizing, provide a comprehensive summary.

Question:
{query}

Context:
{context_text}

Give a clear and accurate answer.
"""

    try:
        resp = llm.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )

        return resp.choices[0].message.content

    except RateLimitError:
        return "__QUOTA_EXCEEDED__"

    except Exception as e:
        return f"__ERROR__:{str(e)}"


def verification_agent(answer: str, context_docs: list[dict], llm: OpenAI, model_name: str):
    context_text = "\n\n".join(
        [d["text"] for d in context_docs]
    ) if context_docs else "No context."

    prompt = f"""
Return JSON only:

{{
  "supported": true or false,
  "notes": "short explanation"
}}

Answer:
{answer}

Context:
{context_text}
"""

    try:
        resp = llm.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        return resp.choices[0].message.content

    except Exception as e:
        return json.dumps({
            "supported": False,
            "notes": str(e)
        })


def agent_pipeline(query: str, api_key: str | None = None):
    llm, model_name = get_llm_client(api_key=api_key)

    docs = retrieval_agent(query)

    draft = reasoning_agent(query, docs, llm, model_name)

    if draft == "__QUOTA_EXCEEDED__":
        return {
            "error": True,
            "message": "🚫 Gemini API quota exceeded. Please wait a few minutes and try again."
        }

    if draft.startswith("__ERROR__:"):
        return {
            "error": True,
            "message": draft.replace("__ERROR__:", "")
        }

    verification = verification_agent(
        draft,
        docs,
        llm,
        model_name
    )

    sources = list({
        d.get("metadata", {}).get("filename", "Unknown")
        for d in docs
    })

    try:
        verification_json = json.loads(verification)
    except Exception:
        verification_json = {
            "supported": None,
            "notes": verification
        }

    return {
        "answer": draft,
        "verification": verification_json,
        "sources": sources
    }