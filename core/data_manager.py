# file: test/core/data_manager.py

import os
import json
import shutil
from datetime import datetime
import config

class DataManager:
    """Kelas untuk mengelola operasi data seperti load, save, dan delete file."""
    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def create_backup_zip(self, zip_path):
        """Membuat arsip zip dari direktori base_path."""
        # Pastikan path untuk zip file tidak menyertakan ekstensi .zip,
        # karena make_archive akan menambahkannya secara otomatis.
        shutil.make_archive(
            base_name=os.path.splitext(zip_path)[0],
            format='zip',
            root_dir=os.path.dirname(self.base_path), # Direktori 'di atas' topics
            base_dir=os.path.basename(self.base_path) # Nama folder 'topics' itu sendiri
        )

    def get_topics(self):
        """Mendapatkan daftar semua topic (folder) beserta ikonnya."""
        topics = []
        for d in sorted([d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]):
            config_path = os.path.join(self.base_path, d, 'topic_config.json')
            icon = config.DEFAULT_TOPIC_ICON
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        icon = data.get('icon', config.DEFAULT_TOPIC_ICON)
                    except json.JSONDecodeError:
                        pass # Gunakan ikon default jika file config rusak
            topics.append({'name': d, 'icon': icon})
        return topics

    def save_topic_config(self, topic_name, data):
        """Menyimpan konfigurasi (termasuk ikon) untuk sebuah topic."""
        config_path = os.path.join(self.base_path, topic_name, 'topic_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _get_earliest_date_and_code(self, file_path):
        """
        Mendapatkan tanggal dan kode repetisi paling awal dari sebuah file subject.
        Prioritas membaca dari metadata untuk efisiensi.
        """
        content = self.load_content(file_path)
        metadata = content.get("metadata")

        # Coba baca dari metadata terlebih dahulu
        if metadata and "earliest_date" in metadata:
            # Pastikan earliest_date tidak None
            if metadata.get("earliest_date") is not None:
                return metadata.get("earliest_date"), metadata.get("earliest_code")

        # Fallback: Hitung manual jika metadata tidak ada/kosong
        earliest_date_obj = None
        earliest_code_val = None

        for item in content.get("content", []):
            # Cek tanggal di discussion
            if item.get("date"):
                try:
                    current_date = datetime.strptime(item["date"], "%Y-%m-%d")
                    if earliest_date_obj is None or current_date < earliest_date_obj:
                        earliest_date_obj = current_date
                        earliest_code_val = item.get("repetition_code")
                except (ValueError, TypeError):
                    continue

            # Cek tanggal di points
            for point in item.get("points", []):
                if point.get("date"):
                    try:
                        current_date = datetime.strptime(point["date"], "%Y-%m-%d")
                        if earliest_date_obj is None or current_date < earliest_date_obj:
                            earliest_date_obj = current_date
                            earliest_code_val = point.get("repetition_code")
                    except (ValueError, TypeError):
                        continue
        
        if earliest_date_obj:
            return earliest_date_obj.strftime("%Y-%m-%d"), earliest_code_val
        return None, None

    def get_subjects(self, topic_path):
        """Mendapatkan daftar semua subject (file .json) dalam sebuah topic beserta tanggal paling awal dan ikon."""
        if not topic_path:
            return []
        
        subjects_with_dates = []
        # Ambil semua file .json KECUALI 'topic_config.json'
        files = sorted([f for f in os.listdir(topic_path) if f.endswith('.json') and f != 'topic_config.json']) # <-- PERUBAHAN DI SINI
        for f in files:
            file_path = os.path.join(topic_path, f)
            content = self.load_content(file_path)
            metadata = content.get("metadata", {})
            icon = metadata.get("icon", config.DEFAULT_SUBJECT_ICON)
            date, code = self._get_earliest_date_and_code(file_path)
            subjects_with_dates.append((os.path.splitext(f)[0], date, code, icon))
        return subjects_with_dates

    def load_content(self, file_path):
        """Memuat konten dari file JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"content": [], "metadata": {"icon": config.DEFAULT_SUBJECT_ICON}}

    def save_content(self, file_path, content):
        """Menyimpan konten ke file JSON."""
        if file_path and content is not None:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

    def create_directory(self, path):
        """Membuat direktori baru."""
        os.makedirs(path)
        # Inisialisasi file konfigurasi untuk topic baru
        topic_name = os.path.basename(path)
        self.save_topic_config(topic_name, {'icon': config.DEFAULT_TOPIC_ICON})

    def rename_path(self, old_path, new_path):
        """Mengubah nama file atau direktori."""
        os.rename(old_path, new_path)

    def delete_directory(self, path):
        """Menghapus direktori dan semua isinya."""
        shutil.rmtree(path)

    def delete_file(self, path):
        """Menghapus file."""
        os.remove(path)