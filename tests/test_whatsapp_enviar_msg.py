from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random


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
        time.sleep(random.uniform(0.1, 0.3))  # Tempo aleatório entre 0.1s e 0.3s


def encontrar_grupo(driver, contato):
    """Procura o grupo pelo nome e entra no chat com digitação humanizada."""
    wait = WebDriverWait(driver, 20)  # Espera de até 20s para os elementos carregarem

    print(f"🔍 Procurando pelo grupo '{contato}'...")

    try:
        busca = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Pesquisar']"))
        )
        busca.click()
        time.sleep(random.uniform(0.5, 1.2))  # Pequena pausa antes de começar a digitar

        # Usando ActionChains para digitação humanizada
        digitar_como_humano(driver, busca, contato)

        time.sleep(random.uniform(1, 2))  # Pausa para garantir que a busca carregue
        busca.send_keys(Keys.ENTER)

        # Verifica se o chat realmente abriu
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//footer//div[@contenteditable='true']")
            )
        )
        print(f"✅ Grupo '{contato}' encontrado e pronto para enviar mensagens.")
        return True
    except Exception as e:
        print(
            f"❌ Grupo '{contato}' não encontrado! Verifique o nome e tente novamente.\nErro: {e}"
        )
        driver.quit()
        return False


def reencontrar_chat(wait):
    """Reencontra o campo de mensagem caso ele tenha ficado obsoleto."""
    return wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//footer//div[@contenteditable='true']")
        )
    )


def enviar_mensagem(driver, contato, mensagem):
    """Verifica se o grupo foi encontrado antes de enviar a mensagem."""
    if not encontrar_grupo(driver, contato):
        return  # Se o grupo não foi encontrado, para a execução.

    wait = WebDriverWait(driver, 60)

    try:
        # Tentativa de encontrar a caixa de mensagem
        chat = reencontrar_chat(wait)

        # Garantir que o campo esteja visível e pronto para receber entrada
        driver.execute_script("arguments[0].scrollIntoView(true);", chat)
        time.sleep(1.5)  # Pequena pausa antes de interagir

        # Simular movimento do mouse até o campo de mensagem e clicar nele
        action = ActionChains(driver)
        action.move_to_element(chat).click().perform()
        time.sleep(
            random.uniform(0.5, 1.2)
        )  # Pequena pausa antes de digitar a mensagem

        # Clicar no campo de mensagem para garantir que não estamos na barra de pesquisa
        chat.click()
        time.sleep(0.5)

        digitar_como_humano(driver, chat, mensagem)  # Digitação humanizada da mensagem

        # Usar ENTER para enviar
        chat.send_keys(Keys.ENTER)
        time.sleep(1)  # Pequena pausa para garantir o envio

        print(f"✅ Mensagem enviada para o grupo '{contato}'!")

    except Exception as e:
        print(
            f"❌ Erro ao tentar enviar a mensagem! Verifique se o grupo foi encontrado corretamente.\nErro: {e}"
        )
        driver.quit()


if __name__ == "__main__":
    driver = iniciar_whatsapp()

    # Pergunta ao usuário qual é o grupo antes de enviar a mensagem
    grupo_nome = input("📢 Qual é o nome exato do grupo para enviar a mensagem? ")

    # Mensagem sem emojis
    mensagem = "Olá, este é um teste de automação com Firefox."

    enviar_mensagem(driver, grupo_nome, mensagem)
