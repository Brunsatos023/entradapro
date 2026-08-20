"""
Envio de e-mails do EntradaPro (recuperação de senha, etc.) via
SMTP do Gmail — gratuito, usando uma "Senha de app" do Google
(diferente da senha normal da conta).

COMO CONFIGURAR (uma vez só):

1. Ative a verificação em duas etapas na conta Google que vai
   enviar os e-mails (myaccount.google.com/security).
2. Gere uma "Senha de app" em
   myaccount.google.com/apppasswords (escolha "Outro" e dê um
   nome tipo "EntradaPro").
3. No .env, preencha:
       SMTP_EMAIL=seuemail@gmail.com
       SMTP_APP_PASSWORD=a senha de 16 letras gerada no passo 2

Se essas variáveis não estiverem configuradas, o envio falha de
forma segura (retorna erro claro) - o EntradaPro NUNCA volta a
mostrar o código na tela como alternativa, isso seria a mesma
falha de segurança que este módulo veio resolver.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SERVIDOR_SMTP = "smtp.gmail.com"
PORTA_SMTP = 587


def _credenciais_configuradas():
    return bool(
        os.getenv("SMTP_EMAIL") and os.getenv("SMTP_APP_PASSWORD")
    )


def enviar_email_recuperacao(email_destino, codigo):
    """
    Envia o código de recuperação de senha por e-mail de verdade.

    Retorna (True, "") em caso de sucesso, ou
    (False, "mensagem de erro") em caso de falha - nunca lança
    exceção, e nunca expõe o código como alternativa ao e-mail.
    """
    if not _credenciais_configuradas():
        return False, (
            "Envio de e-mail não configurado. "
            "Configure SMTP_EMAIL e SMTP_APP_PASSWORD no .env."
        )

    remetente = os.getenv("SMTP_EMAIL")
    senha_app = os.getenv("SMTP_APP_PASSWORD")

    mensagem = MIMEMultipart("alternative")
    mensagem["Subject"] = "Seu código de recuperação — EntradaPro"
    mensagem["From"] = f"EntradaPro <{remetente}>"
    mensagem["To"] = email_destino

    corpo_texto = (
        f"Seu código de recuperação de senha do EntradaPro é: "
        f"{codigo}\n\n"
        "Este código expira em 15 minutos. Se você não pediu "
        "essa recuperação, pode ignorar este e-mail com segurança."
    )

    corpo_html = f"""
    <div style="font-family: sans-serif; max-width: 480px;">
        <h2>EntradaPro</h2>
        <p>Seu código de recuperação de senha é:</p>
        <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">
            {codigo}
        </p>
        <p>Este código expira em 15 minutos.</p>
        <p style="color: #666; font-size: 13px;">
            Se você não pediu essa recuperação, pode ignorar este
            e-mail com segurança.
        </p>
    </div>
    """

    mensagem.attach(MIMEText(corpo_texto, "plain"))
    mensagem.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP(SERVIDOR_SMTP, PORTA_SMTP, timeout=15) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha_app)
            servidor.sendmail(
                remetente, email_destino, mensagem.as_string()
            )
        return True, ""
    except Exception as erro:
        return False, f"Não foi possível enviar o e-mail: {erro}"
