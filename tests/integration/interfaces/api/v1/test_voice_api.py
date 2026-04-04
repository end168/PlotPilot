"""Integration tests for Voice API"""
import pytest
from fastapi.testclient import TestClient
from interfaces.main import app


class TestVoiceAPI:
    """Voice API 集成测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def test_novel_id(self, client):
        """创建测试小说并返回 ID"""
        import uuid
        novel_id = f"test-novel-voice-{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/api/v1/novels",
            json={
                "novel_id": novel_id,
                "title": "测试小说",
                "author": "测试作者",
                "target_chapters": 10,
                "premise": "测试前提"
            }
        )
        assert response.status_code == 201
        return response.json()["id"]

    def test_create_voice_sample(self, client, test_novel_id):
        """测试创建文风样本"""
        # Arrange
        request_data = {
            "ai_original": "这是AI生成的原始文本，包含一些描述。",
            "author_refined": "这是作者精心修改后的文本，更加生动。",
            "chapter_number": 1,
            "scene_type": "dialogue"
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "sample_id" in data
        assert isinstance(data["sample_id"], str)
        assert len(data["sample_id"]) > 0

    def test_create_voice_sample_with_default_scene_type(self, client, test_novel_id):
        """测试使用默认场景类型创建文风样本"""
        # Arrange
        request_data = {
            "ai_original": "AI原文",
            "author_refined": "作者改稿",
            "chapter_number": 2
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "sample_id" in data

    def test_create_voice_sample_validation_empty_ai_original(self, client, test_novel_id):
        """测试空 AI 原文验证"""
        # Arrange
        request_data = {
            "ai_original": "",
            "author_refined": "作者改稿",
            "chapter_number": 1,
            "scene_type": "action"
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_voice_sample_validation_empty_author_refined(self, client, test_novel_id):
        """测试空作者改稿验证"""
        # Arrange
        request_data = {
            "ai_original": "AI原文",
            "author_refined": "",
            "chapter_number": 1,
            "scene_type": "action"
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_voice_sample_validation_invalid_chapter_number(self, client, test_novel_id):
        """测试无效章节号验证"""
        # Arrange
        request_data = {
            "ai_original": "AI原文",
            "author_refined": "作者改稿",
            "chapter_number": 0,  # Invalid: must be >= 1
            "scene_type": "action"
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_voice_sample_missing_required_fields(self, client, test_novel_id):
        """测试缺少必填字段"""
        # Arrange
        request_data = {
            "ai_original": "AI原文"
            # Missing author_refined and chapter_number
        }

        # Act
        response = client.post(
            f"/api/v1/novels/{test_novel_id}/voice/samples",
            json=request_data
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_multiple_voice_samples(self, client, test_novel_id):
        """测试创建多个文风样本"""
        # Arrange
        samples = [
            {
                "ai_original": "第一个样本的AI原文",
                "author_refined": "第一个样本的作者改稿",
                "chapter_number": 1,
                "scene_type": "dialogue"
            },
            {
                "ai_original": "第二个样本的AI原文",
                "author_refined": "第二个样本的作者改稿",
                "chapter_number": 2,
                "scene_type": "action"
            },
            {
                "ai_original": "第三个样本的AI原文",
                "author_refined": "第三个样本的作者改稿",
                "chapter_number": 3,
                "scene_type": "description"
            }
        ]

        # Act & Assert
        sample_ids = []
        for sample in samples:
            response = client.post(
                f"/api/v1/novels/{test_novel_id}/voice/samples",
                json=sample
            )
            assert response.status_code == 201
            data = response.json()
            assert "sample_id" in data
            sample_ids.append(data["sample_id"])

        # Verify all sample IDs are unique
        assert len(sample_ids) == len(set(sample_ids))
