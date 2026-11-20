PRAGMA foreign_keys = ON;

CREATE TABLE unidade (
    codigo TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

INSERT INTO unidade VALUES ('N', 'Norte'), ('S', 'Sul'), ('C', 'Centro');

CREATE TABLE agendamento (
    id INTEGER PRIMARY KEY,
    data_prevista TEXT NOT NULL CHECK (COALESCE(date(data_prevista), '') = data_prevista AND data_prevista <> ''),
    unidade_id TEXT NOT NULL REFERENCES unidade (codigo),
    turno TEXT NOT NULL CHECK (turno IN ('Manha', 'Tarde', 'Noite')),
    lembrete_enviado INTEGER NOT NULL CHECK (lembrete_enviado IN (0, 1)),
    desfecho TEXT NOT NULL CHECK (desfecho IN ('realizado', 'falta', 'cancelado'))
);

CREATE VIEW base_indicadores AS
SELECT
    substr(a.data_prevista, 1, 7) AS mes,
    u.nome AS unidade,
    a.turno,
    CAST(a.desfecho IN ('realizado', 'falta') AS INTEGER) AS elegivel,
    CAST(a.desfecho = 'falta' AS INTEGER) AS falta,
    CAST(a.desfecho = 'cancelado' AS INTEGER) AS cancelado
FROM agendamento AS a
JOIN unidade AS u ON u.codigo = a.unidade_id;

CREATE VIEW resumo AS
SELECT
    COUNT(*) AS marcados,
    COALESCE(SUM(elegivel), 0) AS elegiveis,
    COALESCE(SUM(falta), 0) AS faltas,
    COALESCE(SUM(cancelado), 0) AS cancelados,
    ROUND(100.0 * SUM(falta) / NULLIF(SUM(elegivel), 0), 2) AS taxa_falta_pct
FROM base_indicadores;

CREATE VIEW por_segmento AS
SELECT
    unidade,
    turno,
    COUNT(*) AS marcados,
    SUM(elegivel) AS elegiveis,
    SUM(falta) AS faltas,
    SUM(cancelado) AS cancelados,
    ROUND(100.0 * SUM(falta) / NULLIF(SUM(elegivel), 0), 2) AS taxa_falta_pct
FROM base_indicadores
GROUP BY unidade, turno;

CREATE VIEW por_mes AS
SELECT
    mes,
    COUNT(*) AS marcados,
    SUM(elegivel) AS elegiveis,
    SUM(falta) AS faltas,
    SUM(cancelado) AS cancelados,
    ROUND(100.0 * SUM(falta) / NULLIF(SUM(elegivel), 0), 2) AS taxa_falta_pct
FROM base_indicadores
GROUP BY mes;
