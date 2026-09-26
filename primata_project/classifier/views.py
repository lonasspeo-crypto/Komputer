from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from PIL import Image, UnidentifiedImageError

from . import ml_utils
from .models import FaktaSpesies, RiwayatKlasifikasi, Spesies

# Di bawah ambang ini, hasil dianggap tidak cukup yakin untuk ditampilkan
# sebagai identifikasi pasti (kemungkinan bukan salah satu dari 3 kelas target).
CONFIDENCE_THRESHOLD = 0.5
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png'}
MIN_IMAGE_DIMENSION = 224

# Nama tampilan & nama ilmiah TIDAK lagi ditulis manual di sini: keduanya
# diambil langsung dari tabel Spesies (lihat get_display_names_map() dan
# get_species_info()) supaya satu-satunya "sumber kebenaran" untuk data
# spesies ada di database, bukan tersebar di kode.


def get_display_names_map():
    """
    Bangun ulang mapping {kode: (nama_umum, nama_ilmiah)} dari tabel Spesies,
    dengan bentuk yang sama seperti DISPLAY_NAMES versi lama supaya kode lain
    yang memakainya tidak perlu berubah.
    """
    return {
        s.kode: (s.nama_umum, s.nama_ilmiah)
        for s in Spesies.objects.all()
    }


def get_species_info(kode):
    """
    Ambil semua FaktaSpesies milik satu spesies (berdasar kode label model),
    dikelompokkan per kategori, masing-masing lengkap dengan metadata sumber
    supaya bisa ditampilkan & diverifikasi di halaman hasil.

    Return None kalau spesies dengan kode tersebut belum ada di database.
    """
    spesies = Spesies.objects.filter(kode=kode).prefetch_related('fakta', 'foto_observasi').first()
    if not spesies:
        return None

    info = {
        'nama_umum': spesies.nama_umum,
        'nama_ilmiah': spesies.nama_ilmiah,
        'otoritas_taksonomi': spesies.otoritas_taksonomi,
        'famili': spesies.famili,
        'fakta': {},
        'foto_observasi': list(spesies.foto_observasi.all()[:4]),
    }
    for f in spesies.fakta.all():
        info['fakta'][f.kategori] = {
            'isi': f.isi,
            'source_type': f.get_source_type_display(),
            'source_title': f.source_title,
            'source_author': f.source_author,
            'source_year': f.source_year,
            'source_doi': f.source_doi,
            'source_url': f.source_url,
            'source_date': f.source_date,
        }
    return info


# Ringkasan singkat (netral, tanpa klaim ilmiah spesifik) untuk kartu spesies
# di beranda. Klaim ilmiah yang bisa diperdebatkan tetap WAJIB lewat
# FaktaSpesies + sumbernya, bukan dari teks statis ini.
SPESIES_DESKRIPSI_SINGKAT = {
    'bekantan': 'Primata khas Kalimantan yang hidup di hutan bakau dan kawasan sungai.',
    'orangutan_kalimantan': 'Orangutan yang hidup di hutan hujan Kalimantan.',
    'orangutan_sumatra': 'Orangutan yang terutama ditemukan di utara Sumatra.',
}


def _static_there(path):
    """Cek apakah file static dengan path relatif tertentu benar-benar ada."""
    import os
    from django.conf import settings
    for root in settings.STATICFILES_DIRS:
        if os.path.exists(os.path.join(str(root), path)):
            return True
    return False


def get_species_cards():
    """
    Bangun daftar dict spesies untuk kartu di beranda: identitas dari database,
    plus thumbnail/hero opsional bila file gambarnya tersedia di folder static.
    """
    cards = []
    for s in Spesies.objects.all():
        thumb_rel = f'classifier/images/species/{s.kode}-thumb.jpg'
        hero_rel = f'classifier/images/species/{s.kode}-hero.jpg'
        cards.append({
            'kode': s.kode,
            'nama_umum': s.nama_umum,
            'nama_ilmiah': s.nama_ilmiah,
            'deskripsi': SPESIES_DESKRIPSI_SINGKAT.get(s.kode, ''),
            'thumb_static': static(thumb_rel) if _static_there(thumb_rel) else None,
            'hero_static': static(hero_rel) if _static_there(hero_rel) else None,
            'detail_url': reverse('classifier:spesies_detail', kwargs={'kode': s.kode}),
        })
    return cards


