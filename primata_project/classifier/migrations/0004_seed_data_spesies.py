"""
Data migration: mengisi tabel Spesies & FaktaSpesies dengan data yang
BERSUMBER, bukan dibuat sendiri.

Sumber yang dipakai (per kategori):

1) status_konservasi -> IUCN Red List of Threatened Species (otoritas resmi
   status konservasi global):
   - Nasalis larvatus: Boonratana, R., Cheyne, S.M., Traeholt, C., Nijman, V.
     & Supriatna, J. 2021. Nasalis larvatus. The IUCN Red List of Threatened
     Species 2020: e.T14352A17945165.
     https://www.iucnredlist.org/species/14352/17945165
     doi: 10.2305/IUCN.UK.2020-2.RLTS.T14352A17945165.en
   - Pongo pygmaeus: Ancrenaz, M., Gumal, M., Marshall, A.J., Meijaard, E.,
     Wich, S.A. & Husson, S. 2016 (errata version 2018). Pongo pygmaeus. The
     IUCN Red List of Threatened Species 2016: e.T17975A123809220.
     https://www.iucnredlist.org/species/17975/17966347
     doi: 10.2305/IUCN.UK.2016-1.RLTS.T17975A17966347.en
   - Pongo abelii: Singleton, I., Wich, S.A., Nowak, M., Usher, G. &
     Utami-Atmoko, S.S. 2017 (errata version 2018). Pongo abelii. The IUCN
     Red List of Threatened Species 2017: e.T121097935A123797627.
     https://www.iucnredlist.org/species/121097935/115575085
     doi: 10.2305/IUCN.UK.2017-3.RLTS.T121097935A115575085.en

2) taksonomi & distribusi -> Mammal Diversity Database (MDD), American
   Society of Mammalogists:
   - Nasalis larvatus: https://www.mammaldiversity.org/taxon/1000659
   - Pongo pygmaeus: https://www.mammaldiversity.org/taxon/1000722
   - Pongo abelii: https://www.mammaldiversity.org/taxon/1000721
   MDD mengutip Groves, C.P. 2005. "Order Primates". In Wilson, D.E. &
   Reeder, D.M. (eds), Mammal Species of the World: A Taxonomic and
   Geographic Reference (3rd ed). Johns Hopkins University Press, pp. 111-184
   sebagai rujukan taksonomi dasar.

3) ciri_fisik -> paper ilmiah / monograf taxonomic revision:
   - Nasalis larvatus: Bennett, E.L. & Sebastian, A.C. 1988. "Social
     organization and ecology of proboscis monkeys (Nasalis larvatus) in
     mixed coastal forest in Sarawak." International Journal of Primatology,
     9(3), 233-255. doi: 10.1007/BF02735198
   - Pongo pygmaeus & Pongo abelii (perbandingan morfologi antar spesies):
     Courtenay, J., Groves, C. & Andrews, P. 1988. "Inter- or intra-island
     variation? An assessment of the differences between Bornean and
     Sumatran orangutans." In: J.H. Schwartz (ed.), Orangutan Biology,
     pp. 19-29. Oxford University Press. (dikutip ulang di banyak lembar
     fakta institusi primata, a.l. San Diego Zoo Wildlife Alliance &
     Wisconsin National Primate Research Center PIN Factsheet)

CATATAN PENTING UNTUK PENGEMBANG:
- Field `source_date` di sini diisi tanggal migrasi ini ditulis/diverifikasi
  (tanggal akses), BUKAN tanggal terbit sumber -- tanggal terbit sumber ada
  di `source_year`.
- Jika IUCN merilis asesmen baru untuk salah satu spesies ini, update baris
  status_konservasi terkait (jangan menimpa kategori lain) dan perbarui
  source_date.
- Jangan menambah klaim ilmiah baru ke `isi` tanpa menambah/menyesuaikan
  source_* -- prinsip "satu fakta, satu sumber yang bisa dicek".
"""
from django.db import migrations

TANGGAL_AKSES = '2026-09-18'


