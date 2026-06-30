-- ============================================================
-- Usuário 1: Arthur (com teto global → mostra budget_status)
-- ============================================================
INSERT INTO users (name, password, budget_ceiling)
VALUES ('Arthur', 'senha123', 4000);

-- receitas (total 7500)
INSERT INTO incomes (name, income_value, user_id) VALUES
('Salário',   6000, (SELECT id FROM users WHERE name='Arthur')),
('Freelance', 1500, (SELECT id FROM users WHERE name='Arthur'));

-- contas fixas (total 1820)  
INSERT INTO bills (name, bill_value, user_id) VALUES
('Aluguel',  1500, (SELECT id FROM users WHERE name='Arthur')),
('Internet',  120, (SELECT id FROM users WHERE name='Arthur')),
('Energia',   200, (SELECT id FROM users WHERE name='Arthur'));

-- despesas (start_month/start_year = junho/2026)
INSERT INTO expenses (name, category, expense_value, installment, start_month, start_year, user_id) VALUES
('Mercado',     'alimentação', 700,   1, 6, 2026, (SELECT id FROM users WHERE name='Arthur')),
('Combustível', 'transporte',  500,   1, 6, 2026, (SELECT id FROM users WHERE name='Arthur')),
('Cinema',      'lazer',       300,   1, 6, 2026, (SELECT id FROM users WHERE name='Arthur')),
('Notebook',    'tecnologia',  3600, 12, 6, 2026, (SELECT id FROM users WHERE name='Arthur')),
('Geladeira',   'casa',        1200,  6, 6, 2026, (SELECT id FROM users WHERE name='Arthur'));

-- investimentos (capital 15000 + dividendos 1100)
INSERT INTO investments (name, value_invested, dividends, user_id) VALUES
('Tesouro Direto', 10000, 800, (SELECT id FROM users WHERE name='Arthur')),
('Ações',           5000, 300, (SELECT id FROM users WHERE name='Arthur'));

-- tetos por categoria (geram OK / WARNING / EXCEEDED)
INSERT INTO category_budgets (category, ceiling, user_id) VALUES
('alimentação', 800, (SELECT id FROM users WHERE name='Arthur')),
('transporte',  400, (SELECT id FROM users WHERE name='Arthur')),
('lazer',       500, (SELECT id FROM users WHERE name='Arthur')),
('tecnologia',  600, (SELECT id FROM users WHERE name='Arthur'));

-- ============================================================
-- Usuário 2: Maria (SEM teto global → summary sem budget_status)
-- ============================================================
INSERT INTO users (name, password, budget_ceiling)
VALUES ('Maria', 'maria123', NULL);

INSERT INTO incomes (name, income_value, user_id) VALUES
('Salário', 4000, (SELECT id FROM users WHERE name='Maria'));

INSERT INTO bills (name, bill_value, user_id) VALUES
('Aluguel', 1000, (SELECT id FROM users WHERE name='Maria'));

INSERT INTO expenses (name, category, expense_value, installment, start_month, start_year, user_id) VALUES
('Farmácia', 'saúde', 200, 1, 6, 2026, (SELECT id FROM users WHERE name='Maria'));