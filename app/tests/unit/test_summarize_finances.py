import pytest
from services.financial_service import (
    summarize_finances, IncomeData, ExpenseData, BillData, InvestmentData
)


class TestSummarizeFinances:
    def test_full_summary_without_ceiling(self):
        result = summarize_finances(
            [IncomeData(5000)],
            [ExpenseData(1200, 3, 1, 2025)],
            [BillData(300)],
            [InvestmentData(10000, 500)],
        )
        assert result["balance"] == 4300.0       # 5000 - 400 - 300
        assert result["total_income"] == 5000.0
        assert result["total_spending"] == 700.0  # 400 + 300
        assert result["net_worth"] == 14800.0     # 4300 + 10000 + 500
        assert "budget_status" not in result

    def test_budget_status_ok(self):
        result = summarize_finances(
            [IncomeData(5000)],
            [ExpenseData(1200, 3, 1, 2025)],
            [BillData(300)],
            [],
            budget_ceiling=1000,
        )
        assert result["budget_status"] == "OK"  # 700/1000 = 70%

    def test_budget_status_warning(self):
        result = summarize_finances(
            [IncomeData(5000)],
            [ExpenseData(500, 1, 1, 2025)],
            [BillData(400)],
            [],
            budget_ceiling=1000,
        )
        assert result["budget_status"] == "WARNING"  # 900/1000 = 90%

    def test_budget_status_exceeded(self):
        result = summarize_finances(
            [IncomeData(5000)],
            [ExpenseData(600, 1, 1, 2025)],
            [BillData(500)],
            [],
            budget_ceiling=1000,
        )
        assert result["budget_status"] == "EXCEEDED"  # 1100/1000

    def test_empty_user_all_zeros(self):
        result = summarize_finances([], [], [], [])
        assert result["balance"] == 0.0
        assert result["net_worth"] == 0.0
        assert result["total_income"] == 0.0
        assert result["total_spending"] == 0.0

    def test_ceiling_none_omits_budget_status(self):
        result = summarize_finances([], [], [], [], budget_ceiling=None)
        assert "budget_status" not in result
