
from math import ceil
from typing import Any, Optional, Dict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


def sanitize_pagination(page: int = 1, per_page: int = DEFAULT_PER_PAGE):
    page = max(1, int(page or 1))
    per_page = min(MAX_PER_PAGE, max(1, int(per_page or DEFAULT_PER_PAGE)))

    return page, per_page


def paginate_query(
    db: Session,
    model,
    base_query=None,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    order_by: Optional[str] = None,
    direction: str = "asc",
    allowed_order: Optional[Dict[str, Any]] = None
):
    page, per_page = sanitize_pagination(page, per_page)
    query = base_query if base_query is not None else select(model)

    total = db.scalar(select(func.count()).select_from(model)) or 0

    if total == 0:
        return {"total": 0, "pages": 0, "page": page, "per_page": per_page, "items": []}

    if allowed_order and order_by:
        col = allowed_order.get(order_by, allowed_order.get("id"))
        query = query.order_by(col.desc() if direction ==
                               "desc" else col.asc())

    items = db.execute(query.offset(
        (page-1) * per_page).limit(per_page)).scalars().all()

    return {
        "total": total,
        "pages": ceil(total/per_page),
        "page": page,
        "per_page": per_page,
        "items": items
    }
