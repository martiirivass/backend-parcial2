from math import ceil


def paginated_response(data, total: int, page: int = 1, size: int = 10):
    pages = max(1, ceil(total / size))
    return {
        "data": data,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }
