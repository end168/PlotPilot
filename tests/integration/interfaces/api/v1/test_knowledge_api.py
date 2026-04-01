"""Knowledge API 集成测试

测试 Knowledge API 端点的集成功能。
"""
import pytest
from fastapi.testclient import TestClient
import shutil
from pathlib import Path
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_novel_repository import FileNovelRepository
from infrastructure.persistence.repositories.file_chapter_repository import FileChapterRepository
from infrastructure.persistence.repositories.file_knowledge_repository import FileKnowledgeRepository
from application.services.novel_service import NovelService
from application.services.knowledge_service import KnowledgeService
from interfaces.api.dependencies import get_novel_service, get_knowledge_service
from interfaces.main import app


# Global variables to hold test services
_test_novel_service = None
_test_knowledge_service = None


def get_test_novel_service():
    """Get test novel service"""
    return _test_novel_service


def get_test_knowledge_service():
    """Get test knowledge service"""
    return _test_knowledge_service


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """设置测试环境"""
    global _test_novel_service, _test_knowledge_service

    test_data = tmp_path / "data"
    test_data.mkdir()

    # 创建测试存储和仓储
    storage = FileStorage(test_data)
    novel_repo = FileNovelRepository(storage)
    chapter_repo = FileChapterRepository(storage)
    knowledge_repo = FileKnowledgeRepository(storage)

    # 创建服务
    _test_novel_service = NovelService(novel_repo, chapter_repo)
    _test_knowledge_service = KnowledgeService(knowledge_repo)

    # 覆盖依赖
    app.dependency_overrides[get_novel_service] = get_test_novel_service
    app.dependency_overrides[get_knowledge_service] = get_test_knowledge_service

    yield

    # 清理
    app.dependency_overrides.clear()
    _test_novel_service = None
    _test_knowledge_service = None
    if test_data.exists():
        shutil.rmtree(test_data)


client = TestClient(app)


@pytest.fixture
def test_novel():
    """创建测试小说"""
    response = client.post("/api/v1/novels/", json={
        "novel_id": "test-novel-knowledge",
        "title": "测试小说",
        "author": "测试作者",
        "target_chapters": 10
    })
    assert response.status_code == 201
    return response.json()


class TestGetKnowledge:
    """测试获取知识图谱端点"""

    def test_get_knowledge_empty(self, test_novel):
        """测试获取空知识图谱"""
        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        assert data["premise_lock"] == ""
        assert isinstance(data["chapters"], list)
        assert isinstance(data["facts"], list)
        assert len(data["chapters"]) == 0
        assert len(data["facts"]) == 0

    def test_get_knowledge_with_data(self, test_novel):
        """测试获取有数据的知识图谱"""
        # 先创建知识数据
        client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "测试梗概锁定",
            "chapters": [
                {
                    "chapter_id": 1,
                    "summary": "第一章摘要",
                    "key_events": "关键事件",
                    "open_threads": "未解问题",
                    "consistency_note": "一致性说明",
                    "beat_sections": ["节拍1", "节拍2"],
                    "sync_status": "synced"
                }
            ],
            "facts": [
                {
                    "id": "fact-1",
                    "subject": "主角",
                    "predicate": "是",
                    "object": "程序员",
                    "chapter_id": 1,
                    "note": "测试备注"
                }
            ]
        })

        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert data["premise_lock"] == "测试梗概锁定"
        assert len(data["chapters"]) == 1
        assert len(data["facts"]) == 1
        assert data["chapters"][0]["chapter_id"] == 1
        assert data["chapters"][0]["summary"] == "第一章摘要"
        assert data["facts"][0]["subject"] == "主角"


