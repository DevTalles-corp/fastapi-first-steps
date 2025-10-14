
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.tags.schemas import TagPublic
from app.models.post import PostORM, post_tags
from app.models.tag import TagORM
from app.services.pagination import paginate_query


class TagRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, tag_id: int) -> Optional[TagORM]:
        tag_find = select(TagORM).where(TagORM.id == tag_id)
        return self.db.execute(tag_find).scalar_one_or_none()

    def list_tags(
        self,
        search: Optional[str],
        order_by: str = "id",
        direction: str = "asc",
        page: int = 1,
        per_page: int = 10
    ):
        query = select(TagORM)
        if search:
            query = query.where(func.lower(
                TagORM.name).ilike(f"%{search.lower()}%"))

        allowed_order = {
            "id": TagORM.id,
            "name": func.lower(TagORM.name),
        }

        result = paginate_query(
            db=self.db,
            model=TagORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order
        )

        result["items"] = [TagPublic.model_validate(
            item) for item in result["items"]]

        return result

    def create_tag(self, name: str):
        normalize = name.strip().lower()

        tag_obj = self.db.execute(
            select(TagORM).where(func.lower(TagORM.name) == normalize)
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()
        return tag_obj

    def update(self, tag_id: int, name: str) -> Optional[TagORM]:
        tag = self.get(tag_id)
        if not tag:
            return None
        if name is not None:
            tag.name = name.strip().lower()

        self.db.add(tag)
        self.db.flush()
        self.db.refresh(tag)
        return tag

    def delete(self, tag_id: int) -> bool:
        tag = self.get(tag_id)
        if not tag:
            return False
        self.db.delete(tag)
        return True

    def most_popular(self) -> dict | None:

        row = (
            self.db.execute(
                select(
                    TagORM.id.label("id"),
                    TagORM.name.label("name"),
                    func.count(PostORM.id).label("uses")
                )
                .join(post_tags, post_tags.c.tag_id == TagORM.id)
                .join(PostORM, PostORM.id == post_tags.c.post_id)
                .group_by(TagORM.id, TagORM.name)
                .order_by(func.count(PostORM.id).desc(), func.lower(TagORM.name).asc())
                .limit(1)
            )
            .mappings()
            .first()
        )

        return dict(row) if row else None
