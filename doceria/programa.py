import sqlite3

# Conecta ao banco
conexao = sqlite3.connect("doceria.db")
cursor = conexao.cursor()

print("SEJA BEM VINDO A DOCERIA!!")
print("Faça seu pedido conosco")

print("""
================================
            DOCERIA
================================
    Brigadeiro ........ R$ 5,00
    Beijinho .......... R$ 4,00
    Bolo .............. R$ 10,00
    Brownie ........... R$ 8,00
================================
""")

valortotal = 0

while True:

    opcao = input("Digite o nome do produto: ").lower()
    quantidade = int(input("Digite a quantidade desejada: "))

    # Procura o produto no banco de dados
    cursor.execute(
        "SELECT preco FROM produtos WHERE nome = ?",
        (opcao,)
    )

    resultado = cursor.fetchone()

    if resultado:

        preco = resultado[0]

        valortotal = valortotal + (preco * quantidade)

        print("Total do pedido até agora: R$", valortotal)

    else:

        print("Produto não encontrado")
        continue

    final = input(
        "Finalizar pedido digite 1, continuar pedido digite 2: "
    )

    if final == "1":

        print("Pedido finalizado")
        print("Valor total: R$", valortotal)

        break

    elif final == "2":

        print("Continuando pedido...")

conexao.close()