
from operator import ge
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.tags import repository
from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=dict)
def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):
    repository = TagRepository(db)
    return repository.list_tags(page=page, per_page=per_page, order_by=order_by, direction=direction, search=search)


@router.post("", response_model=TagPublic, response_description="Post creado (OK)", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repository = TagRepository(db)
    try:
        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el tag")


@router.put("/{tag_id}", response_model=TagPublic)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    repository = TagRepository(db)
    tag = repository.update(tag_id, name=payload.name)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    db.commit()
    return TagPublic.model_validate(tag)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_tag(tag_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repository = TagRepository(db)
    delete = repository.delete(tag_id)

    if not delete:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    db.commit()
    return None


@router.get("/popular/top")
def get_most_popular_tag(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    repository = TagRepository(db)
    row = repository.most_popular()

    if not row:
        raise HTTPException(status_code=404, detail="No hay tags en uso")

    return row
