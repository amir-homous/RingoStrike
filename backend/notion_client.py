import requests

class NotionClient:
    def __init__(self, token: str, notion_version: str = "2022-06-28"):
        self.base = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": notion_version,
            "Content-Type": "application/json",
        }

    def query_db(self, database_id: str, payload: dict):
        url = f"{self.base}/databases/{database_id}/query"
        r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def create_page(self, database_id: str, properties: dict):
        url = f"{self.base}/pages"
        payload = {"parent": {"database_id": database_id}, "properties": properties}
        r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def update_page(self, page_id: str, properties: dict):
        url = f"{self.base}/pages/{page_id}"
        payload = {"properties": properties}
        r = requests.patch(url, headers=self.headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def retrieve_page(self, page_id: str):
        url = f"{self.base}/pages/{page_id}"
        r = requests.get(url, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def retrieve_database(self, database_id: str):
        url = f"{self.base}/databases/{database_id}"
        r = requests.get(url, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()
