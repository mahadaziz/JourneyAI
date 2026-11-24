import os
import unittest
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import mongomock
import pandas as pd


SAMPLE = Path(__file__).resolve().parents[3] / "examples" / "vehicles.csv"


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch("dotenv.load_dotenv"), patch.dict(os.environ, {"MONGO_URI": "mongodb://localhost/db"}):
            with patch("pymongo.mongo_client.MongoClient", mongomock.MongoClient):
                from application import app
        cls.client = app.test_client()

    def setUp(self):
        self.db = mongomock.MongoClient().db
        self.enterContext(patch("application.routes.db", self.db))
        self.enterContext(patch("application.models.db", self.db))

    def test_empty_database(self):
        self.assertEqual(self.client.get("/").get_data(as_text=True), "home")
        response = self.client.post("/get_column_names", json={})
        self.assertEqual(response.get_json(), {"column_names": []})

    def test_sample_columns_produce_graphs(self):
        frame = pd.read_csv(SAMPLE)
        self.db.cars.insert_many(frame.to_dict("records"))
        for column in frame:
            with self.subTest(column=column):
                response = self.client.post("/get_insights", json={
                    "column_name": column, "insight_count": 4, "prev_insights": [],
                })
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.get_json()["insights"]["graphs"])

    def test_hypotheses_without_a_token(self):
        with patch.dict(os.environ, {"HF_TOKEN": ""}):
            response = self.client.post("/get_hypothesis", json={})
        self.assertEqual(response.status_code, 503)

    def test_sparse_columns_and_count_header(self):
        rows = [
            {"year": 2022, "count": "West", "sales": None},
            {"year": 2023, "count": "East", "sales": 12},
        ]
        for column in rows[0]:
            with self.subTest(column=column):
                response = self.client.post("/get_insights", json={"rows": rows, "column_name": column})
                self.assertEqual(response.status_code, 200)

    def test_upload_requires_a_current_ticket(self):
        self.db.upload_tickets.insert_one({
            "_id": "expired", "user_id": "writer", "expires_at": datetime.utcnow() - timedelta(seconds=1),
        })
        response = self.upload("x,y\n1,2", "expired")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.db.datasets.count_documents({}), 0)

    def upload(self, csv, token):
        return self.client.post("/upload_dataset", data={
            "file": (BytesIO(csv.encode()), "sample.csv"), "title": "Weekly report",
            "upload_ticket": token,
        })

    def test_upload_and_analyze_distinct_datasets_with_the_same_title(self):
        tables = [
            ("north", "region,sales\nEast,10\nWest,20\nEast,30", "region", "sales"),
            ("south", "section,visits\nNews,7\nArts,15", "section", "visits"),
        ]
        ids = []
        for token, csv, group, measure in tables:
            self.db.upload_tickets.insert_one({
                "_id": token, "user_id": "writer", "expires_at": datetime.utcnow() + timedelta(minutes=1),
            })
            uploaded = self.upload(csv, token)
            self.assertEqual(uploaded.status_code, 200)
            self.assertEqual(uploaded.json["column_names"], [group, measure])
            ids.append(uploaded.json["dataset_id"])
            document = self.db.documents.find_one({"dataset_id": ids[-1]})
            self.assertEqual(document["user_id"], "writer")
            rows = self.db.datasets.find_one({"column_names": [group, measure]})["data"]
            result = self.client.post("/get_insights", json={
                "rows": rows, "column_name": group, "insight_count": 18,
            })
            self.assertEqual(result.status_code, 200)
            graphs = result.json["insights"]["graphs"]
            self.assertTrue(graphs)
            self.assertTrue(all(graph[1:3] == [group, measure] for graph in graphs.values()))
            self.assertEqual(self.upload(csv, token).status_code, 401)
        self.assertNotEqual(*ids)
        self.assertEqual(self.db.cars.count_documents({}), 0)
