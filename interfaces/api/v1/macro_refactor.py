"""Macro Refactor API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from application.services.macro_refactor_scanner import MacroRefactorScanner
from application.dtos.macro_refactor_dto import LogicBreakpoint
from interfaces.api.dependencies import get_macro_refactor_scanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/novels", tags=["macro-refactor"])


@router.get("/{novel_id}/macro-refactor/breakpoints", response_model=List[LogicBreakpoint])
async def scan_breakpoints(
    novel_id: str,
    trait: str = Query(..., description="Target character trait (e.g., '冷酷')"),
    conflict_tags: Optional[str] = Query(None, description="Custom conflict tags (comma-separated)"),
    scanner: MacroRefactorScanner = Depends(get_macro_refactor_scanner)
) -> List[LogicBreakpoint]:
    """
    Scan for logic breakpoints where events conflict with character traits.

    This endpoint analyzes all narrative events in a novel to identify points
    where event tags conflict with a specified character trait.

    Args:
        novel_id: The novel ID
        trait: Target character trait to check for conflicts (e.g., "冷酷", "理性")
        conflict_tags: Optional comma-separated list of custom conflict tags
        scanner: Injected macro refactor scanner service

    Returns:
        List of logic breakpoints with conflict details

    Raises:
        HTTPException: 500 if internal error occurs
    """
    try:
        # Parse conflict_tags if provided
        parsed_conflict_tags = None
        if conflict_tags:
            parsed_conflict_tags = [tag.strip() for tag in conflict_tags.split(",") if tag.strip()]

        # Scan for breakpoints
        breakpoints = scanner.scan_breakpoints(
            novel_id=novel_id,
            trait=trait,
            conflict_tags=parsed_conflict_tags
        )

        logger.info(f"Scanned novel {novel_id} for trait '{trait}', found {len(breakpoints)} breakpoints")
        return breakpoints

    except Exception as e:
        logger.error(f"Error scanning breakpoints: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
