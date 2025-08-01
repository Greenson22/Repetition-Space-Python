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
        # Path untuk file data task tunggal
        self.task_data_file = config.TASK_BASE_PATH
        
        # Pastikan direktori utama ada
        self.ensure_directory_exists(os.path.dirname(self.base_path))
        # Pastikan file task ada, jika tidak buat file kosong
        self.ensure_task_file_exists()

    def ensure_directory_exists(self, path):
        """Membuat direktori jika belum ada."""
        os.makedirs(path, exist_ok=True)

    def ensure_task_file_exists(self):
        """Memastikan file task JSON ada. Jika tidak, buat struktur default."""
        if not os.path.exists(self.task_data_file):
            # Membuat direktori jika belum ada
            self.ensure_directory_exists(os.path.dirname(self.task_data_file))
            # Membuat file dengan struktur data awal (kosong)
            self.save_tasks_data({"categories": {}})

    # --- Metode untuk Topics dan Subjects (Konten Utama) ---

    def get_topics(self):
        """Mendapatkan daftar semua topic beserta ikonnya."""
        if not os.path.exists(self.base_path):
            return []
        topics_data = []
        for d in sorted([d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]):
            config_path = os.path.join(self.base_path, d, 'topic_config.json')
            icon = config.DEFAULT_TOPIC_ICON
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        topic_config = json.load(f)
                        icon = topic_config.get('icon', config.DEFAULT_TOPIC_ICON)
                except (json.JSONDecodeError, IOError):
                    pass 
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
        """Memuat konten dari file JSON generik."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Untuk konten subject, kembalikan struktur default
            if file_path != self.task_data_file:
                return {"content": [], "metadata": {}}
            # Untuk file task, kembalikan struktur task default
            return {"categories": {}}


    def save_content(self, file_path, data):
        """Menyimpan data ke file JSON generik."""
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
        """Membuat backup dari semua folder topic dan file task ke dalam satu file zip."""
        base_dir_for_zip = os.path.dirname(self.base_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup folder topics
            topics_path = self.base_path
            if os.path.exists(topics_path):
                for root, _, files in os.walk(topics_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, base_dir_for_zip))
            
            # Backup file my_tasks.json
            if os.path.exists(self.task_data_file):
                zipf.write(self.task_data_file, os.path.relpath(self.task_data_file, base_dir_for_zip))


    def import_backup_zip(self, zip_path):
        """Mengimpor dan mengekstrak backup zip ke base_path."""
        base_dir_for_zip = os.path.dirname(self.base_path)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(base_dir_for_zip)

    # --- Metode Baru untuk Tasks (Bekerja dengan Satu File) ---

    def load_tasks_data(self):
        """Memuat seluruh data task dari file my_tasks.json."""
        return self.load_content(self.task_data_file)

    def save_tasks_data(self, data):
        """Menyimpan seluruh data task ke file my_tasks.json."""
        self.save_content(self.task_data_file, data)

    def get_task_categories(self):
        """Mendapatkan daftar semua kategori task dari file."""
        tasks_data = self.load_tasks_data()
        categories = tasks_data.get("categories", {})
        
        categories_data = []
        for name in sorted(categories.keys()):
            # Di masa depan, ikon bisa disimpan per kategori di dalam JSON
            categories_data.append({'name': name, 'icon': '📂'})
        return categories_data

    def create_task_category(self, name):
        """Membuat kategori task baru dalam file JSON."""
        tasks_data = self.load_tasks_data()
        if name not in tasks_data["categories"]:
            tasks_data["categories"][name] = {"tasks": {}}
            self.save_tasks_data(tasks_data)

    def rename_task_category(self, old_name, new_name):
        """Mengubah nama kategori task dalam file JSON."""
        tasks_data = self.load_tasks_data()
        if old_name in tasks_data["categories"] and new_name not in tasks_data["categories"]:
            tasks_data["categories"][new_name] = tasks_data["categories"].pop(old_name)
            self.save_tasks_data(tasks_data)

    def delete_task_category(self, name):
        """Menghapus kategori task dari file JSON."""
        tasks_data = self.load_tasks_data()
        if name in tasks_data["categories"]:
            del tasks_data["categories"][name]
            self.save_tasks_data(tasks_data)

    def get_tasks(self, category_name):
        """Mendapatkan semua task dari sebuah kategori dalam file JSON."""
        tasks_data = self.load_tasks_data()
        category = tasks_data.get("categories", {}).get(category_name)
        
        if not category:
            return []
            
        tasks_list = []
        for task_name, task_details in sorted(category.get("tasks", {}).items()):
            tasks_list.append({
                'name': task_name,
                'count': task_details.get('count', 0),
                'date': task_details.get('date', '')
            })
        return tasks_list
    
    def get_all_tasks(self):
        """Mendapatkan semua task dari semua kategori."""
        tasks_data = self.load_tasks_data()
        all_tasks = []
        for category_name, category_details in tasks_data.get("categories", {}).items():
            for task_name, task_details in category_details.get("tasks", {}).items():
                 all_tasks.append({
                    'name': f"[{category_name}] {task_name}", # Tambahkan prefix kategori
                    'count': task_details.get('count', 0),
                    'date': task_details.get('date', ''),
                    'original_name': task_name, # Simpan nama asli dan kategori
                    'category': category_name
                })
        return sorted(all_tasks, key=lambda x: x['name'])


    def save_task(self, category_name, task_name, data):
        """Menyimpan data sebuah task ke dalam kategori di file JSON."""
        tasks_data = self.load_tasks_data()
        if category_name in tasks_data["categories"]:
            tasks_data["categories"][category_name]["tasks"][task_name] = data
            self.save_tasks_data(tasks_data)

    def delete_task(self, category_name, task_name):
        """Menghapus sebuah task dari kategori di file JSON."""
        tasks_data = self.load_tasks_data()
        if category_name in tasks_data["categories"] and task_name in tasks_data["categories"][category_name]["tasks"]:
            del tasks_data["categories"][category_name]["tasks"][task_name]
            self.save_tasks_data(tasks_data)