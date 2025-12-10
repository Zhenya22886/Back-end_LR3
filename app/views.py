from datetime import datetime, timezone

from flask import jsonify, request

from app import app, db
from app.models import User, Category, Record, Account  


# Healthcheck

@app.get("/healthcheck")
def healthcheck():
    return jsonify({
        "status": "ok",
        "date": datetime.now(timezone.utc).isoformat()
    }), 200


# Helpers

def error_response(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
    }


def category_to_dict(category: Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
    }


def record_to_dict(record: Record) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "category_id": record.category_id,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "amount": float(record.amount) if record.amount is not None else None,
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

    return jsonify(user_to_dict(user)), 201


@app.get("/users")
def list_users():
    all_users = User.query.order_by(User.id.asc()).all()
    return jsonify([user_to_dict(u) for u in all_users]), 200


# CATEGORIES 
@app.get("/category")
def list_categories():
    categories = Category.query.order_by(Category.id.asc()).all()
    return jsonify([category_to_dict(c) for c in categories]), 200


@app.post("/category")
def create_category():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    if not name:
        return error_response("Field 'name' is required")

    category = Category(name=name)
    db.session.add(category)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response("Category with this name already exists", 400)

    return jsonify(category_to_dict(category)), 201


@app.delete("/category")
def delete_category():
    category_id = request.args.get("id", type=int)
    if category_id is None:
        return error_response("Query parameter 'id' is required")

    category = Category.query.get(category_id)
    if category is None:
        return error_response("Category not found", 404)

    db.session.delete(category)
    db.session.commit()

    return jsonify({"status": "deleted"}), 200

# RECORDS 

@app.get("/record/<int:record_id>")
def get_record(record_id: int):
    record = Record.query.get(record_id)
    if record is None:
        return error_response("Record not found", 404)
    return jsonify(record_to_dict(record)), 200


@app.delete("/record/<int:record_id>")
def delete_record(record_id: int):
    record = Record.query.get(record_id)
    if record is None:
        return error_response("Record not found", 404)

    db.session.delete(record)
    db.session.commit()

    return jsonify({"status": "deleted"}), 200


@app.post("/record")
def create_record():
    data = request.get_json(silent=True) or {}

    required_fields = ["user_id", "category_id", "amount"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}")

    user_id = data["user_id"]
    category_id = data["category_id"]

    user = User.query.get(user_id)
    if user is None:
        return error_response("User does not exist")

    category = Category.query.get(category_id)
    if category is None:
        return error_response("Category does not exist")

    try:
        amount_value = float(data["amount"])
    except (TypeError, ValueError):
        return error_response("Field 'amount' must be a number")

    if amount_value <= 0:
        return error_response("Field 'amount' must be positive")

    created_at_str = data.get("created_at")
    if created_at_str:
        try:
            created_at = datetime.fromisoformat(created_at_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
        except ValueError:
            return error_response("Field 'created_at' must be valid ISO datetime")
    else:
        created_at = datetime.now(timezone.utc)

    record = Record(
        user_id=user.id,
        category_id=category.id,
        created_at=created_at,
        amount=amount_value,
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(record_to_dict(record)), 201


@app.get("/record")
def list_records():
    user_id = request.args.get("user_id", type=int)
    category_id = request.args.get("category_id", type=int)

    if user_id is None and category_id is None:
        return error_response("At least one of 'user_id' or 'category_id' must be provided")

    query = Record.query

    if user_id is not None:
        query = query.filter(Record.user_id == user_id)
    if category_id is not None:
        query = query.filter(Record.category_id == category_id)

    records = query.order_by(Record.id.asc()).all()
    return jsonify([record_to_dict(r) for r in records]), 200
