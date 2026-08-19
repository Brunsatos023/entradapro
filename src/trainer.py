from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score
)


ARQUIVO_DATASET = Path(
    "data/processed/"
    "brasileirao_features_pre_jogo_2024.csv"
)

ARQUIVO_MODELO = Path(
    "models/"
    "footballai_over15.pkl"
)

FEATURES = [
    "casa_media_gols_marcados_5",
    "casa_media_gols_sofridos_5",
    "casa_media_pontos_5",
    "casa_percentual_over15_5",
    "casa_percentual_btts_5",
    "fora_media_gols_marcados_5",
    "fora_media_gols_sofridos_5",
    "fora_media_pontos_5",
    "fora_percentual_over15_5",
    "fora_percentual_btts_5"
]

TARGET = "target_over15"


def treinar_modelo():
    if not ARQUIVO_DATASET.exists():
        print("Dataset não encontrado:")
        print(ARQUIVO_DATASET)
        return

    dados = pd.read_csv(
        ARQUIVO_DATASET,
        parse_dates=["data"]
    )

    dados = dados.sort_values("data").reset_index(drop=True)

    ponto_corte = int(len(dados) * 0.80)

    treino = dados.iloc[:ponto_corte]
    teste = dados.iloc[ponto_corte:]

    X_train = treino[FEATURES]
    y_train = treino[TARGET]

    X_test = teste[FEATURES]
    y_test = teste[TARGET]

    modelo = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42
    )

    modelo.fit(X_train, y_train)

    previsoes = modelo.predict(X_test)
    probabilidades = modelo.predict_proba(X_test)[:, 1]

    acuracia = accuracy_score(
        y_test,
        previsoes
    )

    brier = brier_score_loss(
        y_test,
        probabilidades
    )

    if len(y_test.unique()) == 2:
        roc_auc = roc_auc_score(
            y_test,
            probabilidades
        )
    else:
        roc_auc = None

    ARQUIVO_MODELO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "modelo": modelo,
            "features": FEATURES,
            "target": TARGET
        },
        ARQUIVO_MODELO
    )

    print("=" * 60)
    print("FOOTBALLAI — AVALIAÇÃO TEMPORAL")
    print("=" * 60)

    print(f"Partidas de treino: {len(treino)}")
    print(f"Partidas de teste: {len(teste)}")

    print()
    print(f"Acurácia: {acuracia:.2%}")
    print(f"Brier Score: {brier:.4f}")

    if roc_auc is not None:
        print(f"ROC AUC: {roc_auc:.4f}")

    print()
    print("Matriz de confusão:")
    print(confusion_matrix(y_test, previsoes))

    print()
    print("Relatório de classificação:")
    print(
        classification_report(
            y_test,
            previsoes,
            digits=3,
            zero_division=0
        )
    )

    print("Modelo salvo em:")
    print(ARQUIVO_MODELO)


if __name__ == "__main__":
    treinar_modelo()