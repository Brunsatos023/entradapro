PLANOS_PRO = {
    "PRO_MENSAL": {
        "nome": "PRO Mensal",
        "periodicidade": "MENSAL",
        "meses": 1,
        "valor": 29.90,
        "descricao": (
            "Acesso completo ao EntradaPro "
            "com cobrança mensal."
        )
    },

    "PRO_TRIMESTRAL": {
        "nome": "PRO Trimestral",
        "periodicidade": "TRIMESTRAL",
        "meses": 3,
        "valor": 74.90,
        "descricao": (
            "Acesso completo ao EntradaPro "
            "por 3 meses."
        )
    },

    "PRO_ANUAL": {
        "nome": "PRO Anual",
        "periodicidade": "ANUAL",
        "meses": 12,
        "valor": 239.90,
        "descricao": (
            "Acesso completo ao EntradaPro "
            "por 12 meses."
        )
    }
}


def listar_planos():
    return PLANOS_PRO.copy()


def obter_plano(
    codigo_plano
):
    return PLANOS_PRO.get(
        codigo_plano
    )


def plano_existe(
    codigo_plano
):
    return (
        codigo_plano
        in PLANOS_PRO
    )


def obter_valor_plano(
    codigo_plano
):
    plano = obter_plano(
        codigo_plano
    )

    if not plano:
        return None

    return plano[
        "valor"
    ]


def obter_periodicidade_plano(
    codigo_plano
):
    plano = obter_plano(
        codigo_plano
    )

    if not plano:
        return None

    return plano[
        "periodicidade"
    ]


def obter_nome_plano(
    codigo_plano
):
    plano = obter_plano(
        codigo_plano
    )

    if not plano:
        return None

    return plano[
        "nome"
    ]


def formatar_valor(
    valor
):
    valor = float(
        valor
    )

    texto = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return (
        f"R$ {texto}"
    )


def obter_resumo_planos():
    resumo = []

    for codigo, plano in (
        PLANOS_PRO.items()
    ):
        resumo.append(
            {
                "codigo": codigo,
                "nome": plano[
                    "nome"
                ],
                "periodicidade": plano[
                    "periodicidade"
                ],
                "meses": plano[
                    "meses"
                ],
                "valor": plano[
                    "valor"
                ],
                "valor_formatado": (
                    formatar_valor(
                        plano[
                            "valor"
                        ]
                    )
                ),
                "descricao": plano[
                    "descricao"
                ]
            }
        )

    return resumo