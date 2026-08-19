"""
Página "Assinatura PRO" — conecta o assinatura.py (que já existia,
mas nunca estava ligado a lugar nenhum do site) ao menu de páginas
do Streamlit, para que o usuário consiga realmente chegar até ela.
"""

import sys
from pathlib import Path

# Garante que os módulos de src/ (assinatura, auth, etc.) sejam
# encontrados quando o Streamlit executa esta página separadamente.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assinatura import main  # noqa: E402

main()
