# AI Agents

Este repositório reúne uma coleção de experimentos com agentes de IA em Python, usando modelos da Groq e integração com MySQL. O projeto explora fluxos simples de interação com LLMs para tarefas como:

- geração de consultas SQL a partir de linguagem natural;
- execução e análise de resultados de consultas;
- análise de relatórios de marketing;
- protótipos de agentes conversacionais e de decisão.

## Objetivo

O objetivo principal é servir como base de estudo e prototipagem para agentes inteligentes que recebem instruções, executam ações e retornam respostas em linguagem natural.

## Estrutura do repositório

- base_agent.py: classe base com estrutura comum para agentes, incluindo memória e cliente da API.
- ReAgentSQL.py: agente para conversar com um banco MySQL e responder perguntas em linguagem natural via SQL.
- SQLgenerator.py: exemplo de geração de SQL a partir de uma pergunta em português.
- mktAgent.py: agente voltado para análise de relatórios de marketing.
- insightsAgent.py: protótipo para análise de dados a partir de CSV.
- count_agent.py: exemplo de agente conversacional com um cenário narrativo.
- Agentes2/: pasta com uma segunda versão do projeto, contendo agentes especializados:
  - sqlAgent.py
  - analysisAgent.py
  - decisionAgent.py
  - displayAgent.py
  - prompts/: arquivos com os prompts de cada agente.

## Requisitos

- Python 3.10+
- Dependências listadas em requirements.txt
- Chave de API da Groq
- Banco MySQL configurado, caso você queira usar os agentes SQL

## Instalação

No Windows, em PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Em sistemas baseados em Unix:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```env
GROQ_API_KEY=sua_chave_aqui
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=
DB_PORT=
```

Essas variáveis são carregadas automaticamente pelos scripts com dotenv.

## Como executar

### 1) Agente SQL

```bash
python ReAgentSQL.py
```

### 2) Gerador de SQL

```bash
python SQLgenerator.py
```

### 3) Agente de marketing

```bash
python mktAgent.py
```

### 4) Agente de contagem/conversação

```bash
python count_agent.py
```

## Observações

- Alguns scripts são protótipos experimentais e não foram pensados para uso em produção.
- O fluxo SQL depende de um banco MySQL acessível e de uma estrutura compatível com os nomes de tabelas usados nos prompts.
- A maior parte do projeto é voltada para estudo e demonstração de arquiteturas de agentes com LLMs.

## Próximos passos sugeridos

- padronizar a interface dos agentes;
- adicionar testes automatizados;
- separar a camada de banco de dados em um módulo próprio;
- configurar um fluxo mais robusto de tratamento de erros e logging.

Se quiser, posso também criar uma versão mais elegante do README com badges, exemplos de uso e uma seção de arquitetura.
