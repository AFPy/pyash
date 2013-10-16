import unittest

from pyash import MovesFile

class TestSequenceFunctions(unittest.TestCase):

    def test_normal(self):
        moves = MovesFile('tests/normal.dat')
        moves_list = list(moves.parse())
        self.assertEqual(710, len(moves_list))

    def test_file_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            MovesFile('idonotexist')

    def test_empty_line_missing(self):
        moves = MovesFile('tests/empty_line_missing.dat')
        moves_list = list(moves.parse())
        self.assertEqual(4, len(moves_list))

    def test_too_many_lines_between(self):
        moves = MovesFile('tests/too_many_lines_between.dat')
        moves_list = list(moves.parse())
        self.assertEqual(4, len(moves_list))

    # trop de lignes entre deux mouvements
    # trop de lignes avant le 1er mouvement
    # trop de lignes après le 2 mouvement
    # 1ère ligne moins de 2 espace
    # 1ère ligne premier élément n'est pas une date
    # 1ère ligne second élément n'est pas un chiffre suivi de €
    # 2nde ligne ne commence pas par 4*' '
    # commentaire sur plusieurs lignes
    # nieme ligne de commentaire ne commence pas par 4*' ' 

if __name__ == '__main__':
    unittest.main()
