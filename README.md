# ☁️ Nuvem de Palavras

Aplicação Streamlit que lê um texto — de um arquivo `.txt`, colado na tela ou baixado de uma
página da web —, remove stop words ajustáveis e mostra uma nuvem de palavras interativa mais
as sequências de palavras (n-gramas) mais frequentes.

Projeto educacional: o código é comentado explicando o **porquê** de cada decisão, não só o
que ele faz.

## Como usar

1. Aba **⚙️ Preferências**: escolha a fonte do texto e preencha o formulário dela.
2. Ajuste a lista de stop words se quiser.
3. Clique em **Processar**.
4. Aba **☁️ Palavras**: a nuvem, a tabela de frequências e as sequências mais frequentes.

O texto é processado em memória e não fica salvo em lugar nenhum.

## Fontes disponíveis

| Fonte | O que faz |
| --- | --- |
| 📄 Arquivo .txt | Upload de um arquivo de texto puro (limite de 10 MB). |
| 📝 Colar texto | Cole ou digite direto na tela, sem arquivo. |
| 🌐 Página da web | Baixa a página, confere que é HTML, descarta as tags e usa o texto entre elas. |

Cada fonte é um plugin numa subpasta de `plugins/`. Criar a pasta já faz a opção aparecer na
tela: o contrato está em [plugins/base.py](plugins/base.py) — duas interfaces, `formulario()`
e `obter_corpus()` — e [plugins/colar/](plugins/colar/) é o exemplo mais curto, com ~20 linhas.

## Rodar localmente

```bash
uv venv "C:\envs\venv-nuvem_palavras" --python 3.13
```

```bash
uv pip install --python "C:\envs\venv-nuvem_palavras\Scripts\python.exe" -r requirements.txt
```

Depois disso, duplo clique em `nuvem_palavras.bat` (ele ativa o venv e sobe o app), ou:

```bash
streamlit run app.py
```

## Deploy no Streamlit Community Cloud

O repositório já está pronto: `app.py` na raiz, `requirements.txt` só com as dependências de
execução, e `.streamlit/config.toml` limitando o upload a 10 MB.

1. Publique este repositório no GitHub.
2. Em [share.streamlit.io](https://share.streamlit.io), **Create app** → **Deploy a public
   app from GitHub**.
3. Preencha:
   - **Repository**: `<seu-usuario>/nuvem_palavras`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Advanced settings → Python version**: `3.13`
4. **Deploy**. A primeira build leva alguns minutos (instalação do pandas e do pyarrow).

Não há segredos nem variáveis de ambiente a configurar. Nada no app grava em disco, o que
importa lá: no Community Cloud o filesystem é efêmero e compartilhado entre os visitantes.

## Estrutura

Três camadas, e nenhuma seta volta:

```
app.py                só orquestra: liga as três camadas
config.py             caminhos e limites da tela
stopwords.txt         lista padrão — edite este arquivo à mão

plugins/              DE ONDE o texto vem — conhece o Streamlit
  base.py             o contrato: Corpus, ErroDeFonte, FonteTexto
  registro.py         acha os plugins sozinho, olhando as subpastas
  txt/ colar/ url/    as três fontes

core/                 O QUE é feito com ele — só biblioteca padrão
  vetorizador.py      class Vetorizador: bytes -> segmentos -> tokens -> contagens
  analise.py          o resultado (os Counter completos)
  stopwords.py        leitura e normalização da lista

visual/               COMO ele aparece — Streamlit, ECharts, pandas
  opcoes.py           dicts de configuração do ECharts
  tabelas.py          Counter -> DataFrame (tela e CSV)
  paineis.py          os blocos de tela
```

O núcleo roda sem subir servidor nenhum:

```bash
python -c "from core import Vetorizador; print(Vetorizador.de_texto('Céu azul. Céu azul.').analisar().top(5))"
```
