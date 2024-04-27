from http import HTTPStatus

from beanie import Document
from flask import Blueprint, request, jsonify, Response
from fast_depends import inject, Depends

from helpers.access import check_access_token
from models.mongo import collections
from services.feedback.bookmarks import get_bookmark_service, BookmarkService

router = Blueprint("bookmark", __name__, url_prefix="/ugc")


@router.route("/bookmark", methods=["POST"])
@inject
@check_access_token
async def post_bookmark(
    user_info: dict = None,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    request_data: dict = request.args.to_dict()
    request_data["user_id"] = user_info.get("sub")
    bookmark: Document = collections.Bookmark(**request_data)
    await bookmark_service.save_object(
        document=bookmark.dict(),
    )
    return jsonify({"message": "Successful writing"}), HTTPStatus.OK


@router.route("/bookmark", methods=["DELETE"])
@inject
@check_access_token
async def delete_bookmark(
    user_info: dict = None,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    request_data: dict = request.args.to_dict()
    request_data["user_id"] = user_info.get("sub")
    bookmark: Document = collections.Bookmark(**request_data)
    await bookmark_service.delete_object(
        document=bookmark.dict(),
    )
    return jsonify({"message": "Successful deleting"}), HTTPStatus.OK


@router.route("/bookmark", methods=["GET"])
@inject
@check_access_token
async def get_bookmark(
    user_info: dict = None,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
):
    request_data: dict = request.args.to_dict()
    response = await bookmark_service.get_with_pagination(
        document={"user_id": str(user_info.get("sub")), "is_delete": False},
        pagination_settings=request_data,
    )

    return Response(response.model_dump_json(), mimetype="application/json")
