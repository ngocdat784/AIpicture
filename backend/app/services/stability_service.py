import requests

from app.config import settings


STABILITY_API_URL = (
    "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
)


def edit_image(
    image_bytes: bytes,
    filename: str,
    search_prompt: str,
    prompt: str,
) -> bytes:
    files = {
        "image": (
            filename,
            image_bytes,
            "image/png",
        )
    }

    data = {
        "search_prompt": search_prompt,
        "prompt": prompt,
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
            error_message = str(error_data)
        except Exception:
            error_message = response.text

        raise Exception(
            f"Stability AI error ({response.status_code}): "
            f"{error_message}"
        )

    return response.content