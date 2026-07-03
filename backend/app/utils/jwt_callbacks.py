from flask import jsonify

from app.extensions import jwt
from app.utils.redis_client import redis_client


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return redis_client.client.exists(f"revoked:{jti}") == 1


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": {"code": "TOKEN_EXPIRED", "message": "Token has expired"}}), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"error": {"code": "TOKEN_INVALID", "message": "Invalid token"}}), 401


@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({"error": {"code": "TOKEN_MISSING", "message": "Authorization token is required"}}), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": {"code": "TOKEN_REVOKED", "message": "Token has been revoked"}}), 401
