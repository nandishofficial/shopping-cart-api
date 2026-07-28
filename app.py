import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask, jsonify, request


def create_app(database="cart.db", event_file="events.jsonl"):
    app = Flask(__name__)

    def connect():
        connection = sqlite3.connect(database)
        connection.row_factory = sqlite3.Row
        return connection

    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                product_id TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL CHECK (quantity > 0)
            )
            """
        )

    def emit(event_type, item):
        event = {
            "id": str(uuid4()),
            "type": event_type,
            "occurredAt": datetime.now(timezone.utc).isoformat(),
            "data": item,
        }
        with open(event_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")

    @app.get("/cart/items")
    def list_items():
        with connect() as db:
            rows = db.execute(
                "SELECT product_id, quantity FROM items ORDER BY product_id"
            ).fetchall()
        return jsonify(
            items=[
                {"productId": row["product_id"], "quantity": row["quantity"]}
                for row in rows
            ]
        )

    @app.post("/cart/items")
    def add_item():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify(error="JSON body is required"), 400

        product_id = data.get("productId")
        quantity = data.get("quantity")

        if not isinstance(product_id, str) or not product_id.strip():
            return jsonify(error="productId must be a non-empty string"), 400
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            return jsonify(error="quantity must be a positive integer"), 400

        item = {"productId": product_id.strip(), "quantity": quantity}
        try:
            with connect() as db:
                db.execute(
                    "INSERT INTO items (product_id, quantity) VALUES (?, ?)",
                    (item["productId"], item["quantity"]),
                )
        except sqlite3.IntegrityError:
            return jsonify(error="Product is already in the cart"), 409

        emit("CartItemAdded", item)
        return jsonify(item), 201

    @app.delete("/cart/items/<product_id>")
    def remove_item(product_id):
        with connect() as db:
            row = db.execute(
                "SELECT product_id, quantity FROM items WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if row is None:
                return jsonify(error="Item not found"), 404
            db.execute("DELETE FROM items WHERE product_id = ?", (product_id,))

        item = {"productId": row["product_id"], "quantity": row["quantity"]}
        emit("CartItemRemoved", item)
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(port=8080)

