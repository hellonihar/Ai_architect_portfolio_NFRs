from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Action
from app.schemas import ActionResponse, ActionCreate

router = APIRouter(prefix="/api/actions", tags=["Actions"])


@router.get("", response_model=list[ActionResponse])
async def get_actions(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Action).order_by(Action.created_at.desc())
    if status:
        query = query.where(Action.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ActionResponse, status_code=201)
async def create_action(payload: ActionCreate, db: AsyncSession = Depends(get_db)):
    action = Action(**payload.model_dump())
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


@router.patch("/{action_id}/complete", response_model=ActionResponse)
async def complete_action(action_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Action).where(Action.id == action_id))
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action.status = "Completed"
    action.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(action)
    return action
