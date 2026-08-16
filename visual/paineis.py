"""Os blocos de tela, cada um numa função.

Esta é a camada de saída: é aqui que mora o Streamlit da parte de exibição. O
`app.py` só decide a ordem e o layout; cada painel sabe desenhar a si mesmo a
partir de uma `Analise` — e nenhum deles processa texto.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

import streamlit as st
from streamlit_echarts import st_echarts

import config
from core import Analise
from visual import opcoes, tabelas

if TYPE_CHECKING:
    # Só para a anotação: importar de verdade criaria uma seta de `visual` para
    # `plugins`, e as duas camadas não precisam se conhecer. Em tempo de
    # execução, `painel_fontes` só usa `.rotulo`, `.id` e `.formulario()`.
    from plugins.base import FonteTexto


# ---------------------------------------------------------------- preferências
def painel_fontes(fontes: list[FonteTexto]) -> tuple[FonteTexto, Any | None]:
    """Seletor de fonte + o formulário da fonte escolhida.

    Devolve (fonte, pedido). O `pedido` é opaco: veio do plugin e volta para ele
    inalterado no clique em Processar.
    """
    escolhidas = {fonte.id: fonte for fonte in fontes}

    # As `options` são os IDS, nunca as instâncias: o registro cria objetos
    # novos a cada re-execução, e o Streamlit não conseguiria casar a instância
    # guardada no session_state com a nova — a escolha se perderia a cada clique.
    id_escolhido = st.selectbox(
        "De onde vem o texto",
        options=list(escolhidas),
        format_func=lambda id_fonte: escolhidas[id_fonte].rotulo,
        key="fonte_escolhida",
    )

    fonte = escolhidas[id_escolhido]
    # O formulário é desenhado aqui dentro, no contêiner de quem chamou: o
    # plugin emite widgets e não precisa saber nada sobre o layout da página.
    return fonte, fonte.formulario()


def painel_stopwords() -> str:
    """Campo das stop words, com os botões de baixar e restaurar.

    Devolve o texto atual do campo.
    """
    st.caption(
        "Uma por linha (ou separadas por vírgula). A comparação ignora acentos "
        "e maiúsculas: escrever `nao` também remove `não`."
    )
    texto = st.text_area(
        "Termos a ignorar",
        key="stopwords_txt",
        height=300,
        label_visibility="collapsed",
    )

    coluna_baixar, coluna_restaurar = st.columns(2)
    coluna_baixar.download_button(
        "⬇️ Baixar lista",
        data=texto.encode("utf-8"),
        file_name="stopwords.txt",
        mime="text/plain",
        width="stretch",
        help="Salve por cima do `stopwords.txt` do projeto para tornar a lista padrão.",
    )
    coluna_restaurar.button(
        "↩️ Restaurar padrão",
        on_click=_restaurar_stopwords,
        width="stretch",
        help="Relê o `stopwords.txt` e descarta as alterações desta sessão.",
    )
    return texto


def _restaurar_stopwords() -> None:
    """Callback do botão restaurar.

    Precisa ser `on_click`, e não código solto: uma key de widget não pode ser
    atribuída depois que o widget já foi criado nesta execução — o Streamlit
    levanta StreamlitAPIException. O callback roda ANTES da próxima execução
    desenhar o text_area, que é o único momento seguro.
    """
    st.session_state.stopwords_txt = config.carregar_stopwords()


def painel_resumo(analise: Analise | None, nome_corpus: str) -> None:
    """As três métricas do último processamento. Some se ainda não houve nenhum."""
    if analise is None:
        return

    st.divider()
    st.subheader("Resumo do último processamento")
    st.caption(f"Fonte: `{nome_corpus}` · codificação detectada: `{analise.codificacao}`")

    col1, col2, col3 = st.columns(3)
    col1.metric("Palavras no texto", _milhar(analise.total_tokens))
    col2.metric("Após as stop words", _milhar(analise.total_filtrados))
    col3.metric("Palavras distintas", _milhar(analise.palavras_distintas))


def _milhar(numero: int) -> str:
    """12345 -> '12.345' (o separador brasileiro)."""
    return f"{numero:,}".replace(",", ".")


# --------------------------------------------------------------------- palavras
def painel_nuvem(analise: Analise) -> None:
    """A nuvem e, logo abaixo, a tabela que está por trás dela."""
    st.subheader("Nuvem de palavras")
    quantidade = st.slider(
        "Palavras exibidas",
        min_value=0,
        max_value=config.MAX_PALAVRAS,
        value=config.PADRAO_PALAVRAS,
        step=5,
        key="slider_palavras",
    )

    if quantidade == 0:
        st.warning("Slider em 0 — aumente para desenhar a nuvem.")
        return

    st_echarts(
        opcoes.opcoes_nuvem(analise.top(quantidade)),
        height="520px",
        key="grafico_nuvem",
    )
    st.caption(
        "Passe o mouse sobre uma palavra para ver a contagem. O ícone no canto "
        "superior direito baixa a imagem em PNG."
    )

    bloco_tabela(
        analise.frequencias,
        quantidade,
        "palavra",
        f"📋 Tabela das {quantidade} palavras exibidas",
        "frequencias",
    )


def painel_sequencias(analise: Analise, n_minimo: int, n_maximo: int) -> None:
    """As sequências de N palavras mais frequentes, em barras horizontais."""
    st.subheader("Sequências mais frequentes")
    st.caption(
        "As stop words saem **antes** das sequências serem formadas, então "
        "“casa de praia” aparece como o par `casa praia`. É o que faz expressões "
        "emergirem em vez de “de a”, “que o”."
    )

    col_n, col_qtd = st.columns(2)
    n = col_n.slider(
        "Palavras por sequência",
        min_value=n_minimo,
        max_value=n_maximo,
        value=n_minimo,
        key="slider_n",
    )
    quantidade = col_qtd.slider(
        "Sequências exibidas",
        min_value=5,
        max_value=config.MAX_SEQUENCIAS,
        value=config.PADRAO_SEQUENCIAS,
        step=5,
        key="slider_sequencias",
    )

    contagens = analise.ngramas.get(n, Counter())
    if not contagens:
        st.info(f"Nenhum segmento do texto tem {n} palavras seguidas após o filtro.")
        return
    if max(contagens.values()) == 1:
        st.warning(
            f"Nenhuma sequência de {n} palavras se repete neste texto — todas "
            "aparecem uma única vez. Tente um agrupamento menor."
        )
        return

    itens = analise.top_sequencias(n, quantidade)
    st_echarts(
        opcoes.opcoes_barras(itens, f"sequencias_{n}_palavras"),
        # Altura proporcional ao número de barras: com poucas, um gráfico de
        # 520px deixaria cada barra gorda demais.
        height=f"{max(320, 28 * len(itens))}px",
        key="grafico_ngramas",
    )
    bloco_tabela(
        contagens,
        quantidade,
        f"sequência ({n} palavras)",
        f"📋 Tabela das {quantidade} sequências exibidas",
        f"sequencias_{n}",
    )


def bloco_tabela(
    contagens: Counter[str], quantidade: int, rotulo: str, titulo: str, chave: str
) -> None:
    """Expander com a tabela de contagens e o botão de download em CSV."""
    with st.expander(titulo, expanded=False):
        df = tabelas.montar(contagens, quantidade, rotulo)
        st.dataframe(df, hide_index=True, width="stretch")
        st.download_button(
            "Baixar CSV",
            # utf-8-sig (com BOM) é o que faz o Excel no Windows abrir os
            # acentos corretamente em vez de exibir "Ã§Ã£o".
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{chave}.csv",
            mime="text/csv",
            key=f"download_{chave}",
        )
