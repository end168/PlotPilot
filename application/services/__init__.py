"""应用层服务"""
from application.services.novel_service import NovelService
from application.services.indexing_service import IndexingService

__all__ = ["NovelService", "IndexingService"]
