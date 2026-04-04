"""Macro Refactor DTOs"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LogicBreakpoint:
    """逻辑断点 - 人设冲突点"""
    event_id: str
    chapter: int
    reason: str  # 冲突原因描述
    tags: List[str]  # 匹配的冲突标签


@dataclass
class BreakpointScanRequest:
    """断点扫描请求"""
    trait: str  # 目标人设标签，如 "冷酷"
    conflict_tags: Optional[List[str]] = None  # 冲突标签列表，如 ["动机:冲动"]
