import pytest
from services.financial_service import check_budget_alert

# =============================================================================
# MC/DC — check_budget_alert
# =============================================================================
#
# Condições atômicas (ratio = category_total / ceiling):
#   C1: ratio >= 1.0
#   C2: ratio > 0.80
#
# Tabela-verdade:
#
#  | # | C1 (ratio >= 1.0) | C2 (ratio > 0.80) | Resultado  |
#  |---|-------------------|-------------------|------------|
#  | 1 |         F         |         F         |     OK     |
#  | 2 |         F         |         T         |  WARNING   |
#  | 3 |         T         |         T         |  EXCEEDED  |
#
#  * C2 não é avaliada quando C1 = T (estrutura if/elif)
#
# Pares MC/DC:
#   Par de C1: caso 2 × caso 3  →  C2 fixo em T, só C1 muda (F→T)  →  WARNING → EXCEEDED
#   Par de C2: caso 1 × caso 2  →  C1 fixo em F, só C2 muda (F→T)  →  OK → WARNING
#
# Conjunto mínimo MC/DC: { 1, 2, 3 }  →  N+1 = 3 testes para N=2 condições
#
# Valores concretos usados nos pares:
#   Caso 1 → C1=F, C2=F  →  OK
#   Caso 2 → C1=F, C2=T  →  WARNING
#   Caso 3 → C1=T, C2=T  →  EXCEEDED
# =============================================================================


class TestCheckBudgetAlert:
    # --- MC/DC: Caso 1 ---

    def test_above_ceiling_exceeded(self):
        assert check_budget_alert(1500, 1000) == "EXCEEDED"

    # --- MC/DC: Caso 2 ---

    def test_99_percent_warning(self):
        assert check_budget_alert(990, 1000) == "WARNING"

    # --- MC/DC: Caso 3 ---

    def test_below_80_percent_ok(self):
        assert check_budget_alert(500, 1000) == "OK"

    # --- fronteiras exatas (boundary analysis) ---
    # 0.799 0.8 0.81 0.999 1 1.1
    def test_boundary_just_below_80_ok(self):
        assert check_budget_alert(799, 1000) == "OK"

    def test_boundary_exactly_80_percent_is_ok(self):
        assert check_budget_alert(800, 1000) == "OK"

    def test_boundary_just_above_80_percent_is_warning(self):
        assert check_budget_alert(801, 1000) == "WARNING"

    def test_boundary_just_below_ceiling_warning(self):
        assert check_budget_alert(999, 1000) == "WARNING"

    def test_exactly_at_ceiling_exceeded(self):
        assert check_budget_alert(1000, 1000) == "EXCEEDED"

    def test_just_above_ceiling_exceeded(self):
        assert check_budget_alert(1001, 1000) == "EXCEEDED"

    # --- entradas inválidas e limite válido ---

    def test_zero_spending_ok(self):
        assert check_budget_alert(0, 1000) == "OK"

    def test_zero_ceiling_raises(self):
        with pytest.raises(ValueError, match="Budget ceiling must be greater than zero"):
            check_budget_alert(500, 0)

    def test_negative_ceiling_raises(self):
        with pytest.raises(ValueError, match="Budget ceiling must be greater than zero"):
            check_budget_alert(500, -100)

    def test_negative_total_raises(self):
        with pytest.raises(ValueError, match="Category total cannot be negative"):
            check_budget_alert(-1, 1000)
