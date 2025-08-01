# file: test/data_manager.py

import os
import json
import shutil
from datetime import datetime

class DataManager:
    """Kelas untuk mengelola operasi data seperti load, save, dan delete file."""
    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def get_topics(self):
        """Mendapatkan daftar semua topic (folder)."""
        return sorted([d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))])

    def get_subjects(self, topic_path):
        """Mendapatkan daftar semua subject (file .json) dalam sebuah topic."""
        if not topic_path:
            return []
        return sorted([f for f in os.listdir(topic_path) if f.endswith('.json')])

    def load_content(self, file_path):
        """Memuat konten dari file JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"content": [], "metadata": None}

    def save_content(self, file_path, content):
        """Menyimpan konten ke file JSON."""
        if file_path and content is not None:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

    def create_directory(self, path):
        """Membuat direktori baru."""
        os.makedirs(path)

    def rename_path(self, old_path, new_path):
        """Mengubah nama file atau direktori."""
        os.rename(old_path, new_path)

    def delete_directory(self, path):
        """Menghapus direktori dan semua isinya."""
        shutil.rmtree(path)

    def delete_file(self, path):
        """Menghapus file."""
        os.remove(path)