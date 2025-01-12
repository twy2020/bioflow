# src/config.py
import json
import os

CONFIG_FILE = 'config.json'

class Config:
    def __init__(self):
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(CONFIG_FILE):
            self.config_data = {
                "email": ""
            }
            self.save()
        else:
            # 从配置文件读取数据
            with open(CONFIG_FILE, 'r') as f:
                self.config_data = json.load(f)

    def save(self):
        # 保存配置文件
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def get_email(self):
        return self.config_data.get("email", "")

    def set_email(self, email):
        self.config_data["email"] = email
        self.save()
