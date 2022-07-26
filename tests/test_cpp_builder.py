import pytest

from CppBuilder import CppBuilder


@pytest.fixture
def test_builder():
    return CppBuilder()


def test_indent():
    indentation_spaces = 5
    test_builder = CppBuilder(indentation_spaces)
    with test_builder.indent():
        with test_builder.indent():
            assert len(test_builder.indentation) == indentation_spaces * 2
    assert len(test_builder.indentation) == 0


def test_write_line_no_code(test_builder):
    test_builder.write_line()
    assert test_builder.get_value() == "\n"


def test_write_line(test_builder):
    test_string = "#include <stdio.h>"
    test_builder.write_line(test_string)

    assert test_builder.get_value() == test_string + "\n"


def test_block_inline(test_builder):
    test_block_output = "int main(void) {  }\n"
    test_block_input = "int main(void)"

    with test_builder.block(test_block_input, inline=True):
        pass
    assert test_builder.get_value() == test_block_output


def test_block(test_builder):
    test_block_output = "int main(void) {\n}\n"
    test_block_input = "int main(void)"

    with test_builder.block(test_block_input):
        pass
    assert test_builder.get_value() == test_block_output


def test_code_single_line(test_builder):
    test_code = "int x"

    test_builder.write_code(test_code)
    assert test_builder.get_value() == test_code + ";\n"


def test_code_multi_line(test_builder):
    test_code_input = "int x; int y;"
    test_code_output = "int x;\nint y;\n"

    test_builder.write_code(test_code_input)
    assert test_builder.get_value() == test_code_output


def test_comment(test_builder):
    test_input = "this is a comment"
    test_output = "// " + test_input + "\n"

    test_builder.comment(test_input)
    assert test_builder.get_value() == test_output
