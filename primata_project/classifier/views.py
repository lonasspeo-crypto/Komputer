from django.shortcuts import render, redirect, get_object_or_404
from PIL import Image, UnidentifiedImageError

from . import ml_utils
from .models import RiwayatKlasifikasi, Spesies

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
    context = {'page_title': 'Klasifikasi Primata Endemik Indonesia'}

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
    }
    return render(request, 'classifier/hasil.html', context)


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
