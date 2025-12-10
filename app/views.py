from datetime import datetime, timezone

from flask import jsonify, request

from app import app, db
from app.models import User


# Healthcheck

@app.get("/healthcheck")
def healthcheck():
    return jsonify({
        "status": "ok",
        "date": datetime.now(timezone.utc).isoformat()
    }), 200



users = {}
categories = {}
records = {}

next_category_id = 1
next_record_id = 1


# Helpers

def error_response(message: str, status_code: int = 400):
    """Уніфікована відповідь з помилкою."""
    return jsonify({"error": message}), status_code


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
    }


# USERS 

@app.get("/user/<int:user_id>")
def get_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return error_response("User not found", 404)
    return jsonify(user_to_dict(user)), 200


@app.delete("/user/<int:user_id>")
def delete_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return error_response("User not found", 404)

    db.session.delete(user)
    db.session.commit()

    users.pop(user_id, None)

    to_delete = [rid for rid, rec in records.items() if rec["user_id"] == user_id]
    for rid in to_delete:
        del records[rid]

    return jsonify({"status": "deleted"}), 200


@app.post("/user")
def create_user():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not name:
        return error_response("Field 'name' is required")

    user = User(name=name)
    db.session.add(user)
    db.session.commit()

    users[user.id] = {"id": user.id, "name": user.name}

    return jsonify(user_to_dict(user)), 201


@app.get("/users")
def list_users():
    """Список усіх користувачів."""
    all_users = User.query.order_by(User.id.asc()).all()
    return jsonify([user_to_dict(u) for u in all_users]), 200


# CATEGORIES 
@app.get("/category")
def list_categories():
    return jsonify(list(categories.values())), 200


@app.post("/category")
def create_category():
    global next_category_id
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not name:
        return error_response("Field 'name' is required")

    category = {
        "id": next_category_id,
        "name": name,
    }
    categories[next_category_id] = category
    next_category_id += 1

    return jsonify(category), 201


@app.delete("/category")
def delete_category():
    category_id = request.args.get("id", type=int)
    if category_id is None:
        return error_response("Query parameter 'id' is required")

    if category_id not in categories:
        return error_response("Category not found", 404)

    del categories[category_id]

    # видаляємо всі записи з цією категорією
    to_delete = [rid for rid, rec in records.items() if rec["category_id"] == category_id]
    for rid in to_delete:
        del records[rid]

    return jsonify({"status": "deleted"}), 200

# RECORDS 

@app.get("/record/<int:record_id>")
def get_record(record_id: int):
    record = records.get(record_id)
    if record is None:
        return error_response("Record not found", 404)
    return jsonify(record), 200


@app.delete("/record/<int:record_id>")
def delete_record(record_id: int):
    if record_id not in records:
        return error_response("Record not found", 404)

    del records[record_id]
    return jsonify({"status": "deleted"}), 200


@app.post("/record")
def create_record():
    global next_record_id
    data = request.get_json(silent=True) or {}

    required_fields = ["user_id", "category_id", "amount"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    user_id = data["user_id"]
    category_id = data["category_id"]

    if user_id not in users:
        return error_response("User does not exist")
    if category_id not in categories:
        return error_response("Category does not exist")

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return error_response("Field 'amount' must be a number")

    created_at = data.get("created_at")
    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()

    record = {
        "id": next_record_id,
        "user_id": user_id,
        "category_id": category_id,
        "created_at": created_at,
        "amount": amount,
    }

    records[next_record_id] = record
    next_record_id += 1

    return jsonify(record), 201


@app.get("/record")
def list_records():
    user_id = request.args.get("user_id", type=int)
    category_id = request.args.get("category_id", type=int)

    if user_id is None and category_id is None:
        return error_response("At least one of 'user_id' or 'category_id' must be provided")

    result = []
    for rec in records.values():
        if user_id is not None and rec["user_id"] != user_id:
            continue
        if category_id is not None and rec["category_id"] != category_id:
            continue
        result.append(rec)

    return jsonify(result), 200
