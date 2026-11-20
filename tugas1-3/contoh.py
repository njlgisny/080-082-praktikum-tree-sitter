import os
from pathlib import Path

nama = "Nad"

def sapa(nama):
    """Menampilkan sapaan kepada pengguna."""
    print("Halo", nama)


def hitung(a, b):
    """Menjumlahkan dua bilangan."""
    hasil = a + b
    print(hasil)
    return hasil


sapa(nama)
hitung(10, 20)
