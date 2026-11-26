import json
import os
import unittest
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import mongomock
import pandas as pd
import requests


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
        self.enterContext(patch.dict(os.environ, {"GROQ_API_KEY": "", "HF_TOKEN": "", "HF_INFERENCE_URL": ""}))
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
        response = self.client.post("/get_hypothesis", json={})
        self.assertEqual(response.status_code, 503)

    def hypothesis_body(self, dataset_id="vehicles", column_name="year", **fields):
        self.db.hypothesis_tickets.insert_one({
            "_id": "one-use", "dataset_id": dataset_id, "dataset_name": "Vehicles",
            "column_name": column_name, "user_id": "writer",
            "expires_at": datetime.utcnow() + timedelta(minutes=1),
        })
        return {"hypothesis_ticket": "one-use", **fields}

    def test_chat_hypothesis_and_feedback(self):
        options = {"HF_TOKEN": "test", "HF_MODEL": "test-model"}
        with patch.dict(os.environ, options), patch("application.models.requests.post") as send:
            send.return_value.json.return_value = {
                "choices": [{"message": {"content": "Newer engines may use less fuel."}}]
            }
            response = self.client.post("/get_hypothesis", json=self.hypothesis_body(
                selected_insights=["City consumption fell from 10.6 to 9.2 L/100 km."],
            ))
        self.assertEqual(response.status_code, 200)
        text, = response.json["data"]
        self.assertEqual(text, "Newer engines may use less fuel.")
        args, kwargs = send.call_args
        self.assertEqual(args[0], "https://router.huggingface.co/v1/chat/completions")
        self.assertEqual(kwargs["json"]["model"], "test-model")
        self.assertIn("10.6 to 9.2", kwargs["json"]["messages"][-1]["content"])
        log_id = response.json["hypothesis_ids"][text]
        self.assertEqual(self.client.post("/good_hypothesis", json={"hypothesis_id": log_id}).status_code, 200)
        self.assertTrue(self.db.Hypothesis_logs.find_one({"_id": log_id})["Thumbs_Up"])

    def test_vehicle_hypothesis_uses_years_from_the_writers_upload(self):
        rows = pd.read_csv(SAMPLE).to_dict("records")
        dataset_id = self.db.datasets.insert_one({"user_id": "writer", "data": rows}).inserted_id
        self.db.datasets.insert_one({"user_id": "another-writer", "data": [{"model year": 2016}]})
        finding = "The maximum city consumption was 13.4 L/100 km for a 2018 model."
        cases = [
            ("Compare the mean for 2018 with vehicles from 2016 and 2017.", 502),
            ("Vehicle class may explain the peak. Compare SUVs in 2018 and 2023.", 200),
        ]
        with patch.dict(os.environ, {"GROQ_API_KEY": "test"}), patch("application.models.requests.post") as send:
            for answer, status in cases:
                with self.subTest(answer=answer):
                    send.return_value.json.return_value = {"choices": [{"message": {"content": answer}}]}
                    body = self.hypothesis_body(str(dataset_id), "model year", selected_insights=[finding])
                    response = self.client.post("/get_hypothesis", json=body)
                    self.assertEqual(response.status_code, status)
                    prompt = json.loads(send.call_args.kwargs["json"]["messages"][-1]["content"])
                    self.assertEqual(prompt["examples_of_observed_years"], list(range(2018, 2024)))
                    if status == 502:
                        self.assertEqual(self.db.Hypothesis_logs.count_documents({}), 0)
                        self.assertEqual(self.db.hypothesis_history.count_documents({}), 0)
                    else:
                        self.assertEqual(response.json["data"], [answer])

    def test_year_coverage_preserves_gaps_and_accepts_measurements_in_the_finding(self):
        rows = [{"model year": value} for value in (2018.0, None, "2020")]
        dataset_id = self.db.datasets.insert_one({"user_id": "writer", "data": rows}).inserted_id
        finding = "The heaviest 2018 vehicle weighed 2100 kg."
        with patch.dict(os.environ, {"HF_TOKEN": "test"}), patch("application.models.requests.post") as send:
            for year, status in [(2019, 502), (2020, 200)]:
                send.return_value.json.return_value = {
                    "choices": [{"message": {"content": f"Compare the 2100 kg vehicle with models from {year}."}}]
                }
                body = self.hypothesis_body(str(dataset_id), "model year", selected_insights=[finding])
                response = self.client.post("/get_hypothesis", json=body)
                self.assertEqual(response.status_code, status)
                prompt = json.loads(send.call_args.kwargs["json"]["messages"][-1]["content"])
                self.assertEqual(prompt["examples_of_observed_years"], [2018, 2020])

    def test_custom_text_generation_endpoint(self):
        url = "https://example.test/generate"
        with patch.dict(os.environ, {"HF_TOKEN": "test", "HF_INFERENCE_URL": url}), patch("application.models.requests.post") as send:
            send.return_value.json.return_value = [{"generated_text": "Engine size may explain the change."}]
            response = self.client.post("/get_hypothesis", json=self.hypothesis_body(context="Cars used less fuel."))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"], ["Engine size may explain the change."])
        self.assertEqual(send.call_args.args[0], url)
        self.assertIn("Cars used less fuel.", send.call_args.kwargs["json"]["inputs"])

    def test_provider_failure_preserves_history_for_retry(self):
        denied = requests.Response()
        denied.status_code = 403
        with patch.dict(os.environ, {"HF_TOKEN": "test"}), patch("application.models.requests.post") as send:
            send.return_value = denied
            response = self.client.post("/get_hypothesis", json=self.hypothesis_body(context="Sales doubled."))
        self.assertEqual(response.status_code, 502)
        self.assertIn("inference permissions", response.json["error"])
        self.assertEqual(self.db.Hypothesis_logs.count_documents({}), 0)
        self.assertEqual(self.db.hypothesis_history.count_documents({}), 0)

    def test_groq_uses_its_own_key_and_scopes_history_to_ticket(self):
        config = {"GROQ_API_KEY": "groq-test-key", "HF_TOKEN": "hf-test-key"}
        with patch.dict(os.environ, config), patch("application.models.requests.post") as send:
            send.return_value.json.return_value = {"choices": [{"message": {"content": "A testable explanation."}}]}
            body = self.hypothesis_body(context="Sales fell.", user_id="another-writer")
            response = self.client.post("/get_hypothesis", json=body)
            replay = self.client.post("/get_hypothesis", json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(replay.status_code, 401)
        send.assert_called_once()
        self.assertEqual(send.call_args.args[0], "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(send.call_args.kwargs["headers"], {"Authorization": "Bearer groq-test-key"})
        self.assertEqual(send.call_args.kwargs["json"]["model"], "openai/gpt-oss-20b")
        self.assertEqual(self.db.hypothesis_history.count_documents({"user_id": "another-writer"}), 0)

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
