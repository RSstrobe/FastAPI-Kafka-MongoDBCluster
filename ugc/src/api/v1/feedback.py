from http import HTTPStatus

from beanie import Document
from pydantic import ValidationError
from flask import Blueprint, request, jsonify, Response
from fast_depends import inject, Depends

from core import exceptions
from helpers.access import check_access_token
from models.mongo import collections
from services.feedback.review import ReviewService, get_review_service

router = Blueprint("feedback", __name__, url_prefix="/ugc")


@router.route("/review", methods=["POST"])
@inject
@check_access_token
async def post_review(
    user_info: dict = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """API for post user review on film-work."""
    request_data: dict = request.args.to_dict()
    request_data["user_id"] = user_info.get("sub")
    try:
        review: Document = collections.Review(**request_data)
    except ValidationError:
        raise exceptions.ValidationException
    await review_service.create(
        document=review.dict(),
    )
    return jsonify({"message": "Successful writing"}), HTTPStatus.OK


@router.route("/review", methods=["GET"])
@inject
@check_access_token
async def get_reviews(
    user_info: dict = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """API for getting all reviews on film-work."""
    request_data: dict = request.args.to_dict()

    response = await review_service.get_with_pagination(
        document={"movie_id": str(request_data["movie_id"]), "is_delete": False},
        pagination_settings=request_data,
    )
    return Response(response.model_dump_json(), mimetype="application/json")


@router.route("/review_admin", methods=["DELETE"])
@inject
@check_access_token
async def admin_delete_review(
    user_info: dict = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """Delete review by admin on film-work."""
    request_data: dict = request.args.to_dict()
    await review_service.delete(
        document={
            "user_id": str(request_data.get("user_id")),
            "movie_id": str(request_data.get("movie_id")),
        }
    )
    return jsonify({"message": "Successful deleting"}), HTTPStatus.OK


@router.route("/review", methods=["DELETE"])
@inject
@check_access_token
async def delete_review(
    user_info: dict = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """Update self review on film-work."""
    request_data: dict = request.args.to_dict()
    await review_service.update(
        filter_data={
            "user_id": str(user_info.get("sub")),
            "movie_id": str(request_data.get("movie_id")),
        },
        update_data={
            "is_delete": True,
        },
    )
    return jsonify({"message": "Successful writing"}), HTTPStatus.OK


@router.route("/review", methods=["PUT"])
@inject
@check_access_token
async def update_review(
    user_info: dict = None,
    review_service: ReviewService = Depends(get_review_service),
):
    """Update self review on film-work."""
    request_data: dict = request.args.to_dict()
    new_data = dict()
    if "text" in request_data:
        new_data["text"] = str(request_data["text"])
    if "score" in request_data:
        new_data["score"] = int(request_data["score"])
    await review_service.update(
        filter_data={
            "user_id": str(user_info.get("sub")),
            "movie_id": str(request_data.get("movie_id")),
            "is_delete": False,
        },
        update_data=new_data,
    )

    return jsonify({"message": "Successful writing"}), HTTPStatus.OK
