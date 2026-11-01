from flask import Blueprint, render_template, request

from .queries import get_sales_page

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    try:
        requested_page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        requested_page = 1

    sales, page, total_pages = get_sales_page(requested_page)

    return render_template(
        "index.html",
        sales=sales,
        page=page,
        total_pages=total_pages,
    )


@bp.route("/health")
def health():
    return {"status": "ok"}