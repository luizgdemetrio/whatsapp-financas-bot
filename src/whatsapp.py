import re
import time
import random
import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from database import configurar_banco, salvar_mensagem


def iniciar_whatsapp():
    """Inicia o WhatsApp Web e pede para escanear o QR Code."""
    service = Service(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()

    driver = webdriver.Firefox(service=service, options=options)

    driver.get("https://web.whatsapp.com")
    input(
        "🔗 Escaneie o QR Code e pressione ENTER para continuar..."
    )  # Aguarde o usuário escanear

    return driver


def digitar_como_humano(driver, elemento, texto):
    """Digita cada caractere com um intervalo aleatório para simular digitação humana."""
    action = ActionChains(driver)

    for letra in texto:
        action.send_keys(letra).perform()
        time.sleep(random.uniform(0.1, 0.3))


def encontrar_grupo(driver, contato):
    """Procura o grupo pelo nome e entra no chat com digitação humanizada."""
    wait = WebDriverWait(driver, 20)

    print(f"🔍 Procurando pelo grupo '{contato}'...")

    try:
        busca = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Pesquisar']"))
        )
        busca.click()
        time.sleep(random.uniform(0.5, 1.2))

        digitar_como_humano(driver, busca, contato)

        time.sleep(random.uniform(1, 2))
        busca.send_keys(Keys.ENTER)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//footer//div[@contenteditable='true']")
            )
        )
        print(f"✅ Grupo '{contato}' encontrado e pronto para capturar mensagens.")

        # Enviar mensagem de boas-vindas ao grupo
        enviar_mensagem(
            driver,
            contato,
            "🤖 Olá pessoal! Estou aqui para ajudar a registrar suas transações financeiras. 💰",
        )

        return True
    except Exception as e:
        print(f"❌ Grupo '{contato}' não encontrado! Erro: {e}")
        driver.quit()
        return False


def mensagem_eh_financeira(mensagem):
    """Verifica se a mensagem segue um padrão financeiro."""
    padrao_financeiro = re.compile(
        r"""
        (\+|\-)?\s?R?\$?\s?\d+(?:,\d{2})?    
        | (\d+x\s?R?\$?\s?\d+(?:,\d{2})?)    
        | (Ganhei|Gastei|Paguei|Recebi)\s\d+ 
    """,
        re.IGNORECASE | re.VERBOSE,
    )

    return bool(padrao_financeiro.search(mensagem))


def mensagem_ja_registrada(mensagem, hora):
    """Verifica no banco se a mensagem já foi registrada."""
    conexao = sqlite3.connect("mensagens.db")
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM mensagens WHERE mensagem = ? AND hora = ?", (mensagem, hora)
    )
    existe = cursor.fetchone()

    conexao.close()
    return bool(existe)


def capturar_mensagens(driver, grupo_nome):
    """Captura mensagens financeiras do grupo e envia confirmação apenas para novas transações."""
    wait = WebDriverWait(driver, 10)

    try:
        mensagens_elementos = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'message-in') or contains(@class, 'message-out')]",
        )

        for msg_elem in mensagens_elementos:
            try:
                # Capturar classe da mensagem (para saber se foi enviada pelo bot)
                classe_msg = msg_elem.get_attribute("class")

                # Captura o texto da mensagem
                mensagem = msg_elem.find_element(
                    By.XPATH, ".//span[contains(@class, 'selectable-text')]"
                ).text
                hora = msg_elem.find_element(
                    By.CSS_SELECTOR,
                    ".x13yyeie.xx3o462.xuxw1ft.x78zum5.x6s0dn4.x12lo8hy.x152skdk",
                ).text

                # Se a mensagem foi enviada pelo bot, ignoramos
                if "message-out" in classe_msg or "Registro adicionado" in mensagem:
                    print(f"🤖 Mensagem do bot ignorada: [{hora}] {mensagem}")
                    continue

                if mensagem_eh_financeira(mensagem):
                    descricao = obter_descricao(mensagem)
                    mensagem_formatada = f"{mensagem} ({descricao})"

                    # Verificar se já foi registrada antes
                    if not mensagem_ja_registrada(mensagem_formatada, hora):
                        salvar_mensagem(mensagem_formatada, hora)

                        # Enviar confirmação no grupo **apenas se for uma nova transação**
                        mensagem_confirmacao = (
                            f"✅ Registro adicionado: {mensagem_formatada} - ({hora})"
                        )
                        enviar_mensagem(driver, grupo_nome, mensagem_confirmacao)
                    else:
                        print(
                            f"🔄 Mensagem já registrada: [{hora}] {mensagem_formatada}"
                        )
                else:
                    print(f"🚫 Mensagem ignorada (não financeira): [{hora}] {mensagem}")

            except Exception as e:
                print(f"⚠️ Erro ao capturar uma mensagem: {e}")
                continue

    except Exception as e:
        print(f"⚠️ Erro ao capturar mensagens: {e}")


def obter_descricao(mensagem):
    """Pede uma descrição ao usuário caso não esteja presente na mensagem."""
    palavras = mensagem.split()

    if len(palavras) == 1 or (len(palavras) == 2 and "R$" in palavras):
        print(f"📝 Mensagem detectada sem descrição: {mensagem}")
        descricao = input("❓ Qual é a descrição dessa transação? ")
        return descricao.strip() if descricao else "Sem descrição"

    return " ".join(palavras[1:])


def reencontrar_chat(driver):
    """Reencontra o campo de mensagem do grupo para evitar erros."""
    wait = WebDriverWait(driver, 10)
    return wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//footer//div[@contenteditable='true']")
        )
    )


def enviar_mensagem(driver, contato, mensagem):
    """Envia uma mensagem automática para o grupo."""
    try:
        chat = reencontrar_chat(driver)

        driver.execute_script("arguments[0].scrollIntoView(true);", chat)
        time.sleep(1.5)

        action = ActionChains(driver)
        action.move_to_element(chat).click().perform()
        time.sleep(random.uniform(0.5, 1.2))

        chat.click()
        time.sleep(0.5)

        digitar_como_humano(driver, chat, mensagem)
        chat.send_keys(Keys.ENTER)

        print(f"📩 Mensagem enviada para '{contato}': {mensagem}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para '{contato}'. Erro: {e}")


if __name__ == "__main__":
    configurar_banco()

    driver = iniciar_whatsapp()

    grupo_nome = input("📢 Qual é o nome exato do grupo para capturar mensagens? ")

    if encontrar_grupo(driver, grupo_nome):
        print(
            "\n📡 Monitorando mensagens do grupo. Pressione 'CTRL + C' para interromper.\n"
        )
        try:
            while True:
                capturar_mensagens(driver, grupo_nome)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido pelo usuário (CTRL + C).")

    driver.quit()
    print("✅ Bot encerrado com sucesso.")
