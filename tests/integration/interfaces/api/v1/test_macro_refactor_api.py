"""Macro Refactor API 集成测试"""
import pytest
from fastapi.testclient import TestClient
from interfaces.main import app


class TestMacroRefactorAPI:
    """Macro Refactor API 集成测试套件"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def setup_test_data(self):
        """设置测试数据"""
        from infrastructure.persistence.database.connection import get_database
        from infrastructure.persistence.database.sqlite_narrative_event_repository import SqliteNarrativeEventRepository

        db = get_database()
        repo = SqliteNarrativeEventRepository(db)

        # 创建测试小说和事件
        novel_id = "test-novel-macro-refactor"

        # 清理旧数据
        db.execute("DELETE FROM narrative_events WHERE novel_id = ?", (novel_id,))
        db.execute("DELETE FROM novels WHERE id = ?", (novel_id,))
        db.get_connection().commit()

        # 创建测试小说
        db.execute(
            "INSERT INTO novels (id, title, slug, target_chapters) VALUES (?, ?, ?, ?)",
            (novel_id, "Test Novel", "test-novel-macro-refactor", 10)
        )
        db.get_connection().commit()

        # 添加测试事件
        repo.append_event(
            novel_id=novel_id,
            chapter_number=1,
            event_summary="主角冲动行事",
            mutations=[],
            tags=["动机:冲动", "情绪:激动"]
        )
        repo.append_event(
            novel_id=novel_id,
            chapter_number=2,
            event_summary="主角愤怒爆发",
            mutations=[],
            tags=["情绪:愤怒", "行为:鲁莽"]
        )
        repo.append_event(
            novel_id=novel_id,
            chapter_number=3,
            event_summary="主角冷静分析",
            mutations=[],
            tags=["动机:理性", "情绪:冷静"]
        )

        yield novel_id

        # 清理测试数据
        db.execute("DELETE FROM narrative_events WHERE novel_id = ?", (novel_id,))
        db.execute("DELETE FROM novels WHERE id = ?", (novel_id,))
        db.get_connection().commit()

    def test_scan_breakpoints_finds_conflicts(self, client, setup_test_data):
        """测试：扫描找到冲突断点"""
        novel_id = setup_test_data

        # 发送请求
        response = client.get(
            f"/api/v1/novels/{novel_id}/macro-refactor/breakpoints",
            params={"trait": "冷酷"}
        )

        # 验证响应
        assert response.status_code == 200
        breakpoints = response.json()

        # 应该找到 2 个冲突（章节 1 和 2）
        assert len(breakpoints) == 2
        assert breakpoints[0]["chapter"] == 1
        assert breakpoints[1]["chapter"] == 2
        assert "冷酷" in breakpoints[0]["reason"]
        assert len(breakpoints[0]["tags"]) > 0

    def test_scan_breakpoints_validation(self, client):
        """测试：验证 trait 参数必需"""
        # 不提供 trait 参数
        response = client.get("/api/v1/novels/test-novel/macro-refactor/breakpoints")

        # 应该返回 422 验证错误
        assert response.status_code == 422

    def test_scan_breakpoints_with_custom_tags(self, client, setup_test_data):
        """测试：使用自定义冲突标签"""
        novel_id = setup_test_data

        # 使用自定义冲突标签
        response = client.get(
            f"/api/v1/novels/{novel_id}/macro-refactor/breakpoints",
            params={
                "trait": "理性",
                "conflict_tags": "动机:冲动,情绪:激动"
            }
        )

        # 验证响应
        assert response.status_code == 200
        breakpoints = response.json()

        # 应该只找到章节 1（包含 "动机:冲动" 或 "情绪:激动"）
        assert len(breakpoints) == 1
        assert breakpoints[0]["chapter"] == 1

    def test_scan_breakpoints_no_conflicts(self, client, setup_test_data):
        """测试：无冲突时返回空列表"""
        novel_id = setup_test_data

        # 使用不会冲突的自定义标签
        response = client.get(
            f"/api/v1/novels/{novel_id}/macro-refactor/breakpoints",
            params={
                "trait": "测试",
                "conflict_tags": "不存在的标签"
            }
        )

        # 验证响应
        assert response.status_code == 200
        breakpoints = response.json()
        assert len(breakpoints) == 0
