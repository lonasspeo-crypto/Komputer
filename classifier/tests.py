from io import BytesIO
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from .models import RiwayatKlasifikasi, Spesies, FaktaSpesies


class RiwayatViewTests(TestCase):
    def create_history(self, *, name, label, confidence, is_confident=True):
        return RiwayatKlasifikasi.objects.create(
            gambar='riwayat/test.jpg',
            nama_tampilan=name,
            label_prediksi=label,
            keyakinan=confidence,
            is_confident=is_confident,
            semua_hasil=[],
        )

    def test_history_hides_predictions_below_confidence_threshold(self):
        self.create_history(
            name='Bekantan kuat', label='bekantan', confidence=88.0
        )
        self.create_history(
            name='Bekantan lemah', label='bekantan', confidence=46.9
        )

        response = self.client.get(reverse('classifier:riwayat'))

        self.assertContains(response, 'Bekantan kuat')
        self.assertNotContains(response, 'Bekantan lemah')
        self.assertContains(response, 'role="meter"')
        self.assertContains(response, 'loading="lazy"')

    def test_history_filters_by_species(self):
        self.create_history(
            name='Bekantan', label='bekantan', confidence=88.0
        )
        target = self.create_history(
            name='Orangutan Sumatra', label='orangutan_sumatra', confidence=91.0
        )

        response = self.client.get(
            reverse('classifier:riwayat'), {'spesies': 'orangutan_sumatra'}
        )

        self.assertContains(response, 'Orangutan Sumatra')
        self.assertEqual(list(response.context['daftar_riwayat']), [target])

    def test_history_sorts_by_confidence(self):
        self.create_history(name='Bekantan', label='bekantan', confidence=72.0)
        self.create_history(
            name='Orangutan Kalimantan', label='orangutan_kalimantan', confidence=91.0
        )
        self.create_history(
            name='Prediksi lemah', label='orangutan_sumatra', confidence=44.0,
            is_confident=False,
        )

        response = self.client.get(
            reverse('classifier:riwayat'), {'urutkan': 'keyakinan_tertinggi'}
        )

        self.assertEqual(
            [item.keyakinan for item in response.context['daftar_riwayat']],
            [91.0, 72.0],
        )
        self.assertContains(response, 'Keyakinan tertinggi')

    def test_result_uses_an_accessible_chart_fallback_without_cdn(self):
        history = self.create_history(
            name='Bekantan', label='bekantan', confidence=88.0
        )
        history.semua_hasil = [
            {'display_name': 'Bekantan', 'confidence': 88.0},
            {'display_name': 'Orangutan Kalimantan', 'confidence': 10.0},
            {'display_name': 'Orangutan Sumatra', 'confidence': 2.0},
        ]
        history.save()

        response = self.client.get(reverse('classifier:hasil', args=[history.pk]))

        self.assertContains(response, 'Perbandingan prediksi')
        self.assertContains(response, 'Melewati ambang 50%')
        self.assertNotContains(response, 'chart.js')

    def test_upload_rejects_an_unsupported_file_type(self):
        upload = SimpleUploadedFile(
            'bukan-gambar.txt', b'isi file', content_type='text/plain'
        )

        response = self.client.post(reverse('classifier:index'), {'image': upload})

        self.assertContains(response, 'Format gambar tidak didukung.')

    def test_upload_rejects_an_image_below_minimum_resolution(self):
        image_data = BytesIO()
        Image.new('RGB', (120, 120), color='white').save(image_data, format='JPEG')
        upload = SimpleUploadedFile(
            'kecil.jpg', image_data.getvalue(), content_type='image/jpeg'
        )

        response = self.client.post(reverse('classifier:index'), {'image': upload})

        self.assertContains(response, 'Resolusi gambar rendah.')

    @patch('classifier.views.ml_utils.predict_image')
    def test_valid_upload_preserves_the_existing_prediction_flow(self, predict_image):
        image_data = BytesIO()
        Image.new('RGB', (224, 224), color='white').save(image_data, format='JPEG')
        upload = SimpleUploadedFile(
            'primata.jpg', image_data.getvalue(), content_type='image/jpeg'
        )
        predict_image.return_value = [
            ('bekantan', 0.88),
            ('orangutan_kalimantan', 0.10),
            ('orangutan_sumatra', 0.02),
        ]

        response = self.client.post(reverse('classifier:index'), {'image': upload})

        self.assertRedirects(response, reverse('classifier:hasil', args=[1]))
        riwayat = RiwayatKlasifikasi.objects.get()
        self.assertEqual(riwayat.nama_tampilan, 'Bekantan')
        self.assertEqual(riwayat.keyakinan, 88.0)


