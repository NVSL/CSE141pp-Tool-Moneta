import unittest
import view
import model

class StartMVC(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_model_init(self):
        self.assertIsNotNone(model.Model())

    def test_view_init(self):
        self.assertIsNotNone(view.View(model.Model()))

if __name__ == '__main__':
    unittest.main(warnings='ignore')
