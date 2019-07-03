"""Defines the HTTP routes and methods supported by the relations API."""

from flask import Blueprint, Response, request
from flask.json import jsonify

from .. import controllers


blueprint = Blueprint('api', __name__, url_prefix='')


@blueprint.route('/status', methods=['GET'])
def service_status() -> Response:
    """
    Service status endpoint.

    Returns ``200 OK`` if the service is up and ready to handle requests.
    """
    response_data, status_code, headers = controllers.service_status(request.params)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response

@blueprint.route('/{str:arxiv_id_str}v{int:arxiv_ver}/relations',methods=['POST'])
def create_new(arxiv_id_str: str,arxiv_ver: int) -> Response:
    response_data,status_code,headers = controllers.create_new(arxiv_id_str,arxiv_ver,request.params)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response

@blueprint.route('/{str:arxiv_id_str}v{int:arxiv_ver}/relations/{str:relation_id_str}',methods=['PUT'])
def supercede(arxiv_id_str: str,arxiv_ver: int,relation_id_str: str) -> Response:
    response_data,code,headers = controllers.supercede(arxiv_id_str,arxiv_ver,relation_id_str,request.params)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response

@blueprint.route('/{str:arxiv_id_str}v{int:arxiv_ver}/relations/{str:relation_id_str}',methods=['DELETE'])
def suppress(arxiv_id_str: str,arxiv_ver: int,relation_id_str: str) -> Response:
    response_data,code,headers = controllers.suppress(arxiv_id_str,arxiv_ver,relation_id_str,request.params)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response

@blueprint.route('/{str:arxiv_id_str}v{int:arxiv_ver}',methods=['GET'])
def get_relations(arxiv_id_str: str,arxiv_ver: int) -> Response:
    data,code,headers = controllers.get_relations(arxiv_id_str,arxiv_ver)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response

@blueprint.route('/{str:arxiv_id_str}v{int:arxiv_ver}/log',methods=['GET'])
def get_events(arxiv_id_str: str,arxiv_ver: int) -> Response:
    response_data,code,headers = controllers.get_events(arxiv_id_str,arxiv_ver)
    response: Response = jsonify(response_data)
    response.status_code = status_code
    response.headers.extend(headers)
    return response