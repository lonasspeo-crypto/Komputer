"""
Import metadata & foto dari observasi_sample/metadata.json (hasil
fetch_sample_observasi.py) ke tabel FotoObservasi di database.

PENTING: taruh script ini di folder ROOT project Django kamu
(folder yang ada manage.py-nya), sejajar dengan folder observasi_sample/
yang dihasilkan fetch_sample_observasi.py.

Cara pakai:
    python import_foto_observasi.py
"""

import os
import sys
import json
from datetime import datetime

import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primata_project.settings')
django.setup()

from django.core.files import File
from classifier.models import Spesies, FotoObservasi

METADATA_PATH = os.path.join('observasi_sample', 'metadata.json')


def main():
    if not os.path.exists(METADATA_PATH):
        print(f"File {METADATA_PATH} tidak ditemukan. Jalanin fetch_sample_observasi.py dulu.")
        return

    with open(METADATA_PATH, encoding='utf-8') as f:
        data = json.load(f)

    dibuat = 0
    dilewati = 0

    for item in data:
        spesies = Spesies.objects.filter(kode=item['spesies_kode']).first()
        if not spesies:
            print(f"[LEWATI] Spesies '{item['spesies_kode']}' tidak ditemukan di database.")
            dilewati += 1
            continue

        path_gambar = os.path.join('observasi_sample', item['file_gambar'])
        if not os.path.exists(path_gambar):
            print(f"[LEWATI] File gambar tidak ditemukan: {path_gambar}")
            dilewati += 1
            continue

        tanggal = None
        if item.get('tanggal_diambil'):
            try:
                tanggal = datetime.strptime(item['tanggal_diambil'], '%Y-%m-%d').date()
            except ValueError:
                tanggal = None

        with open(path_gambar, 'rb') as f:
            FotoObservasi.objects.create(
                spesies=spesies,
                gambar=File(f, name=os.path.basename(path_gambar)),
                lokasi=item.get('lokasi', ''),
                tanggal_diambil=tanggal,
                fotografer=item.get('fotografer', ''),
                sumber_platform=item.get('sumber_platform', 'iNaturalist'),
                sumber_url=item.get('sumber_url', ''),
                lisensi=item.get('lisensi', ''),
            )
        dibuat += 1
        print(f"[OK] {item['spesies_kode']} - {item.get('lokasi') or 'lokasi tidak diketahui'}")

    print(f"\nSelesai. {dibuat} foto observasi dibuat, {dilewati} dilewati.")
    if dibuat:
        print("Cek hasilnya di /admin/ (menu Foto Observasi) atau langsung di halaman hasil klasifikasi.")


if __name__ == '__main__':
    main()
