import unittest
import process_pdf

class ProcessPdfClass(unittest.TestCase):

    def setUp(self):
        # Initialize resources before each test
        self.docs = [
            {'file':'data/pdf/2024/20024612.pdf', 'purchases': 42},
            {'file':'data/pdf/2024/20024916.pdf', 'purchases': 2},
            {'file':'data/pdf/2024/20024062.pdf', 'purchases': 2},
            {'file':'data/pdf/2024/20024248.pdf', 'purchases': 42},
            {'file':'data/pdf/2024/20024413.pdf', 'purchases': 1},
            {'file':'data/pdf/2024/20024461.pdf', 'purchases': 37},
            {'file':'data/pdf/2024/20024572.pdf', 'purchases': 1},
            {'file':'data/pdf/2024/20025020.pdf', 'purchases': 29}
        ]

    def test_documents(self):
        all_purchases = []
        for doc in self.docs:
            purchases = process_pdf.get_pdf_purchases(doc['file'])
            all_purchases.extend(purchases)
            self.assertIsNotNone(purchases)
            self.assertGreater(len(purchases), 0)
            self.assertEqual(len(purchases), doc['purchases'])
        df = process_pdf.pdf_purchases_to_df(all_purchases)
        self.assertIsNotNone(df)

if __name__ == '__main__':
    unittest.main()
