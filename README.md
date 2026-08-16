# ☁️ Nuvem de Palavras

Aplicação web que analisa a frequência de palavras em um texto e apresenta o resultado como
nuvem de palavras, tabela de frequências e gráfico de n-gramas. O texto pode vir de um arquivo
`.txt`, de um campo de digitação ou de uma página da web.

**Projeto Integrador II — UNIVESP.** MVP: funcional, com escopo deliberadamente limitado. As
limitações conhecidas estão listadas no final.

Feito em Python com Streamlit e Apache ECharts.

## Funcionalidades

- Nuvem de palavras interativa, com quantidade de termos ajustável (tooltip com a contagem).
- Tabela de frequências com posição, ocorrências e percentual, exportável em CSV.
- N-gramas de 2 a 10 palavras, que revelam expressões como "mobilidade urbana" em vez de
  termos isolados.
- Lista de stop words editável na interface, com 170 termos do português por padrão.
- Três fontes de texto, implementadas como plugins.

## Requisitos

- Python 3.13 ou 3.14 (versões testadas).
- ~350 MB livres para as dependências.

## Instalação

```bash
git clone https://github.com/RamiltonLima/nuvem_palavras.git
```

```bash
cd nuvem_palavras
```

Ambiente virtual — **Windows**:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

**macOS / Linux**:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Dependências:

```bash
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

O app sobe em `http://localhost:8501`. `Ctrl+C` no terminal encerra. Nas próximas vezes, basta
ativar o ambiente virtual e repetir este comando.

### Problemas comuns

| Erro | Causa e solução |
| --- | --- |
| `python não é reconhecido` | Python fora do PATH. No Windows, reinstale marcando "Add Python to PATH", ou use `py`. |
| `streamlit não é reconhecido` | Ambiente virtual não ativado, ou dependências não instaladas. |
| `activate` bloqueado no PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` na mesma janela. |
| Porta 8501 em uso | `streamlit run app.py --server.port 8502` |

## Uso

1. Aba **⚙️ Preferências**: selecione a fonte e preencha o formulário correspondente.
2. Ajuste a lista de stop words e o tamanho mínimo de palavra, se necessário.
3. **Processar**.
4. Aba **☁️ Palavras**: nuvem, tabela e n-gramas.

O processamento ocorre em memória; nada é gravado em disco.

### Fontes de texto

| Fonte | Descrição |
| --- | --- |
| 📄 Arquivo .txt | Upload de arquivo de texto puro, até 10 MB. |
| 📝 Colar texto | Entrada direta pela interface. |
| 🌐 Página da web | Baixa a URL, valida que a resposta é HTML e extrai o texto entre as tags. |

A fonte de página web extrai todo o texto visível, incluindo menus e rodapés. Termos de
navegação indesejados devem ser adicionados às stop words.

## Estrutura

Três camadas, com dependências em sentido único:

```
plugins/    entrada — as fontes de texto
core/       processamento — tokenização e contagem
visual/     saída — gráficos e tabelas

app.py      orquestração
config.py   caminhos e limites da interface
stopwords.txt   lista padrão, editável em qualquer editor de texto
```

`core/` não importa Streamlit nem pandas, e `plugins/` não conhece `core/` nem `visual/`. Foi
o que permitiu acrescentar a fonte de página web sem alterar as demais camadas.

O núcleo é executável sem servidor:

```bash
python -c "from core import Vetorizador; print(Vetorizador.de_texto('Céu azul. Céu azul.').analisar().top(5))"
```

### Nova fonte de texto

Criar uma subpasta em `plugins/` com dois arquivos — o registro a encontra automaticamente e a
opção passa a aparecer na interface. O contrato está em `plugins/base.py` (duas interfaces:
`formulario()` e `obter_corpus()`); `plugins/colar/` é o exemplo mínimo.

## Deploy

Preparado para o [Streamlit Community Cloud](https://share.streamlit.io): **Create app** →
**Deploy from GitHub** → repositório `RamiltonLima/nuvem_palavras`, branch `main`, arquivo
`app.py`, Python 3.13. Não há segredos nem variáveis de ambiente a configurar.

## Limitações conhecidas

- Sem stemming: `casa` e `casas` são contadas separadamente.
- Uma fonte por processamento.
- Não lê PDF nem DOCX.
- Páginas renderizadas por JavaScript retornam vazias; o app detecta e orienta o uso da
  entrada por texto colado.
- Cores e formato da nuvem são fixos.
