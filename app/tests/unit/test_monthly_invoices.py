import pytest
from services.financial_service import (
    project_monthly_invoices, ExpenseData, MonthlyInvoice,
)


class TestProjectMonthlyInvoices:
    # --- caminho feliz ---

    def test_single_expense_single_installment_in_first_month(self):
        # compra à vista de 500 começando no mês de referência
        expenses = [ExpenseData(500.0, 1, 6, 2025)]
        result = project_monthly_invoices(expenses, 6, 2025, 3)
        assert result == [
            MonthlyInvoice(6, 2025, 500.0),
            MonthlyInvoice(7, 2025, 0.0),
            MonthlyInvoice(8, 2025, 0.0),
        ]

    def test_installments_spread_across_months(self):
        # 300 em 3x a partir de junho → 100/mês
        expenses = [ExpenseData(300.0, 3, 6, 2025)]
        result = project_monthly_invoices(expenses, 6, 2025, 3)
        assert [inv.total for inv in result] == [100.0, 100.0, 100.0]

    def test_multiple_expenses_sum_in_same_month(self):
        # duas compras cuja parcela cai em junho devem somar
        expenses = [
            ExpenseData(300.0, 3, 6, 2025),   # 100 em jun/jul/ago
            ExpenseData(200.0, 1, 6, 2025),   # 200 em junho
        ]
        result = project_monthly_invoices(expenses, 6, 2025, 3)
        assert [inv.total for inv in result] == [300.0, 100.0, 100.0]

    # --- janela / horizonte ---

    def test_every_window_month_present_even_without_installments(self):
        # nenhuma despesa → todos os meses zerados, mas presentes
        result = project_monthly_invoices([], 1, 2025, 4)
        assert [(inv.month, inv.year) for inv in result] == [
            (1, 2025), (2, 2025), (3, 2025), (4, 2025)
        ]
        assert all(inv.total == 0.0 for inv in result)

    def test_installments_beyond_window_are_ignored(self):
        # 1200 em 12x, mas janela de só 2 meses → apenas 2 parcelas contam
        expenses = [ExpenseData(1200.0, 12, 1, 2025)]
        result = project_monthly_invoices(expenses, 1, 2025, 2)
        assert len(result) == 2
        assert [inv.total for inv in result] == [100.0, 100.0]

    def test_past_installments_before_reference_are_ignored(self):
        # compra começou em jan; referência é março → jan/fev ficam de fora
        expenses = [ExpenseData(400.0, 4, 1, 2025)]
        result = project_monthly_invoices(expenses, 3, 2025, 4)
        # parcelas 3 e 4 (mar, abr) entram; 5 e 6 (mai, jun) zeram
        assert [(inv.month, inv.total) for inv in result] == [
            (3, 100.0), (4, 100.0), (5, 0.0), (6, 0.0)
        ]

    # --- virada de ano ---

    def test_window_crosses_year_boundary(self):
        # referência nov/2025, horizonte 3 → nov, dez, jan/2026
        expenses = [ExpenseData(300.0, 3, 11, 2025)]
        result = project_monthly_invoices(expenses, 11, 2025, 3)
        assert [(inv.month, inv.year) for inv in result] == [
            (11, 2025), (12, 2025), (1, 2026)
        ]
        assert [inv.total for inv in result] == [100.0, 100.0, 100.0]

    # --- arredondamento agregado ---

    def test_rounding_correction_aggregated(self):
        # 10 em 3x → 3.33, 3.33, 3.34; soma na janela = 10.0
        expenses = [ExpenseData(10.0, 3, 1, 2025)]
        result = project_monthly_invoices(expenses, 1, 2025, 3)
        assert [inv.total for inv in result] == [3.33, 3.33, 3.34]
        assert round(sum(inv.total for inv in result), 2) == 10.0

    # --- boundary: months_ahead ---

    def test_months_ahead_one_returns_only_reference_month(self):
        expenses = [ExpenseData(300.0, 3, 6, 2025)]
        result = project_monthly_invoices(expenses, 6, 2025, 1)
        assert result == [MonthlyInvoice(6, 2025, 100.0)]

    # --- validações ---

    def test_months_ahead_zero_raises(self):
        with pytest.raises(ValueError, match="months_ahead must be at least 1"):
            project_monthly_invoices([], 6, 2025, 0)

    def test_reference_month_zero_raises(self):
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], 0, 2025, 3)

    def test_reference_month_13_raises(self):
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], 13, 2025, 3)

    def test_reference_year_zero_raises(self):
        with pytest.raises(ValueError, match="reference_year must be a positive integer"):
            project_monthly_invoices([], 6, 0, 3)

    def test_invalid_installment_propagates_from_project_installments(self):
        # política estrita herdada de project_installments
        expenses = [ExpenseData(300.0, 0, 6, 2025)]
        with pytest.raises(ValueError, match="Installments must be at least 1"):
            project_monthly_invoices(expenses, 6, 2025, 3)
