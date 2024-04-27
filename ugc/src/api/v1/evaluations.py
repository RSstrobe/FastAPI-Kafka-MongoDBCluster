from http import HTTPStatus

from fast_depends import inject, Depends
from flask import Blueprint, request, jsonify, Response
from beanie import Document
from pydantic import ValidationError

from core import exceptions
from helpers.access import check_access_token
from models.mongo import collections
from services.feedback.evaluations import EvaluationService, get_evaluation_service

router = Blueprint("evaluations", __name__, url_prefix="/ugc")


@router.route("/evaluation", methods=["POST"])
@inject
@check_access_token
async def post_evaluation(
    user_info: dict = None,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
):
    request_data = request.args.to_dict()
    user_id = user_info.get("sub")

    if await evaluation_service.read(
        {
            "review_id": request_data.get("review_id"),
            "user_id": user_id,
            "is_delete": False,
        }
    ):
        raise exceptions.EvaluationCreatedException
    request_data["user_info"] = user_id

    try:
        evaluation: Document = collections.Evaluation(**request_data)
    except ValidationError:
        raise exceptions.ValidationException

    await evaluation_service.save_object(document=evaluation.dict())
    return jsonify({"message": "Successful writing"}), HTTPStatus.OK


@router.route("/evaluation", methods=["DELETE"])
@inject
@check_access_token
async def delete_evaluation(
    user_info: dict = None,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
):
    request_data: dict = request.args.to_dict()
    request_data["user_info"] = user_info.get("sub")
    evaluation: Document = collections.Evaluation(**request_data)
    await evaluation_service.delete_object(
        document=evaluation.dict(),
    )
    return jsonify({"message": "Successful deleting"}), HTTPStatus.OK


@router.route("/evaluation", methods=["GET"])
@inject
@check_access_token
async def get_evaluations(
    user_info: dict = None,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
):
    request_data = request.args.to_dict()
    request_data["user_info"] = user_info.get("sub")
    response = await evaluation_service.get_with_pagination(
        document={"review_id": request_data.get("review_id"), "is_delete": False},
        pagination_settings=request_data,
    )
    return Response(response.model_dump_json(), mimetype="application/json")