def validate_uploaded_image(image_file):
    """Validate file metadata and image readability before prediction."""
    if image_file.content_type not in ALLOWED_IMAGE_TYPES:
        return 'Format gambar tidak didukung. Gunakan JPG atau PNG.'
    if image_file.size > MAX_IMAGE_SIZE_BYTES:
        return 'Ukuran gambar terlalu besar. Ukuran maksimum adalah 10 MB.'

    try:
        with Image.open(image_file) as uploaded_image:
            uploaded_image.verify()

        image_file.seek(0)
        with Image.open(image_file) as uploaded_image:
            width, height = uploaded_image.size
            uploaded_image.load()
    except (UnidentifiedImageError, OSError):
        return 'Gambar tidak dapat dibaca. Pilih file JPG atau PNG yang valid.'
    finally:
        image_file.seek(0)

    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        return (
            'Resolusi gambar rendah. Gunakan gambar minimal '
            f'{MIN_IMAGE_DIMENSION} x {MIN_IMAGE_DIMENSION} piksel.'
        )

    return None


def index(request):
    context = {
        'page_title': 'Klasifikasi Primata Endemik Indonesia',
        'daftar_spesies': get_species_cards(),
    }

    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if not image_file:
            context['error'] = 'Pilih gambar primata sebelum memulai identifikasi.'
            return render(request, 'classifier/index.html', context)

        validation_error = validate_uploaded_image(image_file)
        if validation_error:
            context['error'] = validation_error
            return render(request, 'classifier/index.html', context)

        try:
            display_names = get_display_names_map()
            results = ml_utils.predict_image(image_file)

            top_label, top_confidence = results[0]
            top_display, _ = display_names.get(top_label, (top_label, ''))
            top_confidence_pct = round(top_confidence * 100, 1)
            is_confident = top_confidence >= CONFIDENCE_THRESHOLD

            image_file.seek(0)
            riwayat = RiwayatKlasifikasi.objects.create(
                gambar=image_file,
                label_prediksi=top_label,
                nama_tampilan=top_display,
                keyakinan=top_confidence_pct,
                is_confident=is_confident,
                semua_hasil=[
                    {
                        'display_name': display_names.get(label, (label, ''))[0],
                        'confidence': round(confidence * 100, 1),
                    }
                    for label, confidence in results
                ],
            )
            return redirect('classifier:hasil', pk=riwayat.pk)
        except FileNotFoundError:
            context['error'] = (
                'Model klasifikasi belum tersedia. Silakan hubungi pengelola '
                'sistem untuk memeriksa konfigurasi model.'
            )
        except Exception:
            context['error'] = (
                'Gagal memproses gambar. Pastikan file yang diunggah adalah '
                'gambar JPG/PNG yang valid.'
            )

    # Sentuhan personal di hero beranda: tampilkan spesies dari prediksi
    # terakhir user bila ada dan file gambarnya tersedia.
    terakhir = RiwayatKlasifikasi.objects.order_by('-waktu').first()
    if terakhir:
        for card in context['daftar_spesies']:
            if card['kode'] == terakhir.label_prediksi and card['hero_static']:
                context['prediksi_spesies'] = card
                break

    return render(request, 'classifier/index.html', context)


