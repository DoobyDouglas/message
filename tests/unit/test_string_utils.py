import pytest

from src.utils.string_utils import camel_to_snake


class TestStringUtils:
    @pytest.mark.parametrize(
        ("input_str", "expected"),
        [
            ("CamelCase", "camel_case"),
            ("UserModel", "user_model"),
            ("HTTPRequest", "http_request"),
            ("HTTPServer", "http_server"),
            ("XMLParser", "xml_parser"),
            ("JSONData", "json_data"),
            ("CamelCaseString", "camel_case_string"),
            ("MyTestClass", "my_test_class"),
            ("SomeAPIEndpoint", "some_api_endpoint"),
            ("Test123Abc", "test123_abc"),
            ("XML2JSON", "xml2_json"),
            ("HTTP2Protocol", "http2_protocol"),
            ("ABC123DEF", "abc123_def"),
            ("Test_AlreadySnake", "test_already_snake"),
            ("testAlreadyMixed", "test_already_mixed"),
            ("TestWithNumbers123", "test_with_numbers123"),
            ("123Test", "123_test"),
            ("AaBb", "aa_bb"),
            ("aA", "a_a"),
        ],
    )
    def test_camel_to_snake(self, input_str: str, expected: str) -> None:
        assert camel_to_snake(input_str) == expected

    @pytest.mark.parametrize(
        ("input_str", "expected"),
        [
            ("", ""),
            ("a", "a"),
            ("A", "a"),
            ("AB", "ab"),
            ("ABC", "abc"),
            ("already_snake", "already_snake"),
            ("test_string", "test_string"),
            ("test123", "test123"),
        ],
    )
    def test_camel_to_snake_edge_cases(self, input_str: str, expected: str) -> None:
        assert camel_to_snake(input_str) == expected
