import json
import tempfile
import unittest
from pathlib import Path

from app import create_app


class ShoppingCartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "cart.db"
        self.events = Path(self.temp.name) / "events.jsonl"
        self.client = create_app(self.database, self.events).test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_add_list_remove_and_events(self):
        response = self.client.post(
            "/cart/items",
            json={"productId": "keyboard-1", "quantity": 2},
        )
        self.assertEqual(201, response.status_code)

        response = self.client.get("/cart/items")
        self.assertEqual(
            [{"productId": "keyboard-1", "quantity": 2}],
            response.get_json()["items"],
        )

        response = self.client.delete("/cart/items/keyboard-1")
        self.assertEqual(204, response.status_code)

        events = [
            json.loads(line)
            for line in self.events.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            ["CartItemAdded", "CartItemRemoved"],
            [event["type"] for event in events],
        )

    def test_validation_conflict_not_found_and_persistence(self):
        self.assertEqual(
            400,
            self.client.post(
                "/cart/items",
                json={"productId": "", "quantity": 0},
            ).status_code,
        )

        item = {"productId": "book-1", "quantity": 1}
        self.assertEqual(201, self.client.post("/cart/items", json=item).status_code)
        self.assertEqual(409, self.client.post("/cart/items", json=item).status_code)
        self.assertEqual(
            404,
            self.client.delete("/cart/items/missing").status_code,
        )

        restarted_client = create_app(
            self.database,
            self.events,
        ).test_client()
        self.assertEqual(
            [item],
            restarted_client.get("/cart/items").get_json()["items"],
        )


if __name__ == "__main__":
    unittest.main()

