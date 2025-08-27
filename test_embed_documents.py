import os

import pytest
import embed_documents


DATA_DIRECTORY = os.getcwd() + '/test_data'


class TestXmlParser:
    def test_xml_parser(self):
        pass


class TestCsvParser:
    def test_csv_parser_blank(self):
        assert embed_documents.csv_parser(DATA_DIRECTORY + '/csv/blank.csv') == []

    def test_csv_parser_empty_rows(self):
        assert embed_documents.csv_parser(DATA_DIRECTORY + '/csv/empty_rows.csv') == [': None. : None. : None. : None.', ': None. : None. : None. : None.']

    def test_csv_parser_sample(self):
        assert len(embed_documents.csv_parser(DATA_DIRECTORY + '/csv/sample.csv')) == 103


class TestTxtParser:
    def test_txt_parser_blank(self):
        assert embed_documents.txt_parser(DATA_DIRECTORY + '/txt/blank.txt') == ['']


    def test_txt_parser_empty_lines(self):
        assert embed_documents.txt_parser(DATA_DIRECTORY + '/txt/empty_lines.txt') == ['']


    def test_txt_parser_leading_empty_lines(self):
        assert embed_documents.txt_parser(DATA_DIRECTORY + '/txt/leading_empty_lines.txt') == ['Line 5: Four leading empty lines.']


    def test_txt_parser_sample(self):
        assert embed_documents.txt_parser(DATA_DIRECTORY + '/txt/sample.txt') == ['Line 3: This is some sample data. Line 4: After being parsed the output should be a single string in a list. Line 5: Each line should be separated by a space. Line 6: Empty Lines should be ingored. Line 9: Line 10: Line 11: This is the last line.']