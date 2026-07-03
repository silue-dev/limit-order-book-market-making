import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from orderbook import OrderBook


class OrderBookTest(unittest.TestCase):
    """
    Tests for the order book.

    """
    def test_limit_orders_rest_on_book(self):
        """
        Tests that non-crossing limit orders rest on the book.

        """
        book = OrderBook()

        book.add_order({'side': 'bid', 'price': 99, 'volume': 10, 'kind': 'limit', 'user': 'A'})
        book.add_order({'side': 'ask', 'price': 101, 'volume': 10, 'kind': 'limit', 'user': 'B'})

        self.assertEqual(book.get_best_bid(), Decimal('99.0'))
        self.assertEqual(book.get_best_ask(), Decimal('101.0'))
        self.assertEqual(book.get_mid_price(), Decimal('100.00'))
        self.assertEqual(len(book.tape), 0)

    def test_crossing_limit_orders_update_positions(self):
        """
        Tests that crossing limit orders update the users' positions.

        """
        book = OrderBook()

        book.add_order({'side': 'ask', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'A'})
        book.add_order({'side': 'bid', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'B'})

        self.assertIsNone(book.get_mid_price())
        self.assertEqual(len(book.tape), 1)
        self.assertEqual(book.user_positions['A'][-1][1], Decimal('-10.0'))
        self.assertEqual(book.user_positions['B'][-1][1], Decimal('10.0'))

    def test_pnl_marks_to_last_trade_without_mid_price(self):
        """
        Tests that PnL uses the last trade price when there is no mid price.

        """
        book = OrderBook()

        book.add_order({'side': 'ask', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'A'})
        book.add_order({'side': 'bid', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'B'})

        self.assertIsNone(book.get_mid_price())
        self.assertEqual(book.get_mark_price(), Decimal('100.0'))
        self.assertEqual(book.get_pnl('A'), Decimal('0.00'))
        self.assertEqual(book.get_pnl('B'), Decimal('0.00'))

    def test_pnl_marks_to_last_trade_when_book_is_one_sided(self):
        """
        Tests that PnL uses the last trade price when the book is one-sided.

        """
        book = OrderBook()

        book.add_order({'side': 'ask', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'A'})
        book.add_order({'side': 'bid', 'price': 100, 'volume': 6, 'kind': 'limit', 'user': 'B'})

        self.assertIsNone(book.get_mid_price())
        self.assertEqual(book.get_best_ask(), Decimal('100.0'))
        self.assertEqual(book.get_mark_price(), Decimal('100.0'))
        self.assertEqual(book.get_pnl('A'), Decimal('0.00'))
        self.assertEqual(book.get_pnl('B'), Decimal('0.00'))
        self.assertEqual(book.user_positions['A'][-1][1], Decimal('-6.0'))
        self.assertEqual(book.user_positions['B'][-1][1], Decimal('6.0'))

    def test_pnl_marks_to_mid_price_when_book_is_two_sided(self):
        """
        Tests that PnL uses the mid price when the book is two-sided.

        """
        book = OrderBook()

        book.add_order({'side': 'ask', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'A'})
        book.add_order({'side': 'bid', 'price': 100, 'volume': 10, 'kind': 'limit', 'user': 'B'})
        book.add_order({'side': 'bid', 'price': 99, 'volume': 10, 'kind': 'limit', 'user': 'C'})
        book.add_order({'side': 'ask', 'price': 101, 'volume': 10, 'kind': 'limit', 'user': 'D'})

        self.assertEqual(book.get_mid_price(), Decimal('100.00'))
        self.assertEqual(book.get_mark_price(), Decimal('100.00'))
        self.assertEqual(book.get_pnl('A'), Decimal('0.00'))
        self.assertEqual(book.get_pnl('B'), Decimal('0.00'))


if __name__ == '__main__':
    unittest.main()
