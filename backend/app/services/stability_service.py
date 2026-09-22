import requests

from app.config import settings


STABILITY_API_URL = (
    "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
)


def edit_image(
    image_bytes: bytes,
    filename: str,
    prompt: str,
):
    files = {
        "image": (
            filename,
            image_bytes,
            "image/png",
        )
    }

    data = {
        "prompt": prompt,
        "search_prompt": "the object or area to modify",
        "output_format": "png",
    }

    headers = {
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
        "Accept": "image/*",
    }

    response = requests.post(
        STABILITY_API_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=120,
    )

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get(
                "message",
                "Unknown Stability AI error",
            )
        except Exception:
            error_message = response.text

        raise Exception(
            f"Stability AI error ({response.status_code}): "
            f"{error_message}"
        )

    return response.content