import pytest
from services.financial_service import (
    calculate_category_totals, check_all_category_alerts,
    ExpenseData, CategoryBudgetData,
)


class TestCalculateCategoryTotals:
    def test_empty_expenses_returns_empty(self):
        assert calculate_category_totals([]) == {}

    def test_single_expense_single_category(self):
        result = calculate_category_totals([ExpenseData(300, 1, "alimentação")])
        assert result == {"alimentação": 300.0}

    def test_installment_expense_contributes_monthly_fraction(self):
        result = calculate_category_totals([ExpenseData(1200, 4, "transporte")])
        assert result == {"transporte": 300.0}

    def test_multiple_expenses_same_category_are_summed(self):
        expenses = [
            ExpenseData(600, 2, "alimentação"),   # 300/mês
            ExpenseData(300, 1, "alimentação"),   # 300/mês
        ]
        result = calculate_category_totals(expenses)
        assert result == {"alimentação": 600.0}

    def test_multiple_expenses_different_categories(self):
        expenses = [
            ExpenseData(500, 1, "alimentação"),
            ExpenseData(200, 1, "transporte"),
        ]
        result = calculate_category_totals(expenses)
        assert result == {"alimentação": 500.0, "transporte": 200.0}

    def test_default_category_geral(self):
        result = calculate_category_totals([ExpenseData(100, 1)])
        assert "geral" in result

    def test_installment_zero_treated_as_one(self):
        result = calculate_category_totals([ExpenseData(300, 0, "lazer")])
        assert result == {"lazer": 300.0}

    def test_three_categories(self):
        expenses = [
            ExpenseData(600, 2, "alimentação"),   # 300
            ExpenseData(400, 1, "transporte"),    # 400
            ExpenseData(900, 3, "lazer"),          # 300
        ]
        result = calculate_category_totals(expenses)
        assert result == {"alimentação": 300.0, "transporte": 400.0, "lazer": 300.0}


class TestCheckAllCategoryAlerts:
    def test_empty_budgets_returns_empty(self):
        assert check_all_category_alerts({}, []) == {}

    def test_category_with_no_expenses_treated_as_zero(self):
        budgets = [CategoryBudgetData("alimentação", 500)]
        result = check_all_category_alerts({}, budgets)
        assert result == {"alimentação": "OK"}

    def test_category_ok(self):
        totals = {"alimentação": 300.0}
        budgets = [CategoryBudgetData("alimentação", 500)]
        assert check_all_category_alerts(totals, budgets) == {"alimentação": "OK"}

    def test_category_warning(self):
        totals = {"transporte": 450.0}
        budgets = [CategoryBudgetData("transporte", 500)]
        # 450/500 = 90% → WARNING
        assert check_all_category_alerts(totals, budgets) == {"transporte": "WARNING"}

    def test_category_exceeded(self):
        totals = {"lazer": 600.0}
        budgets = [CategoryBudgetData("lazer", 500)]
        assert check_all_category_alerts(totals, budgets) == {"lazer": "EXCEEDED"}

    def test_multiple_categories_different_statuses(self):
        totals = {"alimentação": 300.0, "transporte": 450.0, "lazer": 600.0}
        budgets = [
            CategoryBudgetData("alimentação", 500),
            CategoryBudgetData("transporte", 500),
            CategoryBudgetData("lazer", 500),
        ]
        result = check_all_category_alerts(totals, budgets)
        assert result["alimentação"] == "OK"
        assert result["transporte"] == "WARNING"
        assert result["lazer"] == "EXCEEDED"

    def test_category_in_totals_without_budget_is_ignored(self):
        totals = {"alimentação": 300.0, "sem_teto": 999.0}
        budgets = [CategoryBudgetData("alimentação", 500)]
        result = check_all_category_alerts(totals, budgets)
        assert "sem_teto" not in result

    def test_boundary_exactly_at_ceiling_exceeded(self):
        totals = {"alimentação": 500.0}
        budgets = [CategoryBudgetData("alimentação", 500)]
        assert check_all_category_alerts(totals, budgets) == {"alimentação": "EXCEEDED"}

    def test_boundary_exactly_80_percent_ok(self):
        totals = {"alimentação": 400.0}
        budgets = [CategoryBudgetData("alimentação", 500)]
        # 400/500 = 80% → OK (não é > 0.8)
        assert check_all_category_alerts(totals, budgets) == {"alimentação": "OK"}

    def test_zero_ceiling_raises(self):
        with pytest.raises(ValueError, match="must be greater than zero"):
            check_all_category_alerts({}, [CategoryBudgetData("alimentação", 0)])

    def test_negative_ceiling_raises(self):
        with pytest.raises(ValueError, match="must be greater than zero"):
            check_all_category_alerts({}, [CategoryBudgetData("alimentação", -100)])
