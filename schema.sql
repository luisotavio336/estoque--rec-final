CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    unidade TEXT NOT NULL CHECK (length(trim(unidade)) > 0)
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY,
    material_id INTEGER NOT NULL REFERENCES materiais(id) ON DELETE RESTRICT,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
