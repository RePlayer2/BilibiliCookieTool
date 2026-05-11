import json
import os
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

DEFAULT_CONFIG = {
    "bilibili": {
        "enabled": True,
        "cookies": "",
        "target_videos": [],
        "hot_comment_threshold": 100
    },
    "douyin": {
        "enabled": True,
        "cookies": "",
        "target_videos": []
    },
    "storage": {
        "image_dir": "data/images",
        "db_path": "data/db/meme_data.db"
    }
}

class Config:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def _save_config(self, config):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value):
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self._config)
