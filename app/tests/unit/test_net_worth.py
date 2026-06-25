from services.financial_service import calculate_net_worth, InvestmentData


class TestCalculateNetWorth:
    def test_no_investments_returns_balance(self):
        assert calculate_net_worth([], 5000.0) == 5000.0

    def test_investment_no_dividends(self):
        assert calculate_net_worth([InvestmentData(10000, 0.0)], 0.0) == 10000.0

    def test_investment_with_dividends(self):
        assert calculate_net_worth([InvestmentData(10000, 500)], 0.0) == 10500.0

    def test_multiple_investments(self):
        investments = [InvestmentData(5000, 200), InvestmentData(3000, 100)]
        # (5000+200) + (3000+100) + 1000 = 9300
        assert calculate_net_worth(investments, 1000.0) == 9300.0

    def test_negative_balance_reduces_worth(self):
        assert calculate_net_worth([InvestmentData(5000, 0)], -1000.0) == 4000.0

    def test_negative_balance_larger_than_investments(self):
        assert calculate_net_worth([InvestmentData(500, 0)], -1000.0) == -500.0

    def test_all_zeros(self):
        assert calculate_net_worth([], 0.0) == 0.0

    def test_large_values_precision(self):
        investments = [InvestmentData(1_000_000, 50_000)]
        assert calculate_net_worth(investments, 50_000.0) == 1_100_000.0

    def test_zero_dividends_not_counted(self):
        assert calculate_net_worth([InvestmentData(1000, 0.0)], 500.0) == 1500.0
