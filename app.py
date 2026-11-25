import os
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, flash, g, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
PASTA = Path(__file__).resolve().parent
app.config['DATABASE'] = Path(os.environ.get('ESTOQUE_DB') or PASTA / 'instance' / 'estoque.sqlite3')


def conectar():
    if 'banco' not in g:
        caminho = Path(app.config['DATABASE'])
        caminho.parent.mkdir(parents=True, exist_ok=True)
        g.banco = sqlite3.connect(caminho)
        g.banco.row_factory = sqlite3.Row
        g.banco.execute('PRAGMA foreign_keys = ON')
    return g.banco


@app.teardown_appcontext
def fechar_banco(_erro):
    banco = g.pop('banco', None)
    if banco is not None:
        banco.close()


def preparar_banco():
    esquema = (PASTA / 'schema.sql').read_text(encoding='utf-8')
    with app.app_context():
        conectar().executescript(esquema)


def listar_materiais():
    return conectar().execute(
        '''
        SELECT m.id, m.nome, m.unidade,
               COALESCE(SUM(CASE WHEN v.tipo = 'entrada' THEN v.quantidade
                                 ELSE -v.quantidade END), 0) AS saldo
        FROM materiais AS m
        LEFT JOIN movimentacoes AS v ON v.material_id = m.id
        GROUP BY m.id, m.nome, m.unidade
        ORDER BY m.nome COLLATE NOCASE, m.id
        '''
    ).fetchall()


@app.get('/')
def materiais():
    busca = request.args.get('busca', '').strip()
    itens = listar_materiais()
    if busca:
        termo = busca.casefold()
        itens = [
            item for item in itens
            if termo in item['nome'].casefold() or termo in item['unidade'].casefold()
        ]
    return render_template('materiais.html', itens=itens, busca=busca)


@app.post('/materiais')
def adicionar_material():
    nome = request.form.get('nome', '').strip()
    unidade = request.form.get('unidade', '').strip()
    if not (1 <= len(nome) <= 120 and 1 <= len(unidade) <= 40):
        flash('Preencha o nome e a unidade do material.', 'erro')
        return redirect(url_for('materiais'))

    banco = conectar()
    with banco:
        banco.execute(
            'INSERT INTO materiais (nome, unidade) VALUES (?, ?)',
            (nome, unidade),
        )
    flash(f'{nome} foi cadastrado.', 'sucesso')
    return redirect(url_for('materiais'))


@app.post('/materiais/<int:material_id>/editar')
def editar_material(material_id):
    nome = request.form.get('nome', '').strip()
    unidade = request.form.get('unidade', '').strip()
    if not (1 <= len(nome) <= 120 and 1 <= len(unidade) <= 40):
        flash('Preencha o nome e a unidade do material.', 'erro')
        return redirect(url_for('materiais'))

    banco = conectar()
    with banco:
        resultado = banco.execute(
            'UPDATE materiais SET nome = ?, unidade = ? WHERE id = ?',
            (nome, unidade, material_id),
        )
    if resultado.rowcount == 0:
        flash('O material não foi encontrado.', 'erro')
    else:
        flash(f'{nome} foi atualizado.', 'sucesso')
    return redirect(url_for('materiais'))


@app.post('/materiais/<int:material_id>/excluir')
def excluir_material(material_id):
    banco = conectar()
    try:
        with banco:
            resultado = banco.execute(
                'DELETE FROM materiais WHERE id = ?',
                (material_id,),
            )
    except sqlite3.IntegrityError:
        flash('Não é possível excluir um material que possui movimentações.', 'erro')
        return redirect(url_for('materiais'))

    if resultado.rowcount == 0:
        flash('O material não foi encontrado.', 'erro')
    else:
        flash('Material excluído.', 'sucesso')
    return redirect(url_for('materiais'))


preparar_banco()
