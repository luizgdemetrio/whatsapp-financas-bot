import sqlite3

# 📌 Nome do banco de dados
DB_NAME = "mensagens.db"


def configurar_banco():
    """Cria ou atualiza a tabela de mensagens no banco de dados."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()

    # Criar a tabela se não existir
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensagem TEXT NOT NULL,
            hora TEXT NOT NULL,
            UNIQUE(mensagem, hora)  -- Impede duplicação de mesma mensagem no mesmo horário
        )
    """
    )

    # Verificar se a coluna 'hora' existe, se não, adicionar
    cursor.execute("PRAGMA table_info(mensagens);")
    colunas = [col[1] for col in cursor.fetchall()]

    if "hora" not in colunas:
        print("🔄 Atualizando banco de dados para incluir a coluna 'hora'...")
        cursor.execute("ALTER TABLE mensagens ADD COLUMN hora TEXT;")
        conexao.commit()

    conexao.close()


def salvar_mensagem(mensagem, hora):
    """Salva a mensagem no banco de dados se não for duplicada."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()

    # Verifica se a mensagem já foi armazenada
    cursor.execute(
        "SELECT id FROM mensagens WHERE mensagem = ? AND hora = ?", (mensagem, hora)
    )
    existe = cursor.fetchone()

    if not existe:
        cursor.execute(
            "INSERT INTO mensagens (mensagem, hora) VALUES (?, ?)", (mensagem, hora)
        )
        conexao.commit()
        print(f"✅ Nova mensagem salva: [{hora}] {mensagem}")
    else:
        print(f"🔄 Mensagem duplicada ignorada: [{hora}] {mensagem}")

    conexao.close()
