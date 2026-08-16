"""Nuvem de Palavras — MVP.

Este arquivo só orquestra. Ele é o único que conhece as três camadas, e o que
faz é ligar uma na outra:

    plugins  ──►  bytes  ──►  core  ──►  Analise  ──►  visual

Nenhuma regra de negócio mora aqui: quem sabe ler a fonte é o plugin, quem sabe
contar palavras é o `core`, quem sabe desenhar é o `visual`.

O processamento acontece UMA vez, no clique em "Processar". Os sliders da aba
Palavras apenas refatiam o resultado já em memória.
"""

from __future__ import annotations

import streamlit as st

import config
from core import N_MINIMO, Analise, Vetorizador
from core import stopwords as sw
from plugins import registro
from plugins.base import ErroDeFonte
from visual import paineis

st.set_page_config(page_title="Nuvem de Palavras", page_icon="☁️", layout="wide")


@st.cache_data(show_spinner="Processando o texto…", max_entries=3, ttl=3600)
def analisar_em_cache(
    dados: bytes, stopwords: tuple[str, ...], tamanho_minimo: int, n_maximo: int
) -> Analise:
    """Wrapper fino sobre o núcleo, só para ganhar o cache do Streamlit.

    Ele mora AQUI, e não dentro de `core/`, porque é o decorador que amarraria o
    núcleo ao Streamlit — e o núcleo é justamente a camada que não pode conhecer
    a tela.

    Todos os argumentos são hasheáveis (bytes, tupla, int), que é o que o cache
    exige. `max_entries` e `ttl` existem por causa do deploy: o cache é
    compartilhado por todas as sessões e no Community Cloud a memória é pouca —
    sem teto, cada texto novo enviado por qualquer visitante ficaria guardado.
    """
    return Vetorizador(dados).analisar(stopwords, tamanho_minimo, n_maximo)


# `setdefault` roda antes dos widgets: o campo de stop words nasce preenchido e,
# a partir daí, é o próprio widget que mantém a chave no session_state.
st.session_state.setdefault("stopwords_txt", config.carregar_stopwords())
st.session_state.setdefault("analise", None)
st.session_state.setdefault("corpus_nome", "")


st.title("☁️ Nuvem de Palavras")

aba_preferencias, aba_palavras = st.tabs(["⚙️ Preferências", "☁️ Palavras"])


with aba_preferencias:
    coluna_fonte, coluna_limpeza = st.columns(2, gap="large")

    with coluna_fonte:
        st.subheader("1. Fontes")
        fonte, pedido = paineis.painel_fontes(registro.fontes())

        st.subheader("3. Parâmetros")
        tamanho_minimo = st.number_input(
            "Tamanho mínimo da palavra",
            min_value=1,
            max_value=10,
            value=config.TAMANHO_MINIMO_PADRAO,
            help="Descarta tokens mais curtos que isso, antes das stop words.",
        )

        processar = st.button(
            "Processar", type="primary", width="stretch", disabled=pedido is None
        )
        if pedido is None:
            st.caption("Preencha o formulário da fonte para habilitar o processamento.")

    with coluna_limpeza:
        st.subheader("2. Stop words")
        texto_stopwords = paineis.painel_stopwords()

    if processar and pedido is not None:
        try:
            corpus = fonte.obter_corpus(pedido)
        except ErroDeFonte as erro:
            # Só ErroDeFonte é tratado: é a falha que o plugin PREVIU e traduziu
            # para o usuário. Qualquer outra exceção é bug, e bug tem que
            # aparecer inteiro em vez de virar uma mensagem simpática.
            st.error(str(erro))
        else:
            st.session_state.analise = analisar_em_cache(
                corpus.dados,
                tuple(sw.ler(texto_stopwords)),
                int(tamanho_minimo),
                config.N_MAXIMO_UI,
            )
            st.session_state.corpus_nome = corpus.nome

    paineis.painel_resumo(st.session_state.analise, st.session_state.corpus_nome)


with aba_palavras:
    analise = st.session_state.analise

    if analise is None:
        st.info(
            "Vá até **⚙️ Preferências**, escolha uma fonte, ajuste as stop words "
            "se quiser e clique em **Processar**."
        )
    elif analise.vazia:
        st.warning(
            "Nenhuma palavra sobrou depois do filtro. Reduza o tamanho mínimo ou "
            "remova stop words da lista."
        )
    else:
        paineis.painel_nuvem(analise)
        st.divider()
        paineis.painel_sequencias(analise, N_MINIMO, config.N_MAXIMO_UI)