class SpesiesInfoTests(TestCase):
    """
    Memastikan setiap kelas yang dikenali model (lihat ml_utils.CLASS_NAMES)
    punya data Spesies + FaktaSpesies bersumber di database, dan halaman
    hasil benar-benar menampilkan metadata sumber (bukan cuma isi klaimnya).
    """

    def create_history(self, *, label, name):
        return RiwayatKlasifikasi.objects.create(
            gambar='riwayat/test.jpg',
            nama_tampilan=name,
            label_prediksi=label,
            keyakinan=90.0,
            is_confident=True,
            semua_hasil=[],
        )

    def test_seed_data_covers_every_model_class(self):
        from . import ml_utils

        kode_di_db = set(Spesies.objects.values_list('kode', flat=True))
        self.assertEqual(kode_di_db, set(ml_utils.CLASS_NAMES))

    def test_every_species_has_all_five_sourced_categories(self):
        kategori_wajib = {
            'taksonomi', 'status_konservasi', 'ciri_fisik', 'distribusi', 'habitat',
        }
        for spesies in Spesies.objects.all():
            kategori_ada = set(spesies.fakta.values_list('kategori', flat=True))
            self.assertEqual(
                kategori_ada, kategori_wajib,
                f"{spesies.nama_umum} belum punya seluruh kategori fakta wajib",
            )

    def test_every_fact_has_required_source_metadata(self):
        for fakta in FaktaSpesies.objects.all():
            self.assertTrue(fakta.source_title, f"{fakta} tanpa source_title")
            self.assertTrue(fakta.source_url.startswith('http'), f"{fakta} tanpa source_url valid")
            self.assertTrue(fakta.source_type, f"{fakta} tanpa source_type")
            self.assertIsNotNone(fakta.source_date, f"{fakta} tanpa source_date")

    def test_status_konservasi_must_cite_iucn_red_list(self):
        # Sesuai kebijakan: status konservasi WAJIB dari IUCN Red List, bukan sumber lain.
        status_facts = FaktaSpesies.objects.filter(kategori='status_konservasi')
        self.assertEqual(status_facts.count(), 3)
        for fakta in status_facts:
            self.assertEqual(fakta.source_type, 'iucn_red_list')
            self.assertIn('iucnredlist.org', fakta.source_url)

    def test_hasil_page_shows_source_links_for_confident_prediction(self):
        history = self.create_history(label='bekantan', name='Bekantan')

        response = self.client.get(reverse('classifier:hasil', args=[history.pk]))

        self.assertContains(response, 'Status konservasi')
        self.assertContains(response, 'IUCN Red List')
        self.assertContains(response, 'Lihat sumber')
        self.assertContains(response, 'iucnredlist.org')

    def test_hasil_page_shows_missing_data_notice_for_unknown_species(self):
        history = self.create_history(label='spesies_belum_ada', name='Spesies Tidak Dikenal')

        response = self.client.get(reverse('classifier:hasil', args=[history.pk]))

        self.assertContains(response, 'belum tersedia di database')

    def test_homepage_renders_species_cards_from_database(self):
        response = self.client.get(reverse('classifier:index'))

        self.assertEqual(len(response.context['species_cards']), Spesies.objects.count())
        self.assertContains(response, 'classifier/images/bekantan-hero.jpg')
        self.assertContains(response, 'Denis Luyten / Wikimedia Commons')
        self.assertContains(
            response,
            reverse('classifier:spesies_detail', args=['bekantan']),
        )
        self.assertContains(response, 'Lihat profil')

    def test_species_profile_shows_sourced_facts(self):
        response = self.client.get(
            reverse('classifier:spesies_detail', args=['bekantan'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profil spesies')
        self.assertContains(response, 'Nasalis larvatus')
        self.assertContains(response, 'Informasi dan sumber')
        self.assertContains(response, '10.2305/IUCN.UK.2020-2.RLTS.T14352A17945165.en')

    def test_species_profile_returns_not_found_for_unknown_species(self):
        response = self.client.get(
            reverse('classifier:spesies_detail', args=['spesies-tidak-ada'])
        )

        self.assertEqual(response.status_code, 404)

    def test_confident_result_links_to_species_profile(self):
        history = self.create_history(label='bekantan', name='Bekantan')

        response = self.client.get(reverse('classifier:hasil', args=[history.pk]))

        self.assertContains(
            response,
            reverse('classifier:spesies_detail', args=['bekantan']),
        )
