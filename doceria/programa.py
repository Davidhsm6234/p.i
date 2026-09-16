import sqlite3
from datetime import datetime


# ==============================
# LIMPAR TERMINAL
# ==============================

def limpar_terminal():
    print("\033[H\033[J", end="")


# ==============================
# CONEXÃO COM O BANCO
# ==============================

conexao = sqlite3.connect("doceria.db")
cursor = conexao.cursor()


# ==========================================================
# ÁREA DO CLIENTE - FAZER PEDIDO
# ==========================================================

def fazer_pedido():

    limpar_terminal()

    itens = []
    total = 0

    print("\n========================================")
    print("           ÁREA DO CLIENTE")
    print("========================================")
    print("              FAZER PEDIDO")
    print("========================================")

    while True:

        print("\nProdutos disponíveis:")
        print("----------------------------------------")

        cursor.execute("""
        SELECT id, nome, preco
        FROM produtos
        ORDER BY id
        """)

        produtos = cursor.fetchall()

        for produto in produtos:
            print(
                f"{produto[0]} - "
                f"{produto[1].capitalize()} - "
                f"R$ {produto[2]:.2f}"
            )

        print("0 - Finalizar pedido")
        print("----------------------------------------")

        try:
            produto_id = int(
                input("Digite o ID do produto: ")
            )
        except ValueError:
            print("\nDigite apenas números.")
            continue

        # Finalizar pedido
        if produto_id == 0:

            if len(itens) == 0:
                print("\nVocê ainda não adicionou nenhum produto.")
                continue

            break

        # Busca o produto no banco
        cursor.execute("""
        SELECT id, nome, preco
        FROM produtos
        WHERE id = ?
        """, (produto_id,))

        produto = cursor.fetchone()

        if produto is None:
            print("\nProduto não encontrado!")
            continue

        # Solicita quantidade
        try:
            quantidade = int(
                input(f"Quantidade de {produto[1]}: ")
            )
        except ValueError:
            print("\nDigite uma quantidade válida.")
            continue

        if quantidade <= 0:
            print("\nA quantidade deve ser maior que zero.")
            continue

        # Calcula subtotal
        subtotal = produto[2] * quantidade

        # Adiciona produto ao pedido
        itens.append({
            "produto_id": produto[0],
            "nome": produto[1],
            "quantidade": quantidade,
            "preco": produto[2],
            "subtotal": subtotal
        })

        total += subtotal

        print("\n----------------------------------------")
        print("Produto adicionado!")
        print(f"Produto: {produto[1].capitalize()}")
        print(f"Quantidade: {quantidade}")
        print(f"Subtotal: R$ {subtotal:.2f}")
        print(f"Total atual: R$ {total:.2f}")
        print("----------------------------------------")

    # ======================================================
    # RESUMO DO PEDIDO
    # ======================================================

    limpar_terminal()

    print("\n========================================")
    print("             RESUMO DO PEDIDO")
    print("========================================")

    for item in itens:

        print(
            f"{item['quantidade']}x "
            f"{item['nome'].capitalize()} "
            f"- R$ {item['subtotal']:.2f}"
        )

    print("----------------------------------------")
    print(f"TOTAL: R$ {total:.2f}")
    print("========================================")

    confirmar = input(
        "Deseja confirmar o pedido? (s/n): "
    ).lower()

    if confirmar != "s":

        limpar_terminal()

        print("\nPedido cancelado.")
        input("\nPressione ENTER para voltar...")
        return

    # ======================================================
    # DATA E HORA
    # ======================================================

    data = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    # ======================================================
    # SALVA O PEDIDO
    # ======================================================

    cursor.execute("""
    INSERT INTO pedidos (data, valor_total)
    VALUES (?, ?)
    """, (data, total))

    # Número do pedido
    pedido_id = cursor.lastrowid

    # ======================================================
    # SALVA OS ITENS DO PEDIDO
    # ======================================================

    for item in itens:

        cursor.execute("""
        INSERT INTO itens_pedido (
            pedido_id,
            produto_id,
            quantidade,
            preco_unitario,
            subtotal
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            pedido_id,
            item["produto_id"],
            item["quantidade"],
            item["preco"],
            item["subtotal"]
        ))

    # Confirma alterações
    conexao.commit()

    # ======================================================
    # CONFIRMAÇÃO PARA O CLIENTE
    # ======================================================

    limpar_terminal()

    print("\n========================================")
    print("       PEDIDO REALIZADO COM SUCESSO!")
    print("========================================")
    print(f"Pedido Nº: {pedido_id}")
    print(f"Total: R$ {total:.2f}")
    print(f"Data: {data}")
    print("========================================")

    input("\nPressione ENTER para voltar...")


# ==========================================================
# ÁREA ADMINISTRATIVA - VER PEDIDOS
# ==========================================================

def visualizar_pedidos():

    limpar_terminal()

    print("\n========================================")
    print("         PEDIDOS REALIZADOS")
    print("========================================")

    cursor.execute("""
    SELECT id, data, valor_total
    FROM pedidos
    ORDER BY id DESC
    """)

    pedidos = cursor.fetchall()

    if not pedidos:

        print("\nNenhum pedido foi realizado.")
        input("\nPressione ENTER para voltar...")
        return

    for pedido in pedidos:

        pedido_id = pedido[0]
        data = pedido[1]
        total = pedido[2]

        print("\n----------------------------------------")
        print(f"PEDIDO Nº {pedido_id}")
        print(f"Data: {data}")
        print("----------------------------------------")

        cursor.execute("""
        SELECT
            produtos.nome,
            itens_pedido.quantidade,
            itens_pedido.preco_unitario,
            itens_pedido.subtotal
        FROM itens_pedido
        INNER JOIN produtos
            ON produtos.id = itens_pedido.produto_id
        WHERE itens_pedido.pedido_id = ?
        """, (pedido_id,))

        itens = cursor.fetchall()

        for item in itens:

            print(
                f"{item[1]}x "
                f"{item[0].capitalize()} "
                f"| R$ {item[2]:.2f} "
                f"| Subtotal: R$ {item[3]:.2f}"
            )

        print("----------------------------------------")
        print(f"TOTAL: R$ {total:.2f}")

    print("\n========================================")

    input("\nPressione ENTER para voltar...")


# ==========================================================
# ÁREA ADMINISTRATIVA - TABELA DE PEDIDOS
# ==========================================================

def tabela_pedidos():

    limpar_terminal()

    print("\n")
    print("=" * 95)
    print("                         TABELA DE PEDIDOS")
    print("=" * 95)

    cursor.execute("""
    SELECT
        pedidos.id,
        pedidos.data,
        produtos.nome,
        itens_pedido.quantidade,
        itens_pedido.preco_unitario,
        itens_pedido.subtotal
    FROM pedidos
    INNER JOIN itens_pedido
        ON pedidos.id = itens_pedido.pedido_id
    INNER JOIN produtos
        ON produtos.id = itens_pedido.produto_id
    ORDER BY pedidos.id DESC
    """)

    dados = cursor.fetchall()

    if not dados:

        print("\nNenhum pedido foi realizado.")
        input("\nPressione ENTER para voltar...")
        return

    print(
        f"{'PEDIDO':<9}"
        f"{'DATA':<20}"
        f"{'PRODUTO':<18}"
        f"{'QTD':<8}"
        f"{'PREÇO':<12}"
        f"{'SUBTOTAL':<12}"
    )

    print("-" * 95)

    for dado in dados:

        pedido = dado[0]
        data = dado[1]
        produto = dado[2]
        quantidade = dado[3]
        preco = dado[4]
        subtotal = dado[5]

        print(
            f"{pedido:<9}"
            f"{data:<20}"
            f"{produto.capitalize():<18}"
            f"{quantidade:<8}"
            f"R$ {preco:<9.2f}"
            f"R$ {subtotal:<9.2f}"
        )

    print("=" * 95)

    input("\nPressione ENTER para voltar...")


# ==========================================================
# ÁREA ADMINISTRATIVA
# ==========================================================

def area_administrativa():

    while True:

        limpar_terminal()

        print("\n========================================")
        print("        ÁREA ADMINISTRATIVA")
        print("========================================")
        print("1 - Ver pedidos realizados")
        print("2 - Ver tabela de pedidos")
        print("3 - Voltar")
        print("========================================")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":

            visualizar_pedidos()

        elif opcao == "2":

            tabela_pedidos()

        elif opcao == "3":

            break

        else:

            print("\nOpção inválida!")
            input("\nPressione ENTER para continuar...")


# ==========================================================
# MENU PRINCIPAL
# ==========================================================

while True:

    limpar_terminal()

    print("\n========================================")
    print("               DOCERIA")
    print("========================================")
    print("1 - Área do Cliente")
    print("2 - Área Administrativa")
    print("3 - Sair")
    print("========================================")

    opcao = input("Escolha uma opção: ")

    # Área do cliente
    if opcao == "1":

        fazer_pedido()

    # Área administrativa
    elif opcao == "2":

        area_administrativa()

    # Sair
    elif opcao == "3":

        limpar_terminal()

        print("\nObrigado por utilizar o sistema da Doceria!")
        break

    else:

        print("\nOpção inválida!")
        input("\nPressione ENTER para continuar...")


# Fecha a conexão
conexao.close()
