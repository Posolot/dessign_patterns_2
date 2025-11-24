import unittest
from datetime import datetime
from time import perf_counter
from Src.Logics.osv_service import OSVReportService
from Src.Logics.block_period import BlockPeriodCalculator
from Src.Models.settings_model import settings_model
from Src.Dtos.filter_dto import filter_dto

# -------------------------
# Моковые данные
# -------------------------
class MockNomenclature:
    def __init__(self, unique_code):
        self.unique_code = unique_code
        self.range = None

class MockTransaction:
    def __init__(self, nomenclature, date_tr, quantity):
        self.nomenclature = nomenclature
        self.date_tr = date_tr
        self.quantity = quantity
        self.range = None
        self.storage = None

class MockStartService:
    def __init__(self, transactions, nomenclatures):
        self.data = {
            "transaction_model": transactions,
            "nomenclature_model": nomenclatures
        }

class TestBlockPeriodCalculator(unittest.TestCase):

    def setUp(self):
        # Общие данные
        self.n1 = MockNomenclature("n1")
        self.t1 = MockTransaction(self.n1, datetime(2023, 12, 15), 10)  # до блокировки
        self.t2 = MockTransaction(self.n1, datetime(2024, 2, 1), -3)     # после блокировки
        self.start_service = MockStartService([self.t1, self.t2], [self.n1])
        self.osv_service = OSVReportService(self.start_service)
        self.calculator = BlockPeriodCalculator(self.osv_service)

    def test_balance_is_same_with_different_block_date(self):
        # -------------------------
        # Подготовка
        # -------------------------

        settings_model.block_period = datetime(2024, 1, 1)
        self.calculator.calculate_turnover_until_block()

        report1 = self.calculator.calculate_balance(datetime(2024, 1, 1), datetime(2024, 3, 1))

        # -------------------------
        # Действие
        # -------------------------
        settings_model.block_period = datetime(2024, 1, 15)
        self.calculator.calculate_turnover_until_block()
        report2 = self.calculator.calculate_balance(datetime(2024, 1, 1), datetime(2024, 3, 1))

        # -------------------------
        # Проверки
        # -------------------------
        self.assertEqual(len(report1), 1)
        self.assertEqual(len(report2), 1)

        r1 = report1[0]
        r2 = report2[0]

        self.assertEqual(r1["incoming"], r2["incoming"], "Incoming не должен измениться при смене даты блокировки")
        self.assertEqual(r1["outgoing"], r2["outgoing"], "Outgoing не должен измениться при смене даты блокировки")
        self.assertEqual(r1["end_balance"], r2["end_balance"], "End balance не должен измениться при смене даты блокировки")

class TestBlockPeriodCalculatorPerformance(unittest.TestCase):

    def test_large_volume_performance(self):
        import random
        num_transactions = 100000
        nomenclatures = [MockNomenclature(f"n{i}") for i in range(10)]
        transactions = []
        for i in range(num_transactions):
            n = random.choice(nomenclatures)
            date = datetime(2024, 1, 1) if i % 2 == 0 else datetime(2024, 2, 1)
            qty = random.randint(-10, 10)
            transactions.append(MockTransaction(n, date, qty))

        start_service = MockStartService(transactions, nomenclatures)
        osv_service = OSVReportService(start_service)
        calculator = BlockPeriodCalculator(osv_service)

        block_dates = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 15),
            datetime(2024, 2, 1)
        ]

        results = []

        for bd in block_dates:
            settings_model.block_period = bd

            t0 = perf_counter()
            turnover_before_block = calculator.calculate_turnover_until_block()
            t1 = perf_counter()
            report = calculator.calculate_balance(datetime(2024, 1, 1), datetime(2024, 3, 1))
            t2 = perf_counter()

            # Количество транзакций до и после блокировки
            count_before_block = sum(
                1 for tr in transactions if tr.date_tr <= bd
            )
            count_after_block = sum(
                1 for tr in transactions if tr.date_tr > bd
            )

            results.append({
                "block_date": bd.strftime("%Y-%m-%d"),
                "turnover_time": t1 - t0,
                "balance_time": t2 - t1,
                "transactions_before_block": count_before_block,
                "transactions_after_block": count_after_block
            })

        with open("performance_results.md", "w", encoding="utf-8") as f:
            f.write("| Block Date | Turnover Time (s) | Balance Time (s) | Transactions Before Block | Transactions After Block |\n")
            f.write("|------------|-----------------|-----------------|--------------------------|-------------------------|\n")
            for r in results:
                f.write(f"| {r['block_date']} | {r['turnover_time']:.4f} | {r['balance_time']:.4f} | {r['transactions_before_block']} | {r['transactions_after_block']} |\n")

        self.assertTrue(all(r['turnover_time'] > 0 for r in results))
        self.assertTrue(all(r['balance_time'] > 0 for r in results))



if __name__ == "__main__":
    unittest.main()
