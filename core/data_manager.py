# file: core/data_manager.py

import os
import json
import shutil
import zipfile
from datetime import datetime

import config

class DataManager:
    """Kelas untuk mengelola semua operasi file dan data."""
    def __init__(self, base_path):
        self.base_path = base_path
        # Inisialisasi path untuk tasks
        self.task_base_path = os.path.join(self.base_path, 'tasks')
        
        # === PERBAIKAN UTAMA ADA DI SINI ===
        # Pastikan direktori utama dan direktori task ada saat aplikasi dimulai
        self.ensure_directory_exists(self.base_path)
        self.ensure_directory_exists(self.task_base_path)

    def ensure_directory_exists(self, path):
        """Membuat direktori jika belum ada."""
        os.makedirs(path, exist_ok=True)

    # --- Metode untuk Topics dan Subjects (Konten Utama) ---

    def get_topics(self):
        """Mendapatkan daftar semua topic beserta ikonnya."""
        topics_data = []
        for d in sorted([d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]):
            if d == 'tasks': continue # Lewati folder task
            
            config_path = os.path.join(self.base_path, d, 'topic_config.json')
            icon = config.DEFAULT_TOPIC_ICON
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        topic_config = json.load(f)
                        icon = topic_config.get('icon', config.DEFAULT_TOPIC_ICON)
                except (json.JSONDecodeError, IOError):
                    pass # Gunakan ikon default jika ada masalah
            topics_data.append({'name': d, 'icon': icon})
        return topics_data

    def get_subjects(self, topic_path):
        """Mendapatkan daftar semua subject dalam sebuah topic."""
        if not topic_path or not os.path.exists(topic_path):
            return []
        subjects = []
        for f in sorted(os.listdir(topic_path)):
            if f.endswith('.json') and f != 'topic_config.json':
                content = self.load_content(os.path.join(topic_path, f))
                metadata = content.get('metadata', {})
                date = metadata.get('earliest_date')
                code = metadata.get('earliest_code')
                icon = metadata.get('icon', config.DEFAULT_SUBJECT_ICON)
                subjects.append((f.replace('.json', ''), date, code, icon))
        return subjects

    def load_content(self, file_path):
        """Memuat konten dari file JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"content": [], "metadata": {}}

    def save_content(self, file_path, data):
        """Menyimpan data ke file JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def save_topic_config(self, topic_name, data):
        """Menyimpan konfigurasi (seperti ikon) untuk sebuah topic."""
        config_path = os.path.join(self.base_path, topic_name, 'topic_config.json')
        self.save_content(config_path, data)

    def create_directory(self, path):
        os.makedirs(path, exist_ok=True)

    def rename_path(self, old_path, new_path):
        os.rename(old_path, new_path)

    def delete_directory(self, path):
        shutil.rmtree(path)

    def delete_file(self, path):
        os.remove(path)
        
    def create_backup_zip(self, zip_path):
        """Membuat backup dari semua folder topic ke dalam satu file zip."""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.base_path):
                # Jangan sertakan folder 'tasks' dalam backup
                if 'tasks' in root.split(os.sep):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    # Tulis ke zip dengan path relatif dari base_path
                    zipf.write(file_path, os.path.relpath(file_path, self.base_path))

    def import_backup_zip(self, zip_path):
        """Mengimpor dan mengekstrak backup zip ke base_path."""
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(self.base_path)

    # --- Metode Baru untuk Tasks ---

    def get_task_categories(self):
        """Mendapatkan daftar semua kategori task."""
        if not os.path.exists(self.task_base_path):
            return []
        
        categories_data = []
        # Menggunakan list comprehension yang aman
        dir_contents = os.listdir(self.task_base_path)
        subdirectories = [d for d in dir_contents if os.path.isdir(os.path.join(self.task_base_path, d))]
        
        for d in sorted(subdirectories):
            # Asumsi kategori task juga bisa punya config untuk ikon, dll.
            # Untuk saat ini, kita gunakan ikon default.
            categories_data.append({'name': d, 'icon': '📂'})
        return categories_data

    def create_task_category(self, name):
        """Membuat folder untuk kategori task baru."""
        self.ensure_directory_exists(os.path.join(self.task_base_path, name))

    def rename_task_category(self, old_name, new_name):
        """Mengubah nama folder kategori task."""
        old_path = os.path.join(self.task_base_path, old_name)
        new_path = os.path.join(self.task_base_path, new_name)
        self.rename_path(old_path, new_path)

    def delete_task_category(self, name):
        """Menghapus folder kategori task."""
        self.delete_directory(os.path.join(self.task_base_path, name))

    def get_tasks(self, category_name):
        """Mendapatkan semua task dari sebuah kategori."""
        category_path = os.path.join(self.task_base_path, category_name)
        if not os.path.exists(category_path):
            return []
        
        tasks = []
        for f in sorted(os.listdir(category_path)):
            if f.endswith('.json'):
                task_data = self.load_content(os.path.join(category_path, f))
                tasks.append({
                    'name': f.replace('.json', ''),
                    'count': task_data.get('count', 0),
                    'date': task_data.get('date', '')
                })
        return tasks

    def save_task(self, category_name, task_name, data):
        """Menyimpan data sebuah task ke dalam file JSON."""
        category_path = os.path.join(self.task_base_path, category_name)
        self.ensure_directory_exists(category_path)
        self.save_content(os.path.join(category_path, f"{task_name}.json"), data)

    def delete_task(self, category_name, task_name):
        """Menghapus file sebuah task."""
        file_path = os.path.join(self.task_base_path, category_name, f"{task_name}.json")
        if os.path.exists(file_path):
            self.delete_file(file_path)