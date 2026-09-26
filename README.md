# Klasifikasi Primata Endemik Indonesia — Web App (Django)

Skeleton project Django untuk sistem klasifikasi citra primata endemik
Indonesia (EfficientNet-B0). Dibuat sebagai bagian dari Sprint 3.

## Menjalankan project

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Buka http://127.0.0.1:8000/

## Struktur penting

- `classifier/` — app utama (view, url, template halaman upload)
- `classifier/templates/classifier/` — template HTML (base.html, index.html)
- `classifier/static/classifier/style.css` — styling
- `classifier/ml_model/` — **taruh file model .h5 hasil training Colab di sini** (Sprint 4)
- `media/` — tempat gambar yang diupload user disimpan otomatis

## Data spesies & sumber referensi

Informasi biologis spesies (status konservasi, ciri fisik, distribusi,
habitat) **tidak** ditulis bebas di kode. Semuanya disimpan di dua tabel:

- **`Spesies`** — identitas taksonomi dasar (kode, nama umum, nama ilmiah,
  famili).
- **`FaktaSpesies`** — satu baris = satu klaim (`kategori`), WAJIB disertai
  metadata sumber: `source_type`, `source_title`, `source_author`,
  `source_year`, `source_doi`, `source_url`, `source_date` (tanggal akses).

Prioritas sumber per kategori:
- `status_konservasi` → **IUCN Red List of Threatened Species** (otoritas resmi status konservasi & sinonim taksonomi).
- `taksonomi` / `distribusi` → **Mammal Diversity Database (MDD)** dan/atau IUCN Red List.
- `ciri_fisik` → paper ilmiah / monograf / taxonomic revision, dengan DOI bila tersedia.

Data awal (Bekantan, Orangutan Kalimantan, Orangutan Sumatra) diisi lewat
data migration `classifier/migrations/0004_seed_data_spesies.py`, tiap
baris bisa ditelusuri ulang lewat `source_url`/`source_doi` yang tercantum
(IUCN Red List assessment, Mammal Diversity Database, dan paper seperti
Bennett & Sebastian 1988, Courtenay et al. 1988, Nater et al. 2017). Bisa
juga dikelola langsung lewat Django admin (`/admin/`, model *Spesies* dan
*Fakta Spesies*).

Model ini dibuat dengan Django ORM sehingga otomatis kompatibel dengan
MySQL — tinggal ganti `DATABASES` di `settings.py`, contoh:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'primata_db',
        'USER': 'root',
        'PASSWORD': '...',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

lalu `pip install mysqlclient` dan `python manage.py migrate`. Skema tabel
`FaktaSpesies` yang dihasilkan Django kurang lebih setara dengan DDL MySQL
berikut (untuk referensi/dokumentasi):

```sql
CREATE TABLE classifier_spesies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode VARCHAR(50) NOT NULL UNIQUE,
    nama_umum VARCHAR(100) NOT NULL,
    nama_ilmiah VARCHAR(100) NOT NULL,
    otoritas_taksonomi VARCHAR(100),
    famili VARCHAR(100)
);

CREATE TABLE classifier_faktaspesies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spesies_id INT NOT NULL,
    kategori VARCHAR(30) NOT NULL,       -- taksonomi | status_konservasi | ciri_fisik | distribusi | habitat
    isi TEXT NOT NULL,
    source_type VARCHAR(30) NOT NULL,    -- iucn_red_list | mdd | jurnal_ilmiah | buku_monograf | institusi_resmi
    source_title VARCHAR(300) NOT NULL,
    source_author VARCHAR(300),
    source_year INT,
    source_doi VARCHAR(150),
    source_url VARCHAR(500) NOT NULL,
    source_date DATE NOT NULL,           -- tanggal data diakses/diverifikasi
    catatan TEXT,
    FOREIGN KEY (spesies_id) REFERENCES classifier_spesies(id) ON DELETE CASCADE,
    UNIQUE (spesies_id, kategori)
);
```

## Status

- [x] Backend klasifikasi EfficientNet-B0 dan penyimpanan riwayat
- [x] Redesign UI/UX dasar: design system, navbar responsif, beranda, upload, validasi, dan loading state
- [x] Halaman hasil: confidence breakdown, hasil dengan keyakinan rendah, serta informasi spesies
- [x] Riwayat: gallery responsif, pencarian, filter spesies, sorting, dan statistik dari database
- [x] Halaman About, footer, reduced-motion, dan empty/error state dasar
- [ ] Evaluasi dan implementasi Grad-CAM (memerlukan validasi runtime model terlebih dahulu)
- [ ] Deployment
