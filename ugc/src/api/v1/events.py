from http import HTTPStatus

from core.constants import TopicNames
from flask import Blueprint, jsonify, request
from helpers.access import check_access_token
from models.click import ClickEvent
from models.player import EventsNames, PlayerProgress, PlayerSettingEvents
from services.click_event import ClickService, get_click_service
from services.player_events import PlayerService, get_player_service

routers = Blueprint("ugc", __name__, url_prefix="/ugc")


@routers.route("/click_event", methods=["POST"])
@check_access_token
async def post_click_event(user_info: dict = None):
    """API for post click events, parsing and moving to Kafka ETL"""
    click_service: ClickService = get_click_service()
    request_data = request.args.to_dict()
    data_model = ClickEvent(**request_data)
    await click_service.send_message(topic_name=TopicNames.click_events, message_model=data_model)
    return jsonify({'message': f'Message sent'}), HTTPStatus.OK


@routers.route("/player_event", methods=["POST"])
@check_access_token
async def post_player_event(user_info: dict = None):
    """API for post player events, parsing and moving to Kafka ETL"""
    player_service: PlayerService = get_player_service()
    request_data = request.args.to_dict()
    request_data["event_type"] = EventsNames[request_data.get("event_type", "")]
    data_model = PlayerSettingEvents(**request_data)
    await player_service.send_message(topic_name=TopicNames.player_settings_events, message_model=data_model)
    return jsonify({'message': f'Message sent'}), HTTPStatus.OK


@routers.route("/player_progress", methods=["POST"])
@check_access_token
async def post_player_progress(user_info: dict = None):
    """API for post player events, parsing and moving to Kafka ETL"""
    player_service: PlayerService = get_player_service()
    request_data = request.args.to_dict()
    data_model = PlayerProgress(**request_data)
    await player_service.send_message(topic_name=TopicNames.player_progress, message_model=data_model)
    return jsonify({'message': f'Message sent'}), HTTPStatus.OK