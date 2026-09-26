# Pengujian Black Box — Sistem Klasifikasi Primata Endemik Indonesia

Tabel ini bisa langsung diadaptasi untuk BAB IV (Hasil dan Pembahasan / Pengujian Sistem).
Kolom **Status** dikosongkan — isi manual setelah kamu coba tiap skenario di sistem kamu.

| No | Skenario Pengujian | Data Uji | Hasil yang Diharapkan | Status |
|----|---|---|---|---|
| 1 | Unggah foto Bekantan yang jelas | Foto Bekantan, pencahayaan baik | Sistem mengklasifikasikan sebagai "Bekantan" dengan confidence tinggi | |
| 2 | Unggah foto Orangutan Sumatra yang jelas | Foto Orangutan Sumatra | Sistem mengklasifikasikan sebagai "Orangutan Sumatra" | |
| 3 | Unggah foto Orangutan Kalimantan yang jelas | Foto Orangutan Kalimantan | Sistem mengklasifikasikan sebagai "Orangutan Kalimantan" | |
| 4 | Unggah foto dengan kualitas buram/gelap | Foto primata blur atau minim cahaya | Sistem tetap memberi hasil, kemungkinan dengan confidence lebih rendah | |
| 5 | Unggah foto primata di luar 3 kelas target | Foto monyet ekor panjang / spesies lain | Sistem tetap memaksa hasil ke salah satu dari 3 kelas (dicatat sebagai keterbatasan sistem di laporan) | |
| 6 | Unggah berkas bukan gambar | File .pdf atau .txt diganti ekstensi jadi .jpg | Sistem menampilkan pesan error yang jelas, **tidak** crash / server error 500 | |
| 7 | Submit tanpa memilih gambar | Klik tombol tanpa upload apapun | Tombol tetap nonaktif, atau sistem menampilkan pesan "silakan pilih gambar" | |
| 8 | Unggah gambar berukuran besar | Foto resolusi tinggi (>5 MB) | Sistem tetap memproses dengan normal (atau menolak dengan pesan jelas jika melebihi batas) | |
| 9 | Klasifikasi berturut-turut | Upload 3-5 gambar berbeda secara beruntun | Waktu respons tiap klasifikasi konsisten cepat (verifikasi model caching bekerja) | |
| 10 | Uji di browser/device berbeda | Buka di Chrome, Firefox, dan/atau HP | Tampilan tetap responsif dan form berfungsi normal | |
| 11 | Verifikasi sumber info spesies | Buka halaman hasil untuk ketiga kelas (Bekantan, Orangutan Kalimantan, Orangutan Sumatra) | Setiap bagian "Tentang [spesies]" menampilkan status konservasi, ciri fisik, distribusi, dan habitat, masing-masing dengan link "Lihat sumber" yang mengarah ke IUCN Red List / Mammal Diversity Database / DOI paper ilmiah (bukan teks tanpa rujukan) | |

## Catatan untuk akurasi model

Untuk BAB IV bagian evaluasi model, gunakan hasil dari Colab (bukan hasil manual testing di atas):

- **Akurasi pada test set: 78%**
- **Precision/recall per kelas**, dan **confusion matrix** — lampirkan langsung dari output cell terakhir training di Colab (screenshot atau salin tabelnya)
- Jelaskan temuan bahwa kesalahan klasifikasi didominasi oleh kekeliruan antara Orangutan Sumatra dan Orangutan Kalimantan, dan kaitkan dengan kemiripan visual antar dua spesies tersebut sebagai pembahasan hasil (bagian pembahasan/diskusi hasil pengujian)
