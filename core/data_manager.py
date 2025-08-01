# file: test/core/data_manager.py

import os
import json
import shutil
import zipfile
from datetime import datetime

import config

# Fungsi bantuan untuk pengurutan tanggal
def _get_sort_key_for_date(item):
    """Mengembalikan objek datetime untuk pengurutan. Item tanpa tanggal diletakkan di akhir."""
    date_str = item.get('date', '')
    if date_str:
        try:
            # Menggunakan format tanggal yang konsisten
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Jika format tanggal salah, anggap sebagai tanggal di masa depan jauh
            return datetime.max
    # Jika tidak ada tanggal, letakkan di akhir
    return datetime.max

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
            self.ensure_directory_exists(os.path.dirname(self.task_data_file))
            # Menggunakan list untuk 'categories' agar urutan terjaga
            self.save_tasks_data({"categories": []})

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
        """Mendapatkan daftar semua subject dalam sebuah topic, diurutkan berdasarkan tanggal terlama."""
        if not topic_path or not os.path.exists(topic_path):
            return []
        subjects = []
        for f in os.listdir(topic_path):
            if f.endswith('.json') and f != 'topic_config.json':
                content = self.load_content(os.path.join(topic_path, f))
                metadata = content.get('metadata', {})
                date = metadata.get('earliest_date')
                code = metadata.get('earliest_code')
                icon = metadata.get('icon', config.DEFAULT_SUBJECT_ICON)
                subjects.append({'name': f.replace('.json', ''), 'date': date, 'code': code, 'icon': icon})
        
        # Mengurutkan subject berdasarkan tanggal (yang terlama lebih dulu)
        subjects.sort(key=_get_sort_key_for_date)
        
        # Mengubah format kembali ke tuple untuk kompatibilitas
        return [(s['name'], s['date'], s['code'], s['icon']) for s in subjects]


    def load_content(self, file_path):
        """Memuat konten dari file JSON generik."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            if file_path != self.task_data_file:
                return {"content": [], "metadata": {}}
            return {"categories": []} # Mengembalikan list kosong

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
            topics_path = self.base_path
            if os.path.exists(topics_path):
                for root, _, files in os.walk(topics_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, base_dir_for_zip))
            
            if os.path.exists(self.task_data_file):
                zipf.write(self.task_data_file, os.path.relpath(self.task_data_file, base_dir_for_zip))

    def import_backup_zip(self, zip_path):
        """
        Mengimpor backup zip.
        - Untuk tasks: menimpa data yang ada.
        - Untuk topics: menambahkan topic baru, dan jika ada nama yang sama,
          topic dari backup akan diganti namanya dengan tambahan ' (new)'.
        """
        temp_extract_path = os.path.join(os.path.dirname(self.base_path), "temp_backup_extract")
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)
        os.makedirs(temp_extract_path)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_extract_path)

            # --- Proses Tasks: Timpa file task yang lama dengan yang baru dari backup ---
            backup_task_file_rel_path = os.path.relpath(self.task_data_file, os.path.dirname(self.base_path))
            backup_task_file_abs_path = os.path.join(temp_extract_path, backup_task_file_rel_path)
            
            if os.path.exists(backup_task_file_abs_path):
                # Hapus file task lama jika ada
                if os.path.exists(self.task_data_file):
                    os.remove(self.task_data_file)
                # Pindahkan file task dari backup ke lokasi seharusnya
                shutil.move(backup_task_file_abs_path, self.task_data_file)

            # --- Proses Topics: Tambahkan topic baru, ganti nama jika duplikat ---
            backup_topics_dir_rel_path = os.path.relpath(self.base_path, os.path.dirname(self.base_path))
            backup_topics_dir_abs_path = os.path.join(temp_extract_path, backup_topics_dir_rel_path)

            if os.path.isdir(backup_topics_dir_abs_path):
                existing_topics = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
                
                for topic_name in os.listdir(backup_topics_dir_abs_path):
                    source_topic_path = os.path.join(backup_topics_dir_abs_path, topic_name)
                    if not os.path.isdir(source_topic_path):
                        continue

                    dest_topic_name = topic_name
                    # Jika topic sudah ada, tambahkan suffix '(new)'
                    if topic_name in existing_topics:
                        dest_topic_name = f"{topic_name} (new)"
                        # Antisipasi jika "topic (new)" juga sudah ada
                        counter = 1
                        while os.path.exists(os.path.join(self.base_path, dest_topic_name)):
                            counter += 1
                            dest_topic_name = f"{topic_name} (new {counter})"

                    dest_topic_path = os.path.join(self.base_path, dest_topic_name)
                    shutil.move(source_topic_path, dest_topic_path)

        finally:
            # Bersihkan direktori sementara
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path)

            # Pastikan direktori dan file utama ada setelah proses
            self.ensure_directory_exists(self.base_path)
            self.ensure_task_file_exists()

    # --- Metode untuk Tasks (Bekerja dengan Satu File) ---

    def load_tasks_data(self):
        """Memuat seluruh data task dari file my_tasks.json."""
        return self.load_content(self.task_data_file)

    def save_tasks_data(self, data):
        """Menyimpan seluruh data task ke file my_tasks.json."""
        self.save_content(self.task_data_file, data)

    def get_task_categories(self):
        """Mendapatkan daftar semua kategori task dari file."""
        tasks_data = self.load_tasks_data()
        # Data sekarang adalah list, bukan dictionary
        return tasks_data.get("categories", [])

    def create_task_category(self, name):
        """Membuat kategori task baru dalam file JSON."""
        tasks_data = self.load_tasks_data()
        # Cek duplikasi nama
        if not any(cat['name'] == name for cat in tasks_data.get("categories", [])):
            new_category = {
                "name": name, 
                "icon": config.DEFAULT_CATEGORY_ICON, 
                "tasks": []
            }
            tasks_data.setdefault("categories", []).append(new_category)
            self.save_tasks_data(tasks_data)

    def rename_task_category(self, old_name, new_name):
        """Mengubah nama kategori task dalam file JSON."""
        tasks_data = self.load_tasks_data()
        categories = tasks_data.get("categories", [])
        # Cek duplikasi nama baru
        if any(cat['name'] == new_name for cat in categories):
            return
        for category in categories:
            if category['name'] == old_name:
                category['name'] = new_name
                self.save_tasks_data(tasks_data)
                break
    
    def update_task_category_icon(self, category_name, new_icon):
        """Memperbarui ikon untuk kategori task tertentu."""
        tasks_data = self.load_tasks_data()
        categories = tasks_data.get("categories", [])
        for category in categories:
            if category['name'] == category_name:
                category['icon'] = new_icon
                self.save_tasks_data(tasks_data)
                break

    def delete_task_category(self, name):
        """Menghapus kategori task dari file JSON."""
        tasks_data = self.load_tasks_data()
        categories = tasks_data.get("categories", [])
        tasks_data["categories"] = [cat for cat in categories if cat['name'] != name]
        self.save_tasks_data(tasks_data)
        
    def get_tasks(self, category_name, sort_by='date', sort_order='asc'):
        """
        Mendapatkan semua task dari sebuah kategori.
        Pengurutan tidak lagi dilakukan di sini, tapi mengikuti urutan di JSON.
        """
        tasks_data = self.load_tasks_data()
        categories = tasks_data.get("categories", [])
        for category in categories:
            if category.get('name') == category_name:
                return category.get("tasks", [])
        return []

    def get_all_tasks(self, sort_by='date', sort_order='asc'):
        """
        Mendapatkan semua task dari semua kategori.
        Pengurutan sekarang berdasarkan tanggal untuk semua task gabungan.
        """
        tasks_data = self.load_tasks_data()
        all_tasks = []
        for category in tasks_data.get("categories", []):
            for task in category.get("tasks", []):
                task_copy = task.copy()
                task_copy['name'] = f"[{category.get('name')}] {task.get('name')}"
                task_copy['original_name'] = task.get('name')
                task_copy['category'] = category.get('name')
                all_tasks.append(task_copy)

        # Logika pengurutan
        reverse_order = (sort_order == 'desc')
        if sort_by == 'date':
            all_tasks.sort(key=_get_sort_key_for_date, reverse=reverse_order)
        elif sort_by == 'count':
            all_tasks.sort(key=lambda x: x.get('count', 0), reverse=reverse_order)
        else: # default ke 'name'
            all_tasks.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse_order)

        return all_tasks

    def save_task(self, category_name, task_name, data):
        """Menyimpan data sebuah task ke dalam kategori di file JSON."""
        tasks_data = self.load_tasks_data()
        for category in tasks_data.get("categories", []):
            if category.get('name') == category_name:
                task_found = False
                for i, task in enumerate(category.get("tasks", [])):
                    if task.get('name') == task_name:
                        category["tasks"][i] = data
                        task_found = True
                        break
                if not task_found:
                    category.setdefault("tasks", []).append(data)
                self.save_tasks_data(tasks_data)
                return

    def delete_task(self, category_name, task_name):
        """Menghapus sebuah task dari kategori di file JSON."""
        tasks_data = self.load_tasks_data()
        for category in tasks_data.get("categories", []):
            if category.get('name') == category_name:
                category["tasks"] = [task for task in category.get("tasks", []) if task.get('name') != task_name]
                self.save_tasks_data(tasks_data)
                return