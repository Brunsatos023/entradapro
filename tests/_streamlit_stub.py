"""
Auxiliar de testes: cria um "streamlit falso" (stub) para que módulos
como auth.py, access_control.py e admin_users.py possam ser importados
e testados sem precisar do streamlit de verdade instalado, e sem abrir
navegador nenhum.

Importe isto ANTES de importar qualquer módulo de src/ que use
`import streamlit as st`.
"""

import sys
import types


class _ChamadaFalsa:
    """
    Objeto que se comporta tanto como uma função comum do streamlit
    (st.button(...), st.success(...)) quanto como decorador
    (@st.dialog(...), @st.cache_data).
    """

    def __call__(self, *args, **kwargs):
        def decorador_ou_valor(f=None):
            if callable(f):
                return f
            return _ChamadaFalsa()
        return decorador_ou_valor


class _StreamlitFalso(types.ModuleType):
    def __getattr__(self, nome):
        return _ChamadaFalsa()


def instalar_streamlit_falso():
    """
    Registra o streamlit falso em sys.modules. Chame uma vez no topo
    do arquivo de teste, antes de importar módulos do projeto.
    Retorna o módulo falso (útil para inspecionar st.session_state).
    """
    if isinstance(sys.modules.get("streamlit"), _StreamlitFalso):
        return sys.modules["streamlit"]

    falso = _StreamlitFalso("streamlit")
    falso.session_state = {}
    sys.modules["streamlit"] = falso
    return falso
