import pytest
from services.financial_service import (
    project_monthly_invoices, ExpenseData, MonthlyInvoice,
)

# =============================================================================
# MC/DC — validação de reference_month
# =============================================================================
#
# Condições atômicas:
#   C1: reference_month < 1
#   C2: reference_month > 12
#
# Tabela-verdade (C1 OR C2 → raises ValueError):
#
#  | # | C1 (month < 1) | C2 (month > 12) | Raises |
#  |---|----------------|-----------------|--------|
#  | 1 |       F        |        F        |   F    |
#  | 2 |       F        |        T        |   T    |
#  | 3 |       T        |        F        |   T    |
#  | 4 |       T        |        T        |   impossível (inexecutável)
#
#  * Caso 4 é inexecutável: um inteiro não pode ser simultaneamente < 1 e > 12
#
# Pares MC/DC:
#   Par de C1: caso 1 × caso 3  →  C2 fixo em F, só C1 muda (F→T)  →  válido → raises
#   Par de C2: caso 1 × caso 2  →  C1 fixo em F, só C2 muda (F→T)  →  válido → raises
#
# Conjunto mínimo MC/DC: { 1, 2, 3 }  →  N+1 = 3 testes para N=2 condições
#
# Valores concretos:
#   Caso 1 → month=6:   C1=F, C2=F  →  válido
#   Caso 2 → month=17:  C1=F, C2=T  →  raises
#   Caso 3 → month=-5:   C1=T, C2=F  →  raises
#
# BVA — reference_month [1, 12]:
#   OFF point abaixo → month=0   raises
#   ON point mínimo  → month=1   válido
#   ON point         → month=2   válido
#   ON point         → month=11  válido
#   ON point máximo  → month=12  válido
#   OFF point acima  → month=13  raises
#
# BVA — reference_year [1, ∞):
#   OFF point → year=-1  raises
#   OFF point → year=0  raises
#   ON point  → year=1  válido
#
# BVA — months_ahead [1, ∞):
#   OFF point → months_ahead=-1  raises
#   OFF point → months_ahead=0  raises
#   ON point  → months_ahead=1  válido
# =============================================================================


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
        assert result == [
            MonthlyInvoice(6, 2025, 100.0),
            MonthlyInvoice(7, 2025, 100.0),
            MonthlyInvoice(8, 2025, 100.0),
        ]

    def test_multiple_expenses_sum_in_same_month(self):
        # duas compras cuja parcela cai em junho devem somar
        expenses = [
            ExpenseData(300.0, 3, 6, 2025),   # 100 em jun/jul/ago
            ExpenseData(200.0, 1, 6, 2025),   # 200 em junho
        ]
        result = project_monthly_invoices(expenses, 6, 2025, 3)
        assert result == [
            MonthlyInvoice(6, 2025, 300.0),
            MonthlyInvoice(7, 2025, 100.0),
            MonthlyInvoice(8, 2025, 100.0),
        ]

    # --- janela / horizonte ---

    def test_every_window_month_present_even_without_installments(self):
        # nenhuma despesa → todos os meses zerados, mas presentes
        result = project_monthly_invoices([], 1, 2025, 4)
        assert result == [
            MonthlyInvoice(1, 2025, 0.0),
            MonthlyInvoice(2, 2025, 0.0),
            MonthlyInvoice(3, 2025, 0.0),
            MonthlyInvoice(4, 2025, 0.0),
        ]

    def test_installments_beyond_window_are_ignored(self):
        # 1200 em 12x, mas janela de só 2 meses → apenas 2 parcelas contam
        expenses = [ExpenseData(1200.0, 12, 1, 2025)]
        result = project_monthly_invoices(expenses, 1, 2025, 2)
        assert result == [
            MonthlyInvoice(1, 2025, 100.0),
            MonthlyInvoice(2, 2025, 100.0),
        ]

    def test_past_installments_before_reference_are_ignored(self):
        # compra começou em jan; referência é março → jan/fev ficam de fora
        expenses = [ExpenseData(400.0, 4, 1, 2025)]
        result = project_monthly_invoices(expenses, 3, 2025, 4)
        # parcelas 3 e 4 (mar, abr) entram; 5 e 6 (mai, jun) zeram
        assert result == [
            MonthlyInvoice(3, 2025, 100.0),
            MonthlyInvoice(4, 2025, 100.0),
            MonthlyInvoice(5, 2025, 0.0),
            MonthlyInvoice(6, 2025, 0.0),
        ]

    # --- virada de ano ---

    def test_window_crosses_year_boundary(self):
        # referência nov/2025, horizonte 3 → nov, dez, jan/2026
        expenses = [ExpenseData(300.0, 3, 11, 2025)]
        result = project_monthly_invoices(expenses, 11, 2025, 3)
        assert result == [
            MonthlyInvoice(11, 2025, 100.0),
            MonthlyInvoice(12, 2025, 100.0),
            MonthlyInvoice(1, 2026, 100.0),
        ]

    # --- arredondamento agregado ---

    def test_rounding_correction_aggregated(self):
        # 10 em 3x → 3.33, 3.33, 3.34; soma na janela = 10.0
        expenses = [ExpenseData(10.0, 3, 1, 2025)]
        result = project_monthly_invoices(expenses, 1, 2025, 3)
        assert result == [
            MonthlyInvoice(1, 2025, 3.33),
            MonthlyInvoice(2, 2025, 3.33),
            MonthlyInvoice(3, 2025, 3.34),
        ]
        assert round(sum(inv.total for inv in result), 2) == 10.0

    # --- boundary: months_ahead ---

    def test_months_ahead_one_returns_only_reference_month(self):
        expenses = [ExpenseData(300.0, 3, 6, 2025)]
        result = project_monthly_invoices(expenses, 6, 2025, 1)
        assert result == [MonthlyInvoice(6, 2025, 100.0)]
        

    # --- validações ---

    def test_correct_month(self):
        # MC/DC caso 1: C1=F, C2=F → válido (ON point)
        expenses = [ExpenseData(500.0, 2, 6, 2025)]
        result = project_monthly_invoices(expenses, 6, 2025, 2)
        assert result == [
            MonthlyInvoice(6, 2025, 250.0),
            MonthlyInvoice(7, 2025, 250.0),
        ]

    def test_reference_month_zero_raises(self):
        # MC/DC caso 3: C1=T, C2=F → raises (OFF point abaixo)
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], -5, 2025, 3)
    
    def test_reference_month_13_raises(self):
        # MC/DC caso 2: C1=F, C2=T → raises (OFF point acima)
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], 17, 2025, 3)



    def test_reference_month_one_is_valid(self):
        # BVA ON point mínimo: month=1 → válido
        result = project_monthly_invoices([], 1, 2025, 1)
        assert result == [MonthlyInvoice(1, 2025, 0.0)]

    def test_reference_month_twelve_is_valid(self):
        # BVA ON point máximo: month=12 → válido
        result = project_monthly_invoices([], 12, 2025, 1)
        assert result == [MonthlyInvoice(12, 2025, 0.0)]

    def test_reference_month_two_is_valid(self):
        # BVA ON point: month=2 → válido
        result = project_monthly_invoices([], 2, 2025, 1)
        assert result == [MonthlyInvoice(2, 2025, 0.0)]

    def test_reference_month_eleven_is_valid(self):
        # BVA ON point: month=11 → válido
        result = project_monthly_invoices([], 11, 2025, 1)
        assert result == [MonthlyInvoice(11, 2025, 0.0)]

    def test_reference_month_13_raises(self):
        # BVA OFF point: month=13 → raises
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], 13, 2025, 3)
    
    def test_reference_month_0_raises(self):
        # BVA OFF point: month=0 → raises
        with pytest.raises(ValueError, match="reference_month must be between 1 and 12"):
            project_monthly_invoices([], 0, 2025, 3)

    


    def test_months_ahead_zero_raises(self):
        # BVA OFF point: months_ahead=0 → raises
        with pytest.raises(ValueError, match="months_ahead must be at least 1"):
            project_monthly_invoices([], 6, 2025, 0)

    def test_months_ahead_negative_raises(self):
        # BVA OFF point: months_ahead=-1 → raises
        with pytest.raises(ValueError, match="months_ahead must be at least 1"):
            project_monthly_invoices([], 6, 2025, -1)

    def test_months_ahead_valid(self):
        # BVA ON point: months_ahead=1 → válido
        result = project_monthly_invoices([], 6, 2025, 1)
        assert result == [MonthlyInvoice(6, 2025, 0.0)]

    

    def test_reference_year_zero_raises(self):
        # BVA OFF point: year=0 → raises
        with pytest.raises(ValueError, match="reference_year must be a positive integer"):
            project_monthly_invoices([], 6, 0, 3)

    def test_reference_year_negative_raises(self):
        # BVA OFF point: year=-1 → raises
        with pytest.raises(ValueError, match="reference_year must be a positive integer"):
            project_monthly_invoices([], 6, -1, 3)

    def test_reference_year_one_is_valid(self):
        # BVA ON point: year=1 → válido
        result = project_monthly_invoices([], 6, 1, 1)
        assert result == [MonthlyInvoice(6, 1, 0.0)]



    def test_invalid_installment_propagates_from_project_installments(self):
        # política estrita herdada de project_installments
        expenses = [ExpenseData(300.0, 0, 6, 2025)]
        with pytest.raises(ValueError, match="Installments must be at least 1"):
            project_monthly_invoices(expenses, 6, 2025, 3)
