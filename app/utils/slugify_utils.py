
from slugify import slugify as _slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import PostORM


def slugify_base(text: str) -> str:
    slug = _slugify(text, lowercase=True, separator='-')
    return slug or "post"


def ensure_unique_slug(db: Session, base_text: str) -> str:
    base = slugify_base(base_text)
    existing = db.execute(
        select(PostORM.slug).where(PostORM.slug.like(f"{base}%"))
    ).scalars().all()

    if base not in existing:
        return base

    i = 2
    candidate = f"{base}-{i}"
    while candidate in existing:
        i += 1
        candidate = f"{base}-{i}"
    return candidate
