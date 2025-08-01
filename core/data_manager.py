# file: test/core/data_manager.py

import os
import json
import shutil
import tempfile
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
        shutil.make_archive(
            base_name=os.path.splitext(zip_path)[0],
            format='zip',
            root_dir=os.path.dirname(self.base_path),
            base_dir=os.path.basename(self.base_path)
        )

    def import_backup_zip(self, zip_path):
        """Mengekstrak dan mengimpor topics dari file zip."""
        # Buat direktori temporary untuk mengekstrak file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Ekstrak arsip
            shutil.unpack_archive(zip_path, temp_dir, 'zip')

            # Path ke folder 'topics' di dalam temp_dir
            extracted_topics_path = os.path.join(temp_dir, 'topics')

            # Pastikan folder 'topics' ada setelah ekstraksi
            if not os.path.exists(extracted_topics_path):
                # Jika tidak ada folder 'topics', asumsikan konten ada di root temp_dir
                extracted_topics_path = temp_dir
            
            # Iterasi melalui setiap item di direktori hasil ekstraksi
            for topic_name in os.listdir(extracted_topics_path):
                source_topic_path = os.path.join(extracted_topics_path, topic_name)

                # Pastikan itu adalah direktori
                if not os.path.isdir(source_topic_path):
                    continue

                destination_topic_name = topic_name
                destination_topic_path = os.path.join(self.base_path, destination_topic_name)

                # Cek jika topic dengan nama yang sama sudah ada, tambahkan prefix 'new'
                while os.path.exists(destination_topic_path):
                    destination_topic_name = f"new {destination_topic_name}"
                    destination_topic_path = os.path.join(self.base_path, destination_topic_name)

                # Pindahkan folder topic dari temp_dir ke direktori utama
                shutil.move(source_topic_path, destination_topic_path)

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
                        pass
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

        if metadata and "earliest_date" in metadata:
            if metadata.get("earliest_date") is not None:
                return metadata.get("earliest_date"), metadata.get("earliest_code")

        earliest_date_obj = None
        earliest_code_val = None

        for item in content.get("content", []):
            if item.get("date"):
                try:
                    current_date = datetime.strptime(item["date"], "%Y-%m-%d")
                    if earliest_date_obj is None or current_date < earliest_date_obj:
                        earliest_date_obj = current_date
                        earliest_code_val = item.get("repetition_code")
                except (ValueError, TypeError):
                    continue

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
        files = sorted([f for f in os.listdir(topic_path) if f.endswith('.json') and f != 'topic_config.json'])
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