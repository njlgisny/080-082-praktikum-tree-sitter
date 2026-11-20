# Mini Proyek: Pendeteksi TODO dan Fungsi Panjang

Program sederhana berbasis CLI untuk memeriksa file Python menggunakan Tree-sitter.

## Dependensi

Program membutuhkan Python 3.10 atau lebih baru serta library `tree-sitter` dan `tree-sitter-python`.

Instal dependensi dengan perintah:

```bash
pip install tree-sitter tree-sitter-python
```

## Cara Menjalankan

Jalankan program dengan memasukkan folder yang ingin diperiksa sebagai argumen:

```bash
python cek.py <folder>
```

Contoh menjalankan program pada folder pengujian:

```bash
python cek.py uji/
```

## Fitur

- Mendeteksi komentar TODO dan FIXME beserta lokasi file dan baris.
- Mendeteksi fungsi yang memiliki lebih dari 30 baris.
- Mendeteksi kesalahan sintaks pada file Python dan melaporkan baris pertama yang bermasalah.

Program memeriksa semua fungsi yang ditemukan, termasuk fungsi di dalam kelas dan fungsi bersarang.

## Contoh Output

```text
cek\uji\deteksi_error.py: error pada baris 1
cek\uji\deteksi_fungsipjg.py: fungsi 'hitung_total' (33 baris)
cek\uji\deteksi_todo.py:1: # TODO: tambahkan validasi input
cek\uji\deteksi_todo.py:5: # FIXME: fungsi ini perlu diperbaiki
```
