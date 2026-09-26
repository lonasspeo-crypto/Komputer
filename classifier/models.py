from django.db import models


class Spesies(models.Model):
    """
    Data induk spesies primata. Field deskriptif di sini sengaja dibuat
    minim (hanya identitas taksonomi dasar) -- semua klaim ilmiah yang
    bisa diperdebatkan (status konservasi, ciri fisik, distribusi, dll)
    disimpan di model FaktaSpesies supaya setiap klaim WAJIB punya sumber.
    """
    kode = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Harus sama dengan label di classifier.ml_utils.CLASS_NAMES, misal 'bekantan'.",
    )
    nama_umum = models.CharField(max_length=100, help_text="Nama umum Bahasa Indonesia, misal 'Bekantan'.")
    nama_ilmiah = models.CharField(max_length=100, help_text="Nama binomial, misal 'Nasalis larvatus'.")
    otoritas_taksonomi = models.CharField(
        max_length=100,
        blank=True,
        help_text="Penulis & tahun pertama kali dideskripsikan, misal '(Wurmb, 1787)'.",
    )
    famili = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Spesies'
        verbose_name_plural = 'Spesies'
        ordering = ['nama_umum']

    def __str__(self):
        return f"{self.nama_umum} ({self.nama_ilmiah})"


class FaktaSpesies(models.Model):
    """
    Satu baris = satu klaim/informasi spesifik tentang sebuah spesies,
    WAJIB disertai metadata sumber (source_url, source_title, source_date,
    source_type) supaya bisa diverifikasi dan tidak "asal dibuat sendiri".

    Konvensi pengisian:
    - status_konservasi -> WAJIB bersumber dari IUCN Red List of Threatened
      Species (source_type='iucn_red_list'), karena IUCN adalah otoritas
      resmi untuk kategori status konservasi global.
    - taksonomi & distribusi -> prioritas Mammal Diversity Database (MDD)
      dan/atau IUCN Red List (source_type='mdd' / 'iucn_red_list').
    - ciri_fisik -> prioritas paper ilmiah / monograf / taxonomic revision
      (source_type='jurnal_ilmiah' atau 'buku_monograf'), simpan DOI bila ada.
    - habitat -> boleh mengikuti bagian "Habitat and Ecology" pada asesmen
      IUCN yang sama dengan status_konservasi.
    """

    KATEGORI_CHOICES = [
        ('taksonomi', 'Taksonomi'),
        ('status_konservasi', 'Status Konservasi'),
        ('ciri_fisik', 'Ciri Fisik / Identifikasi'),
        ('distribusi', 'Distribusi Geografis'),
        ('habitat', 'Habitat'),
    ]

    SOURCE_TYPE_CHOICES = [
        ('iucn_red_list', 'IUCN Red List of Threatened Species'),
        ('mdd', 'Mammal Diversity Database (MDD)'),
        ('jurnal_ilmiah', 'Jurnal ilmiah (peer-reviewed)'),
        ('buku_monograf', 'Buku / Monograf / Taxonomic Revision'),
        ('institusi_resmi', 'Institusi resmi (BKSDA, LIPI/BRIN, IUCN SSC, dst.)'),
    ]

    spesies = models.ForeignKey(Spesies, on_delete=models.CASCADE, related_name='fakta')
    kategori = models.CharField(max_length=30, choices=KATEGORI_CHOICES)
    isi = models.TextField(help_text="Isi informasi, ditulis ringkas dan sesuai sumber (hindari menambah klaim yang tidak ada di sumber).")

    # --- Metadata sumber: WAJIB diisi untuk setiap baris fakta ---
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPE_CHOICES)
    source_title = models.CharField(
        max_length=300,
        help_text="Judul rujukan persis, misal 'Nasalis larvatus. The IUCN Red List of Threatened Species 2020: e.T14352A17945165'.",
    )
    source_author = models.CharField(max_length=300, blank=True, help_text="Penulis/tim asesmen, misal 'Boonratana, R. et al.'")
    source_year = models.PositiveIntegerField(null=True, blank=True, help_text="Tahun publikasi/asesmen sumber.")
    source_doi = models.CharField(max_length=150, blank=True, help_text="DOI jika tersedia, misal '10.2305/IUCN.UK.2020-2.RLTS.T14352A17945165.en'.")
    source_url = models.URLField(max_length=500, help_text="Tautan langsung ke sumber (halaman spesies IUCN/MDD, atau DOI paper).")
    source_date = models.DateField(help_text="Tanggal data ini diakses/diverifikasi dari sumber (tanggal akses).")

    catatan = models.TextField(blank=True, help_text="Catatan tambahan, misal jika ada perbedaan pendapat antar sumber.")

    class Meta:
        verbose_name = 'Fakta Spesies'
        verbose_name_plural = 'Fakta Spesies'
        ordering = ['spesies', 'kategori']
        constraints = [
            models.UniqueConstraint(fields=['spesies', 'kategori'], name='unique_kategori_per_spesies'),
        ]

    def __str__(self):
        return f"{self.spesies.nama_umum} - {self.get_kategori_display()}"


