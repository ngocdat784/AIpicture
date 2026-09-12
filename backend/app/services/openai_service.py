from io import BytesIO

from openai import OpenAI

from app.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def edit_image(
    image_bytes: bytes,
    filename: str,
    prompt: str,
):
    image_file = BytesIO(image_bytes)
    image_file.name = filename

    result = client.images.edit(
        model="gpt-image-2.5-sunburst",
        image=image_file,
        prompt=prompt,
        quality="medium",
        output_format="png",
    )

    return result