def hasil(request, pk):
    riwayat = get_object_or_404(RiwayatKlasifikasi, pk=pk)
    display_names = get_display_names_map()
    _, top_sci = display_names.get(riwayat.label_prediksi, (riwayat.nama_tampilan, ''))
    species_info = get_species_info(riwayat.label_prediksi)

    context = {
        'page_title': f'Hasil Klasifikasi — {riwayat.nama_tampilan}',
        'uploaded_image_url': riwayat.gambar.url,
        'prediction': {
            'display_name': riwayat.nama_tampilan,
            'sci_name': top_sci,
            'confidence': riwayat.keyakinan,
            'info': species_info,
            'is_confident': riwayat.is_confident,
        },
        'all_results': riwayat.semua_hasil,
        'threshold_pct': round(CONFIDENCE_THRESHOLD * 100),
        'species_detail_url': reverse(
            'classifier:spesies_detail', kwargs={'kode': riwayat.label_prediksi}
        ),
    }
    return render(request, 'classifier/hasil.html', context)


def spesies_detail(request, kode):
    """Halaman profil lengkap satu spesies: identitas, fakta bersumber, galeri."""
    spesies = get_object_or_404(
        Spesies.objects.prefetch_related('fakta', 'foto_observasi'), kode=kode
    )
    hero_rel = f'classifier/images/species/{spesies.kode}-hero.jpg'
    thumb_rel = f'classifier/images/species/{spesies.kode}-thumb.jpg'
    hero_static = static(hero_rel) if _static_there(hero_rel) else None
    if hero_static is None and _static_there(thumb_rel):
        hero_static = static(thumb_rel)

    kategori_label = dict(FaktaSpesies.KATEGORI_CHOICES)
    fakta_list = [
        {'kategori': f.kategori, 'label': kategori_label.get(f.kategori, f.kategori), 'fakta': f}
        for f in spesies.fakta.all().order_by('kategori')
    ]
    status_konservasi = next(
        (item['fakta'] for item in fakta_list if item['kategori'] == 'status_konservasi'),
        None,
    )
    foto_observasi = list(spesies.foto_observasi.all())

    context = {
        'page_title': f'{spesies.nama_umum} ({spesies.nama_ilmiah}) — Profil Spesies',
        'spesies': {
            'kode': spesies.kode,
            'nama_umum': spesies.nama_umum,
            'nama_ilmiah': spesies.nama_ilmiah,
            'otoritas_taksonomi': spesies.otoritas_taksonomi,
            'famili': spesies.famili,
            'hero_static': hero_static,
        },
        'fakta_list': fakta_list,
        'status_konservasi': status_konservasi,
        'foto_observasi': foto_observasi,
        'foto_utama': foto_observasi[0] if foto_observasi else None,
    }
    return render(request, 'classifier/spesies_detail.html', context)


def about(request):
    context = {
        'page_title': 'Tentang Sistem — Klasifikasi Primata Endemik Indonesia',
    }
    return render(request, 'classifier/about.html', context)


def riwayat(request):
    display_names = get_display_names_map()
    query = request.GET.get('q', '').strip()
    selected_species = request.GET.get('spesies', '')
    selected_sort = request.GET.get('urutkan', 'terbaru')
    base_history = RiwayatKlasifikasi.objects.filter(
        is_confident=True,
        keyakinan__gte=CONFIDENCE_THRESHOLD * 100,
    )
    daftar_riwayat = base_history

    if query:
        daftar_riwayat = daftar_riwayat.filter(nama_tampilan__icontains=query)
    if selected_species in display_names:
        daftar_riwayat = daftar_riwayat.filter(label_prediksi=selected_species)

    sort_options = {
        'terbaru': '-waktu',
        'terlama': 'waktu',
        'keyakinan_tertinggi': '-keyakinan',
        'keyakinan_terendah': 'keyakinan',
    }
    if selected_sort not in sort_options:
        selected_sort = 'terbaru'
    daftar_riwayat = daftar_riwayat.order_by(sort_options[selected_sort])

    context = {
        'page_title': 'Riwayat Klasifikasi',
        'daftar_riwayat': daftar_riwayat[:50],
        'query': query,
        'selected_species': selected_species,
        'selected_sort': selected_sort,
        'threshold_pct': round(CONFIDENCE_THRESHOLD * 100),
        'species_choices': [
            (label, display_name) for label, (display_name, _) in display_names.items()
        ],
    }
    return render(request, 'classifier/riwayat.html', context)
