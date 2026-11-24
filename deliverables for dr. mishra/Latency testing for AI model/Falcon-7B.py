import os
import requests
import time

API_URL = os.getenv("HF_INFERENCE_URL") or "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
token = os.environ["HF_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
	return response.json()

start = time.time()
output = query({
	"inputs": "Explain the rules of Candy Crush",
	"parameters": {
		"return_full_text": False,
		"max_time": 2.0
		}
})
end = time.time()
print(end - start)

start = time.time()
output = query({
	"inputs": "Why has there been an increase in the production of electric vehicles",
	"parameters": {
		"return_full_text": False,
		"max_time": 2.0
		}
})
end = time.time()
print(end - start)

start = time.time()
output = query({
	"inputs": "Why do gasoline cars emit more carbon dioxide than hybrid vehicles",
	"parameters": {
		"return_full_text": False,
		"max_time": 2.0
		}
})
end = time.time()
print(end - start)

start = time.time()
output = query({
	"inputs": "Can you name the planets in our solar system?",
	"parameters": {
		"return_full_text": False,
		"max_time": 2.0
		}
})
end = time.time()
print(end - start)

start = time.time()
output = query({
	"inputs": "In the context of advancing artificial intelligence, consider the ethical implications of creating highly autonomous systems with decision-making capabilities. How should society navigate the delicate balance between technological progress and the potential risks associated with AI, such as job displacement, bias in algorithms, and the potential for misuse? Additionally, what proactive measures and policies do you believe should be in place to ensure that AI development aligns with human values and benefits society as a whole?",
	"parameters": {
		"return_full_text": False,
		"max_time": 2.0
		}
})
end = time.time()
print(end - start)
