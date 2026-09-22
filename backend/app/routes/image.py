from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.prompt_optimizer import optimize_prompt
from app.services.stability_service import edit_image


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
    search_prompt: str = Form(...),
    prompt: str = Form(...),
):
    # Kiểm tra loại ảnh
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ JPG, PNG hoặc WebP.",
        )

    # Kiểm tra search prompt
    if not search_prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Đối tượng cần chỉnh sửa không được để trống.",
        )

    # Kiểm tra prompt
    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt không được để trống.",
        )

    # Giới hạn độ dài
    if len(search_prompt) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Search prompt quá dài.",
        )

    if len(prompt) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Prompt quá dài.",
        )

    # Đọc ảnh
    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="File ảnh không hợp lệ.",
        )

    try:
        # ==============================
        # STEP 1: Optimize prompt
        # ==============================

        optimized = optimize_prompt(
            search_prompt=search_prompt,
            prompt=prompt,
        )

        # ==============================
        # STEP 2: Stability AI
        # ==============================

        output_bytes = edit_image(
            image_bytes=image_bytes,
            filename=image.filename or "image.png",
            search_prompt=optimized.search_prompt,
            prompt=optimized.prompt,
        )

        return Response(
            content=output_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": (
                    "inline; filename=edited-image.png"
                )
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image editing failed: {str(e)}",
        )