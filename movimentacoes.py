from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

bp = Blueprint('movimentos', __name__, url_prefix='/movimentacoes')
TIPOS = {'entrada': 'Entrada', 'saida': 'Saída'}


def registrar_rotas(app, conectar, listar_materiais):
    @bp.get('/')
    def lista():
        itens = listar_materiais()
        ids = {str(item['id']) for item in itens}
        material = request.args.get('material', '')
        if material and material not in ids:
            abort(400)
        movimentos = conectar().execute(
            '''
            SELECT v.id, v.material_id, v.tipo, v.quantidade, v.criado_em, m.nome, m.unidade
            FROM movimentacoes AS v
            JOIN materiais AS m ON m.id = v.material_id
            WHERE (? = '' OR v.material_id = ?)
            ORDER BY v.criado_em DESC, v.id DESC
            ''',
            (material, material),
        ).fetchall()
        return render_template(
            'movimentacoes.html', itens=itens, movimentos=movimentos,
            material=material, tipos=TIPOS,
        )

    @bp.post('/')
    @bp.post('/<int:id>/editar')
    @bp.post('/<int:id>/excluir', defaults={'excluir': True})
    def salvar(id=None, excluir=False):
        banco = conectar()
        novo = None
        if not excluir:
            novo = ler_formulario()
            if novo is None:
                flash('Selecione um material, um tipo e uma quantidade inteira positiva.', 'erro')
                return redirect(url_for('movimentos.lista'), code=303)

        with banco:
            # A validação do saldo e a gravação compartilham uma transação.
            banco.execute('BEGIN IMMEDIATE')
            antigo = None
            if id is not None:
                antigo = banco.execute(
                    'SELECT material_id, tipo, quantidade FROM movimentacoes WHERE id = ?', (id,)
                ).fetchone()
                if antigo is None:
                    abort(404)

            ajustes = {}
            if antigo is not None:
                material_id, tipo, quantidade = antigo
                ajustes[material_id] = -efeito(tipo, quantidade)
            if novo is not None:
                material_id, tipo, quantidade = novo
                ajustes[material_id] = ajustes.get(material_id, 0) + efeito(tipo, quantidade)

            for material_id, ajuste in ajustes.items():
                if banco.execute('SELECT 1 FROM materiais WHERE id = ?', (material_id,)).fetchone() is None:
                    flash('O material selecionado não existe.', 'erro')
                    return redirect(url_for('movimentos.lista'), code=303)
                saldo = banco.execute(
                    '''
                    SELECT COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN quantidade ELSE -quantidade END), 0)
                    FROM movimentacoes WHERE material_id = ?
                    ''',
                    (material_id,),
                ).fetchone()[0]
                if saldo + ajuste < 0:
                    flash('Saldo insuficiente. A movimentação não foi alterada.', 'erro')
                    return redirect(url_for('movimentos.lista'), code=303)

            if excluir:
                banco.execute('DELETE FROM movimentacoes WHERE id = ?', (id,))
            elif id is None:
                banco.execute(
                    'INSERT INTO movimentacoes (material_id, tipo, quantidade) VALUES (?, ?, ?)', novo
                )
            else:
                banco.execute(
                    'UPDATE movimentacoes SET material_id = ?, tipo = ?, quantidade = ? WHERE id = ?',
                    (*novo, id),
                )

        flash('Movimentação excluída.' if excluir else 'Movimentação salva.', 'sucesso')
        return redirect(url_for('movimentos.lista'), code=303)

    app.register_blueprint(bp)


def ler_formulario():
    try:
        material_id = int(request.form.get('material_id', ''))
        quantidade = int(request.form.get('quantidade', ''))
    except ValueError:
        return None
    tipo = request.form.get('tipo', '')
    if not (1 <= material_id <= 2**63 - 1 and 1 <= quantidade <= 1_000_000 and tipo in TIPOS):
        return None
    return material_id, tipo, quantidade


def efeito(tipo, quantidade):
    return quantidade if tipo == 'entrada' else -quantidade
