import pytest
from services.financial_service import calculate_balance, IncomeData, ExpenseData, BillData


class TestCalculateBalance:
    # --- caminho feliz ---

    def test_basic_balance(self):
        # 5000 - (1200/3) - 300 = 4300
        assert calculate_balance(
            [IncomeData(5000)], [ExpenseData(1200, 3)], [BillData(300)]
        ) == 4300.0

    def test_multiple_incomes(self):
        incomes = [IncomeData(3000), IncomeData(2000)]
        assert calculate_balance(incomes, [], []) == 5000.0

    def test_multiple_expenses_different_installments(self):
        # 600/2 + 900/3 = 300 + 300 = 600
        expenses = [ExpenseData(600, 2), ExpenseData(900, 3)]
        assert calculate_balance([], expenses, []) == -600.0

    def test_multiple_bills(self):
        bills = [BillData(200), BillData(150)]
        assert calculate_balance([], [], bills) == -350.0

    def test_single_installment_full_value_this_month(self):
        assert calculate_balance([], [ExpenseData(500, 1)], []) == -500.0

    def test_negative_balance_deficit(self):
        assert calculate_balance([IncomeData(1000)], [], [BillData(1500)]) == -500.0

    # --- edge: listas vazias ---

    def test_all_empty_returns_zero(self):
        assert calculate_balance([], [], []) == 0.0

    def test_zero_income_value(self):
        assert calculate_balance([IncomeData(0)], [], []) == 0.0

    # --- edge: saldo exatamente zero ---

    def test_exact_zero_balance(self):
        incomes = [IncomeData(500)]
        expenses = [ExpenseData(300, 1)]
        bills = [BillData(200)]
        assert calculate_balance(incomes, expenses, bills) == 0.0

    # --- edge: installment=0 não divide por zero (max(0,1)=1) ---

    def test_installment_zero_treated_as_one(self):
        assert calculate_balance([], [ExpenseData(300, 0)], []) == -300.0

    # --- validações: valores negativos levantam ValueError ---

    def test_negative_income_raises(self):
        with pytest.raises(ValueError, match="Income values cannot be negative"):
            calculate_balance([IncomeData(-1)], [], [])

    def test_negative_expense_raises(self):
        with pytest.raises(ValueError, match="Expense values cannot be negative"):
            calculate_balance([], [ExpenseData(-100, 1)], [])

    def test_negative_bill_raises(self):
        with pytest.raises(ValueError, match="Bill values cannot be negative"):
            calculate_balance([], [], [BillData(-50)])
