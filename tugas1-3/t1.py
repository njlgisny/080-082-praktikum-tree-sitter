
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Membuat parser Python
parser = Parser(Language(tspython.language()))

# 1. Contoh Function
kode_fungsi = b"""
def sapa(nama):
    return "Halo " + nama
"""

# 2. Contoh If-Else
kode_if = b"""
nilai = 80
if nilai >= 75:
    print("Lulus")
else:
    print("Tidak Lulus")
"""

# 3. Contoh Class dengan satu Method
kode_class = b"""
class Mahasiswa:
    def __init__(self, nama):
        self.nama = nama
"""

# Parsing dan menampilkan root_node
for nama, kode in [
    ("FUNCTION", kode_fungsi),
    ("IF-ELSE", kode_if),
    ("CLASS", kode_class)
]:
    tree = parser.parse(kode)
    print(f"\n=== {nama} ===")
    print(tree.root_node)


# Mengambil node function
tree = parser.parse(kode_fungsi)
fungsi = tree.root_node.children[0]

# Menampilkan seluruh node secara rekursif
def tampilkan_node(node, level=0):
    jenis = "bernama" if node.is_named else "anonim"
    print("  " * level + f"{node.type} - {jenis}")

    for child in node.children:
        tampilkan_node(child, level + 1)


print("\n=== MODE FUNCTION ===")
tampilkan_node(fungsi)

# Menampilkan node pada bagian parameters
print("\n=== MODE PARAMETERS ===")
parameters = fungsi.child_by_field_name("parameters")

if parameters:
    tampilkan_node(parameters)

# Menampilkan root node
print("\n=== MODE ROOT ===")
print(tree.root_node)
