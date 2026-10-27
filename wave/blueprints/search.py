from wave.db import db
from wave.models import Topic, streamed_fuzzy_search

from flask import Blueprint, render_template, request

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/topic", methods=["GET"])
def search_topics():
    search_query = request.args.get("q", "")
    combobox_id = request.args.get("cbid", "")

    results = streamed_fuzzy_search(Topic, "name", db.session, search_query, 5)

    return render_template(
        "/components/combobox_results.html", results=results, id=combobox_id
    )
