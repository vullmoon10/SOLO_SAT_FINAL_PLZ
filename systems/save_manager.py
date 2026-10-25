import json
from pathlib import Path


class SaveManager:
    """플레이어 진행 상황을 JSON 파일로 저장/불러오기."""
    def __init__(self, path="solosat_save.json"):
        self.path = Path(path)

    def save(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self):
        if not self.path.exists():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