def seed_data(apps, schema_editor):
    Spesies = apps.get_model('classifier', 'Spesies')
    FaktaSpesies = apps.get_model('classifier', 'FaktaSpesies')

    data = [
        {
            'kode': 'bekantan',
            'nama_umum': 'Bekantan',
            'nama_ilmiah': 'Nasalis larvatus',
            'otoritas_taksonomi': '(Wurmb, 1787)',
            'famili': 'Cercopithecidae',
            'fakta': [
                dict(
                    kategori='taksonomi',
                    isi=(
                        'Famili Cercopithecidae, subfamili Colobinae. Genus Nasalis '
                        'bersifat monotipik (hanya berisi satu spesies, N. larvatus). '
                        'Subspesies N. l. orientalis pernah diusulkan namun tidak '
                        'diakui secara konsisten oleh semua otoritas taksonomi.'
                    ),
                    source_type='mdd',
                    source_title='Nasalis larvatus (Mammal Diversity Database, taxon 1000659)',
                    source_author='American Society of Mammalogists; mengutip Groves, C.P. (2005)',
                    source_year=2005,
                    source_doi='',
                    source_url='https://www.mammaldiversity.org/taxon/1000659',
                ),
                dict(
                    kategori='status_konservasi',
                    isi='Endangered (EN) - kategori risiko kepunahan tinggi pada skala IUCN Red List.',
                    source_type='iucn_red_list',
                    source_title=(
                        'Nasalis larvatus. The IUCN Red List of Threatened Species '
                        '2020: e.T14352A17945165'
                    ),
                    source_author='Boonratana, R., Cheyne, S.M., Traeholt, C., Nijman, V. & Supriatna, J.',
                    source_year=2021,
                    source_doi='10.2305/IUCN.UK.2020-2.RLTS.T14352A17945165.en',
                    source_url='https://www.iucnredlist.org/species/14352/17945165',
                ),
                dict(
                    kategori='ciri_fisik',
                    isi=(
                        'Jantan dewasa memiliki hidung besar dan menggantung, diduga '
                        'berfungsi memperkuat resonansi vokalisasi dan sebagai penanda '
                        'status sosial; betina memiliki hidung lebih kecil dan runcing. '
                        'Panjang tubuh (kepala-badan) jantan dewasa sekitar 66-76,2 cm '
                        'dengan berat 16-22,5 kg; betina lebih kecil, panjang sekitar '
                        '53,3-62 cm dengan berat 7-12 kg. Bulu tubuh oranye-cokelat, '
                        'wajah kemerahan, dan ekor panjang berwarna putih keabuan.'
                    ),
                    source_type='jurnal_ilmiah',
                    source_title=(
                        'Social organization and ecology of proboscis monkeys '
                        '(Nasalis larvatus) in mixed coastal forest in Sarawak'
                    ),
                    source_author='Bennett, E.L. & Sebastian, A.C.',
                    source_year=1988,
                    source_doi='10.1007/BF02735198',
                    source_url='https://doi.org/10.1007/BF02735198',
                ),
                dict(
                    kategori='distribusi',
                    isi=(
                        'Endemik Pulau Borneo; tersebar di Kalimantan (Indonesia), '
                        'Sabah dan Sarawak (Malaysia), serta Brunei Darussalam. Tidak '
                        'ditemukan secara alami di luar Borneo.'
                    ),
                    source_type='mdd',
                    source_title='Nasalis larvatus - distribusi negara (Mammal Diversity Database, taxon 1000659)',
                    source_author='American Society of Mammalogists',
                    source_year=2026,
                    source_doi='',
                    source_url='https://www.mammaldiversity.org/taxon/1000659',
                ),
                dict(
                    kategori='habitat',
                    isi=(
                        'Hutan bakau (mangrove), hutan rawa gambut, hutan pesisir, dan '
                        'hutan riparian di sepanjang sungai besar, umumnya pada '
                        'ketinggian di bawah 250 m dpl.'
                    ),
                    source_type='iucn_red_list',
                    source_title=(
                        'Nasalis larvatus. The IUCN Red List of Threatened Species '
                        '2020: e.T14352A17945165 (bagian Habitat and Ecology)'
                    ),
                    source_author='Boonratana, R., Cheyne, S.M., Traeholt, C., Nijman, V. & Supriatna, J.',
                    source_year=2021,
                    source_doi='10.2305/IUCN.UK.2020-2.RLTS.T14352A17945165.en',
                    source_url='https://www.iucnredlist.org/species/14352/17945165',
                ),
            ],
        },
        {
            'kode': 'orangutan_kalimantan',
            'nama_umum': 'Orangutan Kalimantan',
            'nama_ilmiah': 'Pongo pygmaeus',
            'otoritas_taksonomi': '(Linnaeus, 1760)',
            'famili': 'Hominidae',
            'fakta': [
                dict(
                    kategori='taksonomi',
                    isi=(
                        'Famili Hominidae, subfamili Ponginae. Tiga subspesies diakui '
                        'berdasarkan wilayah geografis di Kalimantan: P. p. pygmaeus, '
                        'P. p. wurmbii, dan P. p. morio.'
                    ),
                    source_type='mdd',
                    source_title='Pongo pygmaeus (Mammal Diversity Database, taxon 1000722)',
                    source_author='American Society of Mammalogists; mengutip Groves, C.P. (2005)',
                    source_year=2005,
                    source_doi='',
                    source_url='https://www.mammaldiversity.org/taxon/1000722',
                ),
                dict(
                    kategori='status_konservasi',
                    isi='Critically Endangered (CR) - risiko kepunahan sangat tinggi, satu tingkat di bawah punah di alam liar.',
                    source_type='iucn_red_list',
                    source_title=(
                        'Pongo pygmaeus (errata version published in 2018). The IUCN '
                        'Red List of Threatened Species 2016: e.T17975A123809220'
                    ),
                    source_author='Ancrenaz, M., Gumal, M., Marshall, A.J., Meijaard, E., Wich, S.A. & Husson, S.',
                    source_year=2016,
                    source_doi='10.2305/IUCN.UK.2016-1.RLTS.T17975A17966347.en',
                    source_url='https://www.iucnredlist.org/species/17975/17966347',
                ),
                dict(
                    kategori='ciri_fisik',
                    isi=(
                        'Dibandingkan orangutan Sumatra, orangutan Kalimantan '
                        'bertubuh lebih besar dan berat; wajah lebih lebar berbentuk '
                        'menyerupai angka 8; bantalan pipi (flange) pada jantan dewasa '
                        'lebih besar dan menonjol ke depan dengan rambut pendek dan '
                        'kaku; kantung tenggorokan (throat sac) lebih besar; warna '
                        'bulu cenderung lebih gelap (cokelat kemerahan tua hingga '
                        'marun).'
                    ),
                    source_type='buku_monograf',
                    source_title=(
                        'Inter- or intra-island variation? An assessment of the '
                        'differences between Bornean and Sumatran orangutans, dalam '
                        'buku Orangutan Biology (J.H. Schwartz, ed.), hlm. 19-29'
                    ),
                    source_author='Courtenay, J., Groves, C. & Andrews, P.',
                    source_year=1988,
                    source_doi='',
                    source_url='https://global.oup.com/academic/product/orangutan-biology-9780195052070',
                ),
                dict(
                    kategori='distribusi',
                    isi=(
                        'Endemik Pulau Kalimantan (Borneo); tersebar di wilayah '
                        'Kalimantan Indonesia (Kalimantan Barat, Tengah, Timur, dan '
                        'Utara) serta Sabah dan Sarawak, Malaysia.'
                    ),
                    source_type='mdd',
                    source_title='Pongo pygmaeus - distribusi negara (Mammal Diversity Database, taxon 1000722)',
                    source_author='American Society of Mammalogists',
                    source_year=2026,
                    source_doi='',
                    source_url='https://www.mammaldiversity.org/taxon/1000722',
                ),
                dict(
                    kategori='habitat',
                    isi=(
                        'Hutan hujan tropis dataran rendah hingga perbukitan, '
                        'termasuk hutan rawa gambut, umumnya hingga ketinggian '
                        'sekitar 800 m dpl. Lebih toleran terhadap gangguan/degradasi '
                        'habitat dibandingkan orangutan Sumatra.'
                    ),
                    source_type='iucn_red_list',
                    source_title=(
                        'Pongo pygmaeus (errata version published in 2018). The IUCN '
                        'Red List of Threatened Species 2016: e.T17975A123809220 '
                        '(bagian Habitat and Ecology)'
                    ),
                    source_author='Ancrenaz, M., Gumal, M., Marshall, A.J., Meijaard, E., Wich, S.A. & Husson, S.',
                    source_year=2016,
                    source_doi='10.2305/IUCN.UK.2016-1.RLTS.T17975A17966347.en',
                    source_url='https://www.iucnredlist.org/species/17975/17966347',
                ),
            ],
        },
        {
            'kode': 'orangutan_sumatra',
            'nama_umum': 'Orangutan Sumatra',
            'nama_ilmiah': 'Pongo abelii',
            'otoritas_taksonomi': '(Lesson, 1827)',
            'famili': 'Hominidae',
            'fakta': [
                dict(
                    kategori='taksonomi',
                    isi=(
                        'Famili Hominidae, subfamili Ponginae. Sebagian populasi yang '
                        'kini termasuk spesies terpisah Pongo tapanuliensis '
                        '(Orangutan Tapanuli) sebelumnya dimasukkan ke dalam Pongo '
                        'abelii, sampai dipisahkan berdasarkan bukti morfometrik, '
                        'perilaku, dan genom oleh Nater et al. (2017).'
                    ),
                    source_type='jurnal_ilmiah',
                    source_title='Morphometric, behavioral, and genomic evidence for a new orangutan species',
                    source_author='Nater, A., Mattle-Greminger, M.P., Nurcahyo, A., et al.',
                    source_year=2017,
                    source_doi='10.1016/j.cub.2017.09.047',
                    source_url='https://doi.org/10.1016/j.cub.2017.09.047',
                ),
                dict(
                    kategori='status_konservasi',
                    isi='Critically Endangered (CR) - risiko kepunahan sangat tinggi, satu tingkat di bawah punah di alam liar.',
                    source_type='iucn_red_list',
                    source_title=(
                        'Pongo abelii (errata version published in 2018). The IUCN '
                        'Red List of Threatened Species 2017: e.T121097935A123797627'
                    ),
                    source_author='Singleton, I., Wich, S.A., Nowak, M., Usher, G. & Utami-Atmoko, S.S.',
                    source_year=2017,
                    source_doi='10.2305/IUCN.UK.2017-3.RLTS.T121097935A115575085.en',
                    source_url='https://www.iucnredlist.org/species/121097935/115575085',
                ),
                dict(
                    kategori='ciri_fisik',
                    isi=(
                        'Dibandingkan orangutan Kalimantan, orangutan Sumatra '
                        'bertubuh lebih ramping (gracile); wajah lebih memanjang '
                        'berbentuk oval; bantalan pipi (flange) pada jantan dewasa '
                        'relatif rata/tidak menonjol ke depan dan ditutupi rambut '
                        'halus keputihan; kantung tenggorokan lebih kecil; bulu lebih '
                        'panjang dan berwarna lebih pucat (jingga kecoklatan terang).'
                    ),
                    source_type='buku_monograf',
                    source_title=(
                        'Inter- or intra-island variation? An assessment of the '
                        'differences between Bornean and Sumatran orangutans, dalam '
                        'buku Orangutan Biology (J.H. Schwartz, ed.), hlm. 19-29'
                    ),
                    source_author='Courtenay, J., Groves, C. & Andrews, P.',
                    source_year=1988,
                    source_doi='',
                    source_url='https://global.oup.com/academic/product/orangutan-biology-9780195052070',
                ),
                dict(
                    kategori='distribusi',
                    isi=(
                        'Endemik bagian utara Pulau Sumatra, Indonesia, terutama di '
                        'Provinsi Aceh dan Sumatera Utara.'
                    ),
                    source_type='mdd',
                    source_title='Pongo abelii - distribusi negara (Mammal Diversity Database, taxon 1000721)',
                    source_author='American Society of Mammalogists',
                    source_year=2026,
                    source_doi='',
                    source_url='https://www.mammaldiversity.org/taxon/1000721',
                ),
                dict(
                    kategori='habitat',
                    isi=(
                        'Hutan hujan tropis dataran rendah hingga hutan pegunungan, '
                        'termasuk hutan rawa gambut. Lebih sensitif terhadap '
                        'gangguan/degradasi habitat (misalnya penebangan selektif) '
                        'dibandingkan orangutan Kalimantan.'
                    ),
                    source_type='iucn_red_list',
                    source_title=(
                        'Pongo abelii (errata version published in 2018). The IUCN '
                        'Red List of Threatened Species 2017: e.T121097935A123797627 '
                        '(bagian Habitat and Ecology)'
                    ),
                    source_author='Singleton, I., Wich, S.A., Nowak, M., Usher, G. & Utami-Atmoko, S.S.',
                    source_year=2017,
                    source_doi='10.2305/IUCN.UK.2017-3.RLTS.T121097935A115575085.en',
                    source_url='https://www.iucnredlist.org/species/121097935/115575085',
                ),
            ],
        },
    ]

    for item in data:
        fakta_list = item.pop('fakta')
        spesies = Spesies.objects.create(**item)
        for fakta in fakta_list:
            FaktaSpesies.objects.create(spesies=spesies, source_date=TANGGAL_AKSES, **fakta)


def unseed_data(apps, schema_editor):
    Spesies = apps.get_model('classifier', 'Spesies')
    Spesies.objects.filter(
        kode__in=['bekantan', 'orangutan_kalimantan', 'orangutan_sumatra']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('classifier', '0003_spesies_faktaspesies'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
