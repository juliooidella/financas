# Automação Nota Paraná

Este projeto utiliza Python e Playwright para automatizar o download de dados de notas fiscais do portal Nota Paraná.

## Pré-requisitos

- Python 3.x
- `uv` (Gerenciador de pacotes)

## Instalação

As dependências já foram adicionadas ao projeto. Para garantir que tudo esteja instalado, execute:

```bash
uv sync
```

Instale os navegadores do Playwright:

```bash
uv run playwright install chromium
```

## Como usar

1. Execute o script de extração:

```bash
uv run extract_notes.py
```

2. Uma janela do navegador Chromium será aberta.
3. Faça o **Login** no portal Nota Paraná manualmente.
4. Navegue até a aba **Minhas Notas** ou a seção onde a lista de notas é exibida.
5. Selecione o mês desejado para carregar a lista de notas na tela.
6. Volte ao terminal e pressione **ENTER**.
7. O script irá capturar todos os links visíveis e baixar os detalhes de cada nota (Estabelecimento, Data, Itens, Valores).
8. Ao final, um arquivo `notas_parana_extraidas.csv` será gerado.

## Estrutura

- `extract_notes.py`: Script principal.
- `htmls/`: Pasta contendo exemplos de HTML (usados para referência no desenvolvimento).
