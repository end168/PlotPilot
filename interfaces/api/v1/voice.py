"""Voice API 路由"""
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional

from application.services.voice_sample_service import VoiceSampleService
from interfaces.api.dependencies import get_voice_sample_service
from domain.shared.exceptions import EntityNotFoundError


router = APIRouter(tags=["voice"])


# Request Models
class VoiceSampleRequest(BaseModel):
    """文风样本请求"""
    ai_original: str = Field(..., min_length=1, description="AI 原文")
    author_refined: str = Field(..., min_length=1, description="作者改稿")
    chapter_number: int = Field(..., ge=1, description="章节号")
    scene_type: Optional[str] = Field(default="general", description="场景类型")


# Response Models
class VoiceSampleResponse(BaseModel):
    """文风样本响应"""
    sample_id: str = Field(..., description="样本 ID")


@router.post(
    "/novels/{novel_id}/voice/samples",
    response_model=VoiceSampleResponse,
    status_code=201,
    summary="创建文风样本",
    description="添加 AI 原文和作者改稿的文风样本对"
)
def create_voice_sample(
    novel_id: str = Path(..., description="小说 ID"),
    request: VoiceSampleRequest = ...,
    service: VoiceSampleService = Depends(get_voice_sample_service)
) -> VoiceSampleResponse:
    """
    创建文风样本

    Args:
        novel_id: 小说 ID
        request: 文风样本请求
        service: 文风样本服务

    Returns:
        VoiceSampleResponse: 包含样本 ID 的响应
    """
    try:
        sample_id = service.append_sample(
            novel_id=novel_id,
            chapter_number=request.chapter_number,
            scene_type=request.scene_type,
            ai_original=request.ai_original,
            author_refined=request.author_refined
        )
        return VoiceSampleResponse(sample_id=sample_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create voice sample: {str(e)}")
