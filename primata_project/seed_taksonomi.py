"""
Isi FaktaSpesies kategori='taksonomi' buat 3 spesies, sumber Mammal
Diversity Database (MDD) -- situs yang sama dengan referensi yang kamu
kasih (mammaldiversity.org). Data taksonomi di bawah ini SAMA PERSIS
sama yang tertera di halaman MDD masing-masing spesies per 21 Sep 2026.

PENTING: taruh script ini di folder ROOT project Django kamu
(folder yang ada manage.py-nya).

Cara pakai:
    python seed_taksonomi.py
"""

import os
import sys
import datetime

import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primata_project.settings')
django.setup()

from classifier.models import Spesies, FaktaSpesies

TANGGAL_AKSES = datetime.date(2026, 9, 21)

DATA_TAKSONOMI = {
    "bekantan": {
        "isi": (
            "Subkelas Theria; Infrakelas Placentalia; Magnordo Boreoeutheria; "
            "Superordo Euarchontoglires; Ordo Primates; Subordo Haplorhini; "
            "Infraordo Simiiformes; Parvordo Catarrhini; Superfamili Cercopithecoidea; "
            "Famili Cercopithecidae; Subfamili Colobinae; Tribus Presbytini; Genus Nasalis."
        ),
        "source_title": "Nasalis larvatus (Van Wurmb, 1787). Mammal Diversity Database, taxon 1000659",
        "source_url": "https://www.mammaldiversity.org/taxon/1000659",
    },
    "orangutan_kalimantan": {
        "isi": (
            "Subkelas Theria; Infrakelas Placentalia; Magnordo Boreoeutheria; "
            "Superordo Euarchontoglires; Ordo Primates; Subordo Haplorhini; "
            "Infraordo Simiiformes; Parvordo Catarrhini; Superfamili Hominoidea; "
            "Famili Hominidae; Subfamili Ponginae; Tribus Pongini; Genus Pongo."
        ),
        "source_title": "Pongo pygmaeus (Linnaeus, 1760). Mammal Diversity Database, taxon 1000722",
        "source_url": "https://www.mammaldiversity.org/taxon/1000722",
    },
    "orangutan_sumatra": {
        "isi": (
            "Subkelas Theria; Infrakelas Placentalia; Magnordo Boreoeutheria; "
            "Superordo Euarchontoglires; Ordo Primates; Subordo Haplorhini; "
            "Infraordo Simiiformes; Parvordo Catarrhini; Superfamili Hominoidea; "
            "Famili Hominidae; Subfamili Ponginae; Tribus Pongini; Genus Pongo."
        ),
        "source_title": "Pongo abelii (Lesson, 1827). Mammal Diversity Database, taxon 1000721",
        "source_url": "https://www.mammaldiversity.org/taxon/1000721",
    },
}


def main():
    for kode, data in DATA_TAKSONOMI.items():
        spesies = Spesies.objects.filter(kode=kode).first()
        if not spesies:
            print(f"[LEWATI] Spesies '{kode}' tidak ditemukan di database.")
            continue

        obj, dibuat = FaktaSpesies.objects.update_or_create(
            spesies=spesies,
            kategori='taksonomi',
            defaults={
                'isi': data['isi'],
                'source_type': 'mdd',
                'source_title': data['source_title'],
                'source_author': 'Mammal Diversity Database (ASM)',
                'source_year': 2024,
                'source_doi': '',
                'source_url': data['source_url'],
                'source_date': TANGGAL_AKSES,
                'catatan': '',
            },
        )
        status = 'dibuat' if dibuat else 'diperbarui'
        print(f"[OK] Taksonomi {spesies.nama_umum} {status}.")

    print("\nSelesai. Cek halaman hasil klasifikasi -- taksonomi harusnya")
    print("sekarang muncul di bawah gambar yang diunggah.")


if __name__ == '__main__':
    main()
