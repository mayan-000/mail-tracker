from flask import Blueprint, request, jsonify, session
import boto3
import uuid
import random
import string
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint("auth", __name__)

dynamodb = boto3.resource(
    "dynamodb", region_name="ap-south-1", endpoint_url="http://localhost:4566"
)
users_table = dynamodb.Table("users")


def generate_otp():
    return "".join(random.choices(string.digits, k=6))


def send_otp(email, otp):
    # TODO: Implement email sending
    logging.info(f"OTP: {otp}")


@auth_bp.route("/login/request-otp", methods=["POST"])
def login_request_otp():
    data = request.json
    email = data.get("email")

    otp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=10)

    response = users_table.scan(
        FilterExpression="email = :email", ExpressionAttributeValues={":email": email}
    )
    items = response.get("Items")

    if items:
        user = items[0]
        user_id = user["user_id"]
        user_otp_expiry = datetime.fromisoformat(user["otp_expiry"])

        if user_otp_expiry - otp_expiry > timedelta(minutes=2):
            return jsonify(
                {
                    "status": "update",
                    "message": "Previous OTP is still valid for 2 minutes",
                }
            )

        users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET otp = :otp, otp_expiry = :otp_expiry",
            ExpressionAttributeValues={
                ":otp": otp,
                ":otp_expiry": otp_expiry.isoformat(),
            },
        )
    else:
        user_id = str(uuid.uuid4())

        users_table.put_item(
            Item={
                "user_id": user_id,
                "email": email,
                "otp": otp,
                "otp_expiry": otp_expiry.isoformat(),
            }
        )

    send_otp(email, otp)

    return jsonify(
        {"status": "success", "message": "OTP Sent, Please check your email"}
    )


@auth_bp.route("/login/verify-otp", methods=["POST"])
def login_verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    response = users_table.scan(
        FilterExpression="email = :email", ExpressionAttributeValues={":email": email}
    )
    items = response.get("Items")

    if not items:
        return jsonify({"status": "error", "message": "User not found"}, 404)

    user = items[0]
    otp_expiry = datetime.fromisoformat(user["otp_expiry"])

    if user.get("otp") != otp:
        return jsonify({"status": "error", "message": "Invalid OTP"}, 401)

    if datetime.now() > otp_expiry:
        return jsonify({"status": "error", "message": "OTP Expired"}, 401)

    session["user_id"] = user["user_id"]

    return jsonify(
        {"status": "success", "message": "OTP Verified", "user_id": user["user_id"]}
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"status": "success", "message": "Logged out"})
