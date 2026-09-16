import sqlite3

conexao = sqlite3.connect("doceria.db")
cursor = conexao.cursor()

cursor.execute("""
UPDATE produtos
SET preco = 
WHERE nome = ''
""")

conexao.commit()

print("Preço alterado com sucesso!")

conexao.close()


"python alterar_preco.py" "jogar no terminal"