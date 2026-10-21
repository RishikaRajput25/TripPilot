
# import json

# from config import GEMINI_API_KEY, GROQ_API_KEY


# def get_ai_provider():
#     if GEMINI_API_KEY:
#         return "gemini"
#     if GROQ_API_KEY:
#         return "groq"
#     return "demo"


# def generate_json(prompt: str) -> dict:
#     provider = get_ai_provider()

#     if provider == "demo":
#         return {
#             "message": "Demo mode is active. Add an API key to enable AI."
#         }

#     try:
#         if provider == "gemini":
#             from google import genai

#             client = genai.Client(api_key=GEMINI_API_KEY)

#             response = client.models.generate_content(
#                 model="gemini-3.8-flash",
#                 contents=prompt,
#                 config={"response_mime_type": "application/json"},
#             )

#             content = response.text

#         else:
#             from groq import Groq

#             client = Groq(api_key=GROQ_API_KEY)

#             response = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "Return valid JSON only."
#                     },
#                     {"role": "user", "content": prompt},
#                 ],
#                 response_format={"type": "json_object"},
#             )

#             content = response.choices[0].message.content

#         result = json.loads(content)

#         if not isinstance(result, dict):
#             raise ValueError("AI response must be a JSON object.")

#         return result

#     except Exception as exc:
#         raise RuntimeError(
#             f"AI generation failed ({provider}): {exc}"
#         ) from exc



import json

from config import GEMINI_API_KEY, GROQ_API_KEY


def get_ai_provider():
    """Prefer Groq; use Gemini only if Groq key is unavailable."""
    if GROQ_API_KEY:
        return "groq"
    if GEMINI_API_KEY:
        return "gemini"
    return "demo"


def generate_json(prompt: str) -> dict:
    """Generate a JSON response using Groq or Gemini."""
    provider = get_ai_provider()

    if provider == "demo":
        return {
            "message": "Demo mode is active. Add a Groq or Gemini API key."
        }

    try:
        if provider == "groq":
            from groq import Groq

            client = Groq(api_key=GROQ_API_KEY)

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return valid JSON only. "
                            "Do not include Markdown or explanations."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

        else:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )

            content = response.text

        if not content:
            raise ValueError("The AI provider returned an empty response.")

        result = json.loads(content)

        if not isinstance(result, dict):
            raise ValueError("AI response must be a JSON object.")

        return result

    except Exception as exc:
        raise RuntimeError(
            f"AI generation failed ({provider}): {exc}"
        ) from exc