class FotoObservasi(models.Model):
    """
    Foto referensi/pembanding hasil observasi lapangan untuk satu spesies,
    ditampilkan di halaman hasil klasifikasi sebagai pembanding visual.
    Detail pengambilan foto (lokasi, tanggal, fotografer, sumber) WAJIB
    diisi sejauh diketahui -- jangan diisi dengan data karangan.
    """
    spesies = models.ForeignKey(Spesies, on_delete=models.CASCADE, related_name='foto_observasi')
    gambar = models.ImageField(upload_to='observasi/')
    lokasi = models.CharField(
        max_length=200, blank=True,
        help_text="Lokasi observasi, misal 'Taman Nasional Tanjung Puting, Kalimantan Tengah'.",
    )
    tanggal_diambil = models.DateField(
        null=True, blank=True,
        help_text="Tanggal foto diambil / observasi dilakukan (bukan tanggal diunggah ke sistem ini).",
    )
    fotografer = models.CharField(max_length=150, blank=True, help_text="Nama observer/fotografer, jika diketahui.")
    sumber_platform = models.CharField(
        max_length=100, blank=True, default='iNaturalist',
        help_text="Platform sumber observasi, misal 'iNaturalist'.",
    )
    sumber_url = models.URLField(max_length=500, blank=True, help_text="Tautan ke observasi asli.")
    lisensi = models.CharField(max_length=100, blank=True, help_text="Lisensi foto, misal 'CC-BY-NC 4.0'.")
    catatan = models.TextField(blank=True)
    urutan = models.PositiveIntegerField(default=0, help_text="Urutan tampil, angka kecil di depan.")

    class Meta:
        verbose_name = 'Foto Observasi'
        verbose_name_plural = 'Foto Observasi'
        ordering = ['spesies', 'urutan', 'id']

    def __str__(self):
        return f"{self.spesies.nama_umum} — {self.lokasi or 'lokasi tidak diketahui'}"


class RiwayatKlasifikasi(models.Model):
    gambar = models.ImageField(upload_to='riwayat/')
    label_prediksi = models.CharField(max_length=50)
    nama_tampilan = models.CharField(max_length=100)
    keyakinan = models.FloatField(help_text="Persentase keyakinan, misal 81.9")
    is_confident = models.BooleanField(
        default=True,
        help_text="False kalau keyakinan di bawah ambang batas (tidak ditampilkan di Riwayat publik)",
    )
    semua_hasil = models.JSONField(
        default=list,
        help_text="Breakdown confidence untuk semua kelas, dipakai buat render ulang chart",
    )
    waktu = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-waktu']
        verbose_name = 'Riwayat Klasifikasi'
        verbose_name_plural = 'Riwayat Klasifikasi'

    def __str__(self):
        return f"{self.nama_tampilan} ({self.keyakinan:.1f}%) - {self.waktu:%d %b %Y %H:%M}"
