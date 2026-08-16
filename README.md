# ☁️ Nuvem de Palavras

Um app que lê um texto, joga fora as palavras sem graça ("de", "que", "para"…) e mostra quais
palavras mais aparecem — numa nuvem colorida e num gráfico de expressões.

**Projeto Integrador II — UNIVESP.** É um MVP: funciona, faz o que promete, e tem um monte de
coisa que dava pra melhorar. A ideia era sair de uma pergunta simples ("sobre o que esse texto
fala, afinal?") e chegar num app que qualquer pessoa consegue usar sem instalar nada.

## O que ele faz

- Você dá um texto pra ele — um arquivo `.txt`, um texto colado, ou o endereço de uma página
  da web.
- Ele separa as palavras, descarta as que você mandou ignorar e conta o resto.
- Mostra a **nuvem de palavras** (passe o mouse pra ver quantas vezes cada uma apareceu).
- Mostra a **tabela** por trás da nuvem, que dá pra baixar em CSV e abrir no Excel.
- Mostra as **expressões mais repetidas** — pares, trios, até 10 palavras seguidas. É isso que
  faz aparecer "mobilidade urbana" em vez de só "mobilidade".

## Rodando na sua máquina

Você vai precisar do **Python** instalado ([python.org/downloads](https://www.python.org/downloads/)).
Testamos no **3.13** e no **3.14** — pode baixar a versão mais recente sem medo. Reserve uns
350 MB de espaço, que é o tamanho das bibliotecas.

> No Windows, na hora de instalar o Python, **marque a caixinha "Add Python to PATH"**. Sem
> isso os comandos abaixo não são encontrados e você vai penar.

### 1. Baixe o código

```bash
git clone https://github.com/RamiltonLima/nuvem_palavras.git
```

```bash
cd nuvem_palavras
```

Se você não usa git, dá pra clicar em **Code → Download ZIP** na página do GitHub e descompactar.

### 2. Crie o ambiente virtual

É uma pastinha que guarda as bibliotecas só deste projeto, pra não bagunçar o Python da sua
máquina.

**Windows:**

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

**macOS ou Linux:**

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Deu certo se aparecer `(.venv)` no começo da linha do terminal.

### 3. Instale as bibliotecas

```bash
pip install -r requirements.txt
```

Demora alguns minutos na primeira vez (o pandas é grandinho).

### 4. Rode

```bash
streamlit run app.py
```

O navegador abre sozinho em `http://localhost:8501`. Se não abrir, é só colar esse endereço
na barra.

Pra parar, volte no terminal e aperte `Ctrl+C`.

### Deu errado?

| O que apareceu | O que fazer |
| --- | --- |
| `python não é reconhecido...` | O Python não está no PATH. No Windows, reinstale marcando "Add Python to PATH", ou tente `py` no lugar de `python`. |
| `streamlit não é reconhecido...` | Você provavelmente esqueceu de ativar o ambiente virtual (passo 2) ou de instalar (passo 3). |
| Erro no `pip install` | Rode `python -m pip install --upgrade pip` e tente de novo. |
| `.venv\Scripts\activate` barrado no PowerShell | O Windows bloqueia scripts por padrão. Rode `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` na mesma janela e ative de novo. |
| A porta 8501 já está em uso | `streamlit run app.py --server.port 8502` |

Toda vez que for mexer no projeto de novo, é só ativar o ambiente (passo 2) e rodar (passo 4)
— os passos 1 e 3 são só na primeira vez.

## Como usar o app

1. Aba **⚙️ Preferências**: escolha de onde vem o texto e preencha o campo que aparecer.
2. Se quiser, mexa na lista de **stop words** (as palavras que serão ignoradas). Ela já vem
   preenchida com 170 palavras comuns do português.
3. Clique em **Processar**.
4. Vá pra aba **☁️ Palavras** e brinque com os controles.

O texto é processado na memória e não fica salvo em lugar nenhum.

### As três fontes de texto

| Fonte | O que é |
| --- | --- |
| 📄 Arquivo .txt | Você envia um arquivo de texto (até 10 MB). |
| 📝 Colar texto | Cola direto na tela, sem precisar de arquivo. |
| 🌐 Página da web | Você dá o endereço, o app baixa a página e tira as tags do HTML. |

Um aviso sobre a fonte de página web: ela pega **todo** o texto visível da página, incluindo
menu e rodapé. Se a nuvem vier cheia de palavra de navegação, jogue essas palavras na lista de
stop words.

## Como o código está organizado

Três pastas, cada uma com um trabalho só:

```
plugins/    DE ONDE o texto vem (as três fontes acima)
core/       O QUE é feito com ele (separar palavras, contar)
visual/     COMO ele aparece na tela (os gráficos e as tabelas)

app.py      junta as três — e só isso
config.py   os limites e os caminhos
stopwords.txt   a lista de palavras ignoradas (dá pra editar no bloco de notas)
```

A regra é que uma pasta não enxerga a outra sem necessidade: o `core/` não sabe que Streamlit
existe, e os plugins não sabem nada sobre os gráficos. Foi o que permitiu acrescentar a fonte
de página web sem encostar em nenhuma outra parte.

Pra ver isso na prática, a parte que conta as palavras roda sem abrir o app:

```bash
python -c "from core import Vetorizador; print(Vetorizador.de_texto('Céu azul. Céu azul.').analisar().top(5))"
```

### Quer criar uma fonte nova?

Tipo PDF, ou puxar de uma planilha. É criar uma pasta dentro de `plugins/` com dois arquivos —
o app acha sozinho e a opção aparece na tela. O molde está em `plugins/base.py`, e
`plugins/colar/` é o exemplo mais curto, com umas 20 linhas.

## Colocando no ar

O app está preparado pro [Streamlit Community Cloud](https://share.streamlit.io), que hospeda
de graça: **Create app** → **Deploy from GitHub** → repositório `RamiltonLima/nuvem_palavras`,
branch `main`, arquivo `app.py`, Python `3.13`. A primeira build demora alguns minutos.

Não tem senha nem chave de API pra configurar.

## O que ficou de fora

Coisas que a gente sabe que faltam, caso alguém queira continuar:

- `casa` e `casas` são contadas como palavras diferentes (faltou stemming).
- Só dá pra usar uma fonte por vez.
- Não lê PDF nem Word.
- Página feita em JavaScript vem vazia — o app avisa e sugere colar o texto.
- As cores e o formato da nuvem são fixos.
