import os
import boto3
from flask import Blueprint, session, request, jsonify, send_file
import base64
import datetime
import uuid
from io import BytesIO
from flask_cors import CORS
import logging

routes_bp = Blueprint("routes", __name__)
CORS(routes_bp)

dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:4566")
region_name = os.getenv("REGION_NAME", "ap-south-1")

dynamodb = boto3.resource(
    "dynamodb", region_name=region_name, endpoint_url=dynamodb_endpoint
)
emails_table = dynamodb.Table("emails")
users_table = dynamodb.Table("users")


def create_hash(*args):
    _args = [str(arg) for arg in args]
    return base64.b64encode("".join(_args).encode()).decode()


@routes_bp.route("/create-tracker", methods=["POST"])
def create_tracker():
    data = request.json
    logging.info(data)
    from_email = data.get("from_email")
    receiver_email = data.get("receiver_email")
    subject = data.get("subject")

    if not from_email or not receiver_email or not subject:
        return jsonify({"status": "error", "message": "Missing required fields"}, 400)

    response = users_table.scan(
        FilterExpression="email = :email",
        ExpressionAttributeValues={":email": from_email},
    )
    items = response.get("Item", [])
    user_id = None

    if items:
        user_id = items[0].get("user_id")

    if not user_id:
        user_id = create_hash(from_email)
        users_table.put_item(Item={"user_id": user_id, "email": from_email})

    milliseconds = datetime.datetime.now().timestamp() * 1000
    message_id = create_hash(user_id, receiver_email, subject, milliseconds)

    emails_table.put_item(
        Item={
            "message_id": message_id,
            "user_id": user_id,
            "receiver_email": receiver_email,
            "subject": subject,
            "open_count": 0,
            "open_timestamps": [],
        }
    )

    return jsonify({"status": "success", "message_id": message_id})


def generate_base64_image():
    pixel = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x8d\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
    
    return pixel


@routes_bp.route("/track/<message_id>.png", methods=["GET"])
def track(message_id):
    response = emails_table.get_item(Key={"message_id": message_id})
    item = response.get("Item")

    if not item:
        return jsonify({"status": "error", "message": "Invalid message_id"}, 400)

    open_count = item["open_count"] or 0
    open_count += 1
    open_timestamps = item["open_timestamps"] or []
    open_timestamps.append(datetime.datetime.now().isoformat())

    emails_table.update_item(
        Key={"message_id": message_id},
        UpdateExpression="SET open_count = :open_count, open_timestamps = :open_timestamps",
        ExpressionAttributeValues={
            ":open_count": open_count,
            ":open_timestamps": open_timestamps,
        },
    )

    base64_pixel = generate_base64_image()

    return send_file(BytesIO(base64_pixel), mimetype="image/png")


@routes_bp.route("/get-tracker", methods=["GET"])
@routes_bp.route("/get-tracker/<message_id>", methods=["GET"])
def get_tracker(message_id=None):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "Missing required fields"}, 400)

    if not message_id:
        response = emails_table.scan(
            FilterExpression="user_id = :user_id",
            ExpressionAttributeValues={":user_id": user_id},
        )
        items = response.get("Items")
    else:
        response = emails_table.get_item(
            Key={"message_id": message_id, "user_id": user_id}
        )
        item = response.get("Item")
        items = [item] if item else []

    return jsonify({"status": "success", "data": items})
