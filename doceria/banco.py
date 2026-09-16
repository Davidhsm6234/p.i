import sqlite3

# Conecta ao banco de dados
conexao = sqlite3.connect("doceria.db")
cursor = conexao.cursor()

# ==============================
# TABELA DE PRODUTOS
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    preco REAL NOT NULL
)
""")

# ==============================
# TABELA DE PEDIDOS
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    valor_total REAL NOT NULL
)
""")

# ==============================
# TABELA DE ITENS DO PEDIDO
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    subtotal REAL NOT NULL
)
""")

# ==============================
# PRODUTOS
# ==============================

produtos = [
    ("brigadeiro", 5.00),
    ("beijinho", 4.00),
    ("bolo", 10.00),
    ("brownie", 8.00)
]

for nome, preco in produtos:
    cursor.execute("""
    INSERT OR IGNORE INTO produtos (nome, preco)
    VALUES (?, ?)
    """, (nome, preco))

# Salva as alterações
conexao.commit()

# Fecha a conexão
conexao.close()

print("Banco de dados criado com sucesso!")
print("Tabelas: produtos, pedidos e itens_pedido")

