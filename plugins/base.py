"""O contrato que toda fonte de texto precisa cumprir.

Este módulo NÃO importa streamlit de propósito: ele descreve o contrato, não
desenha nada. Quem desenha é cada plugin concreto, e aí sim ele importa o que
precisar.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True)
class Corpus:
    """O que um plugin entrega: os bytes crus e de onde eles vieram.

    É `bytes`, e não `str`, por três motivos:
      - é o menor denominador comum — upload, download e leitura de disco já
        chegam assim;
      - concentra a decisão de codificação num lugar só, o `core`, em vez de
        espalhá-la por cada plugin;
      - `bytes` é hasheável, então serve direto como chave do `@st.cache_data`.

    Plugin que já nasce com texto (colar, HTML extraído) faz `.encode("utf-8")`.
    """

    dados: bytes
    nome: str  # rótulo para a tela: "relatorio.txt", "3 arquivos", a própria URL
    origem: str  # id do plugin que produziu — aparece no resumo e ajuda a depurar


class ErroDeFonte(Exception):
    """Falha ESPERADA ao obter o corpus: URL fora do ar, arquivo vazio, não é HTML.

    O app mostra a mensagem direto com `st.error`, então escreva algo que o
    usuário final entenda — não um traceback. Qualquer outra exceção que escapar
    de um plugin é bug, e bug deve aparecer inteiro na tela.
    """


class FonteTexto(ABC):
    """Uma fonte de texto = duas interfaces: um formulário e um corpus.

    ABC, e não Protocol, porque aqui o erro precisa aparecer em tempo de
    execução: sem checador de tipos no projeto, um Protocol deixaria um plugin
    incompleto passar despercebido até alguém clicar. Com ABC, instanciar já
    explode dizendo qual método falta.

    REGRAS para escrever um plugin novo:

    1. **Não guarde estado em `self`.** O registro cria uma instância nova a
       cada re-execução do script; o que o formulário coletou viaja de volta no
       `pedido`, não no objeto.
    2. **Prefixe TODA key de widget com `self.id`** (`key=f"{self.id}_arquivo"`),
       senão dois plugins com um campo de mesmo nome brigam pelo `session_state`.
    3. **Trabalho caro mora em `obter_corpus`, nunca no formulário** — o
       formulário roda a cada clique em qualquer widget da tela.
    """

    id: ClassVar[str]  # slug único; vira o prefixo das keys dos widgets
    nome: ClassVar[str]  # rótulo no seletor de fontes
    icone: ClassVar[str] = "📄"
    descricao: ClassVar[str] = ""

    @property
    def rotulo(self) -> str:
        """Como a fonte aparece no seletor."""
        return f"{self.icone} {self.nome}"

    @abstractmethod
    def formulario(self) -> Any | None:
        """Desenha os widgets e devolve o "pedido" do usuário — ou `None`.

        Roda a CADA re-execução do script, então tem que ser barato: só widgets.
        O valor devolvido é opaco — só o próprio plugin o entende, e ele volta
        inalterado para `obter_corpus`. `None` significa "ainda não dá para
        processar", e é o que mantém o botão Processar desabilitado.
        """

    @abstractmethod
    def obter_corpus(self, pedido: Any) -> Corpus:
        """Transforma o pedido em bytes. Só é chamado no clique em Processar.

        Aqui pode ser caro: ler arquivo, bater na rede, extrair texto de um PDF.
        Em falha previsível, levante `ErroDeFonte` com uma mensagem amigável.
        """
