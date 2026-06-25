import pytest
from services.financial_service import check_budget_alert

# MC/DC — duas condições independentes:
#   C1: ratio >= 1.0  →  EXCEEDED
#   C2: ratio > 0.8   →  WARNING  (só alcançada se C1 for False)
#
# Pares que demonstram independência de cada condição:
#   C1: (ratio=0.9 → WARNING)  vs  (ratio=1.0 → EXCEEDED)   — só C1 muda, outcome muda
#   C2: (ratio=0.8 → OK)       vs  (ratio=0.9 → WARNING)    — só C2 muda, outcome muda


class TestCheckBudgetAlert:
    # --- MC/DC: C1 True ---

    def test_exactly_at_ceiling_exceeded(self):
        assert check_budget_alert(1000, 1000) == "EXCEEDED"

    def test_above_ceiling_exceeded(self):
        assert check_budget_alert(1500, 1000) == "EXCEEDED"

    # --- MC/DC: C1 False, C2 True ---

    def test_just_above_80_percent_warning(self):
        assert check_budget_alert(801, 1000) == "WARNING"

    def test_99_percent_warning(self):
        assert check_budget_alert(990, 1000) == "WARNING"

    # --- MC/DC: C1 False, C2 False ---

    def test_below_80_percent_ok(self):
        assert check_budget_alert(500, 1000) == "OK"

    def test_zero_spending_ok(self):
        assert check_budget_alert(0, 1000) == "OK"

    # --- fronteiras exatas (boundary analysis) ---

    def test_boundary_exactly_80_percent_is_ok(self):
        # 800/1000 = 0.80 — NOT > 0.8, então OK
        assert check_budget_alert(800, 1000) == "OK"

    def test_boundary_just_below_80_ok(self):
        assert check_budget_alert(799, 1000) == "OK"

    def test_boundary_just_below_ceiling_warning(self):
        assert check_budget_alert(999, 1000) == "WARNING"

    # --- par MC/DC para C1 (muda só C1, C2 constante True) ---

    def test_mcdcc1_c1_false_c2_true_warning(self):
        assert check_budget_alert(900, 1000) == "WARNING"   # ratio=0.9

    def test_mcdcc1_c1_true_exceeded(self):
        assert check_budget_alert(1000, 1000) == "EXCEEDED"  # ratio=1.0

    # --- par MC/DC para C2 (C1 sempre False) ---

    def test_mcdcc2_c2_false_ok(self):
        assert check_budget_alert(800, 1000) == "OK"   # ratio=0.80

    def test_mcdcc2_c2_true_warning(self):
        assert check_budget_alert(900, 1000) == "WARNING"  # ratio=0.90

    # --- entradas inválidas ---

    def test_zero_ceiling_raises(self):
        with pytest.raises(ValueError, match="Budget ceiling must be greater than zero"):
            check_budget_alert(500, 0)

    def test_negative_ceiling_raises(self):
        with pytest.raises(ValueError, match="Budget ceiling must be greater than zero"):
            check_budget_alert(500, -100)

    def test_negative_total_raises(self):
        with pytest.raises(ValueError, match="Category total cannot be negative"):
            check_budget_alert(-1, 1000)
