from flask import request

from app.errors.exceptions import ValidationAppError

MAX_PER_PAGE = 100


def parse_list_params(allowed_filters=None):
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), MAX_PER_PAGE)
    sort = request.args.get("sort", "").strip()
    search = request.args.get("search", "").strip()

    filters = {}
    for key in allowed_filters or []:
        value = request.args.get(f"filter[{key}]")
        if value is not None:
            filters[key] = value

    return {
        "page": max(page, 1),
        "per_page": max(per_page, 1),
        "sort": sort,
        "search": search,
        "filters": filters,
    }


def apply_sort(query, model, sort_param, allowed_fields):
    if not sort_param:
        return query
    descending = sort_param.startswith("-")
    field_name = sort_param[1:] if descending else sort_param
    if field_name not in allowed_fields:
        raise ValidationAppError(f"Cannot sort by '{field_name}'")
    column = getattr(model, field_name)
    return query.order_by(column.desc() if descending else column.asc())


def paginated_response(query, page, per_page, schema):
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": schema.dump(result.items, many=True),
        "meta": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
        },
    }
