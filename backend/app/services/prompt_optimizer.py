from pydantic import BaseModel, Field
from google import genai

from app.config import settings


GEMINI_MODEL = "gemini-3.5-flash-lite"


class OptimizedPrompt(BaseModel):
    search_prompt: str = Field(
        description=(
            "A concise English description of the exact object or area "
            "to find in the image."
        )
    )

    prompt: str = Field(
        description=(
            "A clear English image-editing instruction describing exactly "
            "what should be changed while preserving everything the user "
            "did not ask to change."
        )
    )


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


SYSTEM_INSTRUCTION = """
You are an expert image-editing prompt optimizer.

Your job is to convert a Vietnamese user's image-editing request
into precise English prompts for an image editing model.

You receive:
1. search_prompt: the object or area that should be located in the image.
2. prompt: what the user wants to change.

Rules:

- Translate Vietnamese into natural, precise English.
- Preserve the user's exact intent.
- Do NOT invent objects, actions, colors, styles, or details
  that the user did not request.
- Do NOT remove requirements from the user's request.
- If the user says to preserve something, explicitly preserve it.
- Keep search_prompt concise and visually identifiable.
- search_prompt must describe the actual object or area in the image.
- Do not use vague phrases such as "the object to modify".
- Make the editing prompt clear and suitable for an image editing model.
- Preserve composition, perspective, lighting, identity, and other
  image properties when the user asks to keep them unchanged.
- If the user's request is already in English, improve its clarity
  without changing its meaning.
- Return only the requested structured JSON output.
"""


def optimize_prompt(
    search_prompt: str,
    prompt: str,
) -> OptimizedPrompt:

    user_input = f"""
Original search target:
{search_prompt}

Original editing request:
{prompt}
"""

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=SYSTEM_INSTRUCTION + "\n" + user_input,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": OptimizedPrompt.model_json_schema(),
        },
    )

    if not interaction.output_text:
        raise Exception(
            "Gemini did not return an optimized prompt."
        )

    try:
        return OptimizedPrompt.model_validate_json(
            interaction.output_text
        )
    except Exception as e:
        raise Exception(
            f"Invalid Gemini response: {str(e)}"
        )