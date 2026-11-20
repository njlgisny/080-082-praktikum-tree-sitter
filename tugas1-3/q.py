
import sys
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

# Membuat parser Python
language = Language(tspython.language())
parser = Parser(language)

# Memastikan nama file Python diberikan
if len(sys.argv) < 2:
    print("Cara penggunaan: python q.py nama_file.py")
    sys.exit(1)

# Membaca dan mem-parsing file Python
file_python = Path(sys.argv[1])

with open(file_python, "rb") as f:
    tree = parser.parse(f.read())

# Mengambil semua file query .scm di folder yang sama
folder = Path(__file__).parent
daftar_query = sorted(folder.glob("*.scm"))

# Menjalankan semua query
for file_query in daftar_query:
    print(f"\n=== QUERY: {file_query.name} ===")

    source_query = file_query.read_text(encoding="utf-8")
    query = Query(language, source_query)
    cursor = QueryCursor(query)

    matches = cursor.matches(tree.root_node)

    if not matches:
        print("Tidak ada hasil.")
        continue

    # Menampilkan hasil query
    for _, captures in matches:
        for nama_capture, nodes in captures.items():
            for node in nodes:
                baris = node.start_point.row + 1
                teks = node.text.decode("utf-8")
                print(f"@{nama_capture} baris {baris}: {teks}")

    # Menghitung jumlah parameter fungsi
    if file_query.name == "fungsi.scm":
        print("\n=== Percobaan matches() ===")

        for _, captures in matches:
            nama = captures["nama"][0].text.decode("utf-8")
            params = captures["params"][0]

            jumlah = len(params.named_children)
            print(f"{nama} {jumlah}")
