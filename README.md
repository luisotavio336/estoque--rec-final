# Estoque em Dia

Base de um sistema para acompanhar o estoque de materiais de uma clínica fictícia.
A versão inicial cria o SQLite e exibe a lista de materiais com Flask e Jinja2.

## Executar no VS Code

Abra a pasta que contém o `app.py`. No terminal do Windows, com Python 3.10 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

Abra http://127.0.0.1:5000. A lista começa vazia.

## Etapas para implementar

1. **Materiais**. Adicione um formulário com nome e unidade. Implemente cadastro,
   edição e exclusão, além da listagem existente. No servidor, valide campos
   vazios, use parâmetros `?` nas consultas e grave com `with banco:`.
   Exiba uma mensagem se uma movimentação impedir excluir um material.
2. **Busca em Python**. Crie uma função que receba a lista e o trecho pesquisado.
   Percorra a lista com `for`, compare com `if` e use `casefold()` para ignorar
   diferenças entre letras maiúsculas e minúsculas. Ligue a função a um formulário GET.
3. **Movimentações**. Crie a segunda tela e coloque um menu nas duas páginas.
   Implemente cadastro, listagem, edição e exclusão de entradas e saídas.
   Use `JOIN` para mostrar o nome do material, `WHERE` nos filtros e `ORDER BY`
   para ordenar por data. Calcule o saldo somando entradas e subtraindo saídas.
   Verifique o saldo antes de salvar ou excluir uma movimentação. Ao editar,
   calcule o efeito no saldo com o valor antigo removido antes de aplicar o novo.
   Faça a validação e a gravação na mesma transação.
4. **API**. Crie `GET /api/materiais` e retorne uma lista JSON. As linhas de
   `sqlite3.Row` podem ser convertidas para dicionários antes de usar `jsonify`.
5. **Revisão e publicação**. Teste o fluxo com dados fictícios e confira as
   duas telas no celular. Use `git init -b main` uma vez e faça commits reais
   ao concluir as etapas. Publique em um GitHub público. No Render, crie um
   Web Service Python, use `pip install -r requirements.txt` no build e
   `gunicorn --no-control-socket --bind 0.0.0.0:$PORT app:app` como comando de início. Compare
   os arquivos de deploy com os modelos da atividade na Geekie.

## Roteiro de demonstração

| Ação | Resultado esperado |
| --- | --- |
| Cadastrar Luvas com unidade Caixa e buscar por “luv” | Luvas aparece na busca |
| Registrar entrada de 20 e saída de 5 | Saldo de 15 caixas |
| Tentar registrar saída de 16 | Operação rejeitada e saldo de 15 |
| Editar a saída de 5 para 3 | Saldo de 17 caixas |
| Abrir `/api/materiais` | A API retorna JSON |

Atualize este README com as rotas, os testes e os links que funcionarem no seu projeto.
