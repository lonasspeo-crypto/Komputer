import os
from django.apps import AppConfig


class ClassifierConfig(AppConfig):
    name = 'classifier'

    def ready(self):
        # Django dev server (runserver) jalanin 2 proses gara-gara auto-reloader.
        # RUN_MAIN cuma 'true' di proses anak yang beneran nge-handle request,
        # jadi model cuma di-load sekali (ga dobel di proses reloader).
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from . import ml_utils
        try:
            print("Memuat model EfficientNet-B0, mohon tunggu...")
            ml_utils.get_model()
            print("Model siap. Server siap menerima klasifikasi.")
        except FileNotFoundError as e:
            print(f"[WARNING] {e}")
