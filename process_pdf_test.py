import unittest
import process_pdf

class ProcessPdfClass(unittest.TestCase):

    def setUp(self):
        # Initialize resources before each test
        #self.docs = [
        #    {'file':'data/pdf/2024/20024542.pdf', 'purchases': 2},
        #    {'file':'data/pdf/2024/20024572.pdf', 'purchases': 1},
        #    {'file':'data/pdf/2024/20024800.pdf', 'purchases': 1},
        #    {'file':'data/pdf/2024/20025064.pdf', 'purchases': 2},
        #    {'file':'data/pdf/2024/20025020.pdf', 'purchases': 29}
        #]
        self.docs = [
            {'file':'data/pdf/2024/20025020.pdf', 'purchases': 29}
        ]

    def test_documents(self):
        for doc in self.docs:
            purchases = process_pdf.get_pdf_purchases(doc['file'])
            self.assertIsNotNone(purchases)
            self.assertGreater(len(purchases), 0)
            self.assertEqual(len(purchases), doc['purchases'])


if __name__ == '__main__':
    unittest.main()