class TestUpdateKnowledge:
    """测试更新知识图谱端点"""

    def test_update_knowledge_success(self, test_novel):
        """测试成功更新知识图谱"""
        response = client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "程序员穿越到古代",
            "chapters": [
                {
                    "chapter_id": 1,
                    "summary": "主角穿越",
                    "key_events": "李云舟穿越到古代",
                    "open_threads": "如何生存",
                    "consistency_note": "时间线第1天",
                    "beat_sections": ["穿越场景", "初到古代"],
                    "sync_status": "draft"
                }
            ],
            "facts": [
                {
                    "id": "f_001",
                    "subject": "李云舟",
                    "predicate": "职业",
                    "object": "程序员",
                    "chapter_id": 1,
                    "note": "主角设定"
                }
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["premise_lock"] == "程序员穿越到古代"
        assert len(data["chapters"]) == 1
        assert len(data["facts"]) == 1
        assert data["chapters"][0]["chapter_id"] == 1
        assert data["facts"][0]["id"] == "f_001"

    def test_update_knowledge_multiple_chapters(self, test_novel):
        """测试更新多个章节摘要"""
        response = client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "测试梗概",
            "chapters": [
                {
                    "chapter_id": 1,
                    "summary": "第一章",
                    "key_events": "事件1",
                    "open_threads": "",
                    "consistency_note": "",
                    "beat_sections": [],
                    "sync_status": "synced"
                },
                {
                    "chapter_id": 2,
                    "summary": "第二章",
                    "key_events": "事件2",
                    "open_threads": "",
                    "consistency_note": "",
                    "beat_sections": [],
                    "sync_status": "draft"
                }
            ],
            "facts": []
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["chapters"]) == 2
        assert data["chapters"][0]["chapter_id"] == 1
        assert data["chapters"][1]["chapter_id"] == 2

    def test_update_knowledge_multiple_facts(self, test_novel):
        """测试更新多个知识三元组"""
        response = client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "",
            "chapters": [],
            "facts": [
                {
                    "id": "f_001",
                    "subject": "张三",
                    "predicate": "是",
                    "object": "主角",
                    "chapter_id": 1,
                    "note": ""
                },
                {
                    "id": "f_002",
                    "subject": "李四",
                    "predicate": "是",
                    "object": "配角",
                    "chapter_id": 2,
                    "note": ""
                },
                {
                    "id": "f_003",
                    "subject": "张三",
                    "predicate": "认识",
                    "object": "李四",
                    "chapter_id": None,
                    "note": "关系"
                }
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["facts"]) == 3
        assert data["facts"][0]["subject"] == "张三"
        assert data["facts"][2]["chapter_id"] is None

    def test_update_knowledge_overwrite(self, test_novel):
        """测试覆盖更新知识图谱"""
        # 第一次更新
        client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "初始梗概",
            "chapters": [{"chapter_id": 1, "summary": "初始摘要", "key_events": "", "open_threads": "", "consistency_note": "", "beat_sections": [], "sync_status": "draft"}],
            "facts": [{"id": "f_001", "subject": "A", "predicate": "B", "object": "C", "chapter_id": None, "note": ""}]
        })

        # 第二次更新（覆盖）
        response = client.put("/api/v1/novels/test-novel-knowledge/knowledge", json={
            "version": 1,
            "premise_lock": "更新后梗概",
            "chapters": [{"chapter_id": 2, "summary": "新摘要", "key_events": "", "open_threads": "", "consistency_note": "", "beat_sections": [], "sync_status": "synced"}],
            "facts": [{"id": "f_002", "subject": "X", "predicate": "Y", "object": "Z", "chapter_id": None, "note": ""}]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["premise_lock"] == "更新后梗概"
        assert len(data["chapters"]) == 1
        assert data["chapters"][0]["chapter_id"] == 2
        assert len(data["facts"]) == 1
        assert data["facts"][0]["id"] == "f_002"


class TestSearchKnowledge:
    """测试搜索知识图谱端点"""

    def test_search_knowledge_empty(self, test_novel):
        """测试搜索空知识图谱"""
        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge/search?q=测试&k=5")
        assert response.status_code == 200
        data = response.json()
        assert "hits" in data
        assert isinstance(data["hits"], list)
        # 当前实现返回空结果
        assert len(data["hits"]) == 0

    def test_search_knowledge_with_params(self, test_novel):
        """测试带参数的搜索"""
        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge/search?q=主角&k=10")
        assert response.status_code == 200
        data = response.json()
        assert "hits" in data

    def test_search_knowledge_missing_query(self, test_novel):
        """测试缺少查询参数"""
        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge/search")
        assert response.status_code == 422  # Validation error

    def test_search_knowledge_invalid_k(self, test_novel):
        """测试无效的 k 参数"""
        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge/search?q=测试&k=0")
        assert response.status_code == 422  # Validation error

        response = client.get("/api/v1/novels/test-novel-knowledge/knowledge/search?q=测试&k=100")
        assert response.status_code == 422  # Validation error
