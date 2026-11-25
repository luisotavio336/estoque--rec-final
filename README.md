# Estoque em Dia

Controle de materiais para o almoxarifado de uma clínica fictícia. O sistema
cadastra e busca itens, registra entradas e saídas e calcula o saldo disponível
de cada material. Use registros fictícios na demonstração pública.

## Executar no VS Code

Abra a pasta com o `app.py`. No terminal do Windows, com Python 3.10 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

Abra http://127.0.0.1:5000. O SQLite é criado em
`instance/estoque.sqlite3`. A variável `ESTOQUE_DB` pode indicar outro caminho.

## Telas e API

| Endereço | Função |
| --- | --- |
| `/` | Cadastrar, editar, excluir e pesquisar materiais. Exibe o saldo. |
| `/movimentacoes/` | Registrar, editar, excluir e filtrar entradas e saídas por material. |
| `/api/materiais` | Retorna uma lista JSON com `id`, `nome`, `unidade` e `saldo`. |

A busca usa Python e `casefold()`. Cada movimentação referencia um material
pela chave estrangeira `material_id`. A listagem do histórico usa `JOIN` para
mostrar o nome, `WHERE` para filtrar e `ORDER BY` para ordenar. O saldo é a soma
das entradas menos a soma das saídas. A gravação e a verificação do saldo
ocorrem dentro da mesma transação SQLite. A edição considera o efeito da
movimentação antiga e da nova, inclusive se trocar de material.

## Demonstração

1. Cadastre `Luvas` com unidade `Caixa` e pesquise `luv`.
2. Registre uma entrada de 20 e uma saída de 5. O saldo deve ser 15.
3. Tente registrar uma nova saída de 16. O sistema deve rejeitar a operação.
4. Edite a saída de 5 para 3. O saldo deve passar para 17.
5. Abra `/api/materiais` e confira se o JSON mostra o mesmo saldo.

## Render

Crie um **Web Service** com runtime Python, branch `main` e raiz do repositório.

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --no-control-socket --bind 0.0.0.0:$PORT app:app`
- Variável de ambiente: configure `SECRET_KEY` com um valor aleatório.
- Após o deploy, teste `/`, `/movimentacoes/` e `/api/materiais`.

O arquivo SQLite pode ser reiniciado com o serviço quando o armazenamento é
temporário. Use um disco persistente e configure `ESTOQUE_DB` dentro dele se
precisar manter os registros. Compare os arquivos de publicação com os
modelos da atividade na Geekie.
