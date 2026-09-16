import sqlite3

conexao = sqlite3.connect("doceria.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    preco REAL NOT NULL
)
""")

produtos = [
    ("brigadeiro", 5),
    ("beijinho", 4),
    ("bolo", 10),
    ("brownie", 8)
]

cursor.executemany(
    "INSERT OR IGNORE INTO produtos (nome, preco) VALUES (?, ?)",
    produtos
)

conexao.commit()

print("Banco de dados configurado com sucesso!")

conexao.close()