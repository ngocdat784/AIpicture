import base64

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.openai_service import edit_image


router = APIRouter(
    prefix="/api/images",
    tags=["Images"],
)


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.post("/edit")
async def edit_image_endpoint(
    image: UploadFile = File(...),
    prompt: str = Form(...),
):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ JPG, PNG hoặc WebP.",
        )

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt không được để trống.",
        )

    if len(prompt) > 32000:
        raise HTTPException(
            status_code=400,
            detail="Prompt quá dài.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="File ảnh không hợp lệ.",
        )

    try:
        result = edit_image(
            image_bytes=image_bytes,
            filename=image.filename or "image.png",
            prompt=prompt,
        )

        image_data = result.data[0].b64_json

        if not image_data:
            raise HTTPException(
                status_code=500,
                detail="OpenAI không trả về ảnh.",
            )

        output_bytes = base64.b64decode(image_data)

        return Response(
            content=output_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=edited-image.png"
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image editing failed: {str(e)}",
        )