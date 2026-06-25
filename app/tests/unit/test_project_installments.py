import pytest
from services.financial_service import project_installments


class TestProjectInstallments:
    # --- caminho feliz ---

    def test_single_installment(self):
        result = project_installments(300.0, 1, 6, 2025)
        assert len(result) == 1
        assert result[0].amount == 300.0
        assert result[0].month == 6
        assert result[0].year == 2025
        assert result[0].installment_number == 1

    def test_three_installments_same_year(self):
        result = project_installments(900.0, 3, 3, 2025)
        assert [(e.month, e.year) for e in result] == [(3, 2025), (4, 2025), (5, 2025)]
        assert all(e.amount == 300.0 for e in result)

    def test_installment_numbers_are_sequential(self):
        result = project_installments(400.0, 4, 1, 2025)
        assert [e.installment_number for e in result] == [1, 2, 3, 4]

    # --- edge: virada de ano ---

    def test_year_rollover_from_november(self):
        result = project_installments(1200.0, 3, 11, 2025)
        assert [(e.month, e.year) for e in result] == [
            (11, 2025), (12, 2025), (1, 2026)
        ]

    def test_year_rollover_from_december(self):
        result = project_installments(240.0, 2, 12, 2025)
        assert [(e.month, e.year) for e in result] == [(12, 2025), (1, 2026)]

    def test_full_year_installments_from_january(self):
        result = project_installments(1200.0, 12, 1, 2025)
        months = [e.month for e in result]
        assert months == list(range(1, 13))
        assert all(e.year == 2025 for e in result)

    def test_13_installments_crosses_two_years(self):
        result = project_installments(1300.0, 13, 1, 2025)
        assert result[-1].month == 1
        assert result[-1].year == 2026

    # --- edge: correção de arredondamento na última parcela ---

    def test_rounding_correction_on_last_installment(self):
        # 10 / 3 = 3.333... → [3.33, 3.33, 3.34]
        result = project_installments(10.0, 3, 1, 2025)
        assert result[0].amount == 3.33
        assert result[1].amount == 3.33
        assert result[2].amount == 3.34

    def test_sum_equals_total_expense(self):
        result = project_installments(10.0, 3, 1, 2025)
        assert sum(e.amount for e in result) == pytest.approx(10.0)

    def test_zero_expense_all_amounts_zero(self):
        result = project_installments(0.0, 3, 1, 2025)
        assert all(e.amount == 0.0 for e in result)

    # --- fronteiras de mês válido ---

    def test_start_month_1_valid(self):
        result = project_installments(100.0, 1, 1, 2025)
        assert result[0].month == 1

    def test_start_month_12_valid(self):
        result = project_installments(100.0, 1, 12, 2025)
        assert result[0].month == 12

    # --- entradas inválidas ---

    def test_installments_zero_raises(self):
        with pytest.raises(ValueError, match="Installments must be at least 1"):
            project_installments(300.0, 0, 1, 2025)

    def test_installments_negative_raises(self):
        with pytest.raises(ValueError, match="Installments must be at least 1"):
            project_installments(300.0, -1, 1, 2025)

    def test_month_zero_raises(self):
        with pytest.raises(ValueError, match="start_month must be between 1 and 12"):
            project_installments(300.0, 3, 0, 2025)

    def test_month_13_raises(self):
        with pytest.raises(ValueError, match="start_month must be between 1 and 12"):
            project_installments(300.0, 3, 13, 2025)

    def test_negative_expense_raises(self):
        with pytest.raises(ValueError, match="Expense value cannot be negative"):
            project_installments(-100.0, 3, 1, 2025)

    def test_year_zero_raises(self):
        with pytest.raises(ValueError, match="start_year must be a positive integer"):
            project_installments(300.0, 3, 1, 0)

    def test_year_negative_raises(self):
        with pytest.raises(ValueError, match="start_year must be a positive integer"):
            project_installments(300.0, 3, 1, -1)
