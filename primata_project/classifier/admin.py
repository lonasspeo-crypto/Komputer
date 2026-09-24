from django.contrib import admin
from .models import RiwayatKlasifikasi, Spesies, FaktaSpesies, FotoObservasi


@admin.register(RiwayatKlasifikasi)
class RiwayatKlasifikasiAdmin(admin.ModelAdmin):
    list_display = ('nama_tampilan', 'keyakinan', 'waktu')
    list_filter = ('label_prediksi',)
    ordering = ('-waktu',)


class FaktaSpesiesInline(admin.TabularInline):
    model = FaktaSpesies
    extra = 0
    fields = ('kategori', 'isi', 'source_type', 'source_title', 'source_author', 'source_year', 'source_doi', 'source_url', 'source_date')


class FotoObservasiInline(admin.TabularInline):
    model = FotoObservasi
    extra = 0
    fields = ('gambar', 'lokasi', 'tanggal_diambil', 'fotografer', 'sumber_platform', 'sumber_url', 'lisensi', 'urutan')


@admin.register(Spesies)
class SpesiesAdmin(admin.ModelAdmin):
    list_display = ('nama_umum', 'nama_ilmiah', 'kode', 'famili')
    search_fields = ('nama_umum', 'nama_ilmiah', 'kode')
    inlines = [FaktaSpesiesInline, FotoObservasiInline]


@admin.register(FaktaSpesies)
class FaktaSpesiesAdmin(admin.ModelAdmin):
    # Admin terpisah supaya tim yang bertugas verifikasi sumber bisa
    # menyaring & mengaudit semua klaim per source_type/kategori tanpa
    # harus membuka satu-satu halaman spesies.
    list_display = ('spesies', 'kategori', 'source_type', 'source_title', 'source_year', 'source_date')
    list_filter = ('kategori', 'source_type')
    search_fields = ('isi', 'source_title', 'source_author', 'source_doi')
    autocomplete_fields = ('spesies',)


@admin.register(FotoObservasi)
class FotoObservasiAdmin(admin.ModelAdmin):
    list_display = ('spesies', 'lokasi', 'tanggal_diambil', 'fotografer', 'sumber_platform')
    list_filter = ('spesies', 'sumber_platform')
    search_fields = ('lokasi', 'fotografer', 'catatan')
    autocomplete_fields = ('spesies',)
