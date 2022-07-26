import contextlib
from io import StringIO
from typing import ContextManager


class CppBuilder:
    """
    Helper class to generate C++ code while keeping proper formatting
    """

    def __init__(self, indent_len=4):
        self._buffer = [StringIO()]
        self._indentation_level = 0
        self._indent_spaces = ' ' * indent_len
        self._indent_next = False

    def get_value(self) -> str:
        assert len(self._buffer) == 1
        return self._buffer[-1].getvalue()

    def save(self, file_out: str) -> None:
        assert len(self._buffer) == 1
        with open(file_out, 'w') as f:
            f.write(self._buffer[-1].getvalue())

    @contextlib.contextmanager
    def indent(self) -> ContextManager:
        self.push_indent()
        try:
            yield
        finally:
            self.pop_indent()

    def push_indent(self) -> None:
        self._indentation_level += 1

    def pop_indent(self) -> None:
        self._indentation_level = max(self._indentation_level - 1, 0)

    @property
    def indentation(self):
        return self._indent_spaces * self._indentation_level

    def write(self, code: str) -> None:
        if not code:
            return

        if self._indent_next:
            self._buffer[-1].write(self.indentation)
        self._buffer[-1].write(code)

        nl_pos = code.rfind('\n')
        if nl_pos != -1 and code[nl_pos:].strip() == '':
            self._indent_next = True
        elif self._indent_next is True:
            if code.strip() != '':
                self._indent_next = False
        else:
            self._indent_next = True

    def write_line(self, code: str = ""):
        self.write("{}\n".format(code))

    @contextlib.contextmanager
    def block(self,
              line: str,
              *,
              inline: bool = False,
              newline: bool = True) -> None:
        self.write('{} {}'.format(line, '{'))

        if not inline:
            self.write('\n')
            self.push_indent()
        else:
            self.write(' ')

        self._buffer.append(StringIO())

        try:
            yield
        finally:
            text = self._buffer.pop().getvalue()
            if inline:
                text = ' '.join(text.split())
            else:
                self.pop_indent()

            self._buffer[-1].write(text)

            if inline:
                if newline:
                    self._buffer[-1].write(" }\n")
                else:
                    self._indent_next = False
                    self._buffer[-1].write(" } ")
            else:
                if newline:
                    self.write_line("}")
                else:
                    self.write("} ")
                    self._indent_next = False

    def _split_write_statement(self, statement: str) -> None:
        lines = statement.splitlines()
        if len(lines) == 1:
            self.write_line("{};".format(lines[-1]))
        elif len(lines) > 1:
            self.write_line(lines[0].strip())
            # Add hanging indent
            with self.indent():
                for line in lines[1:-1]:
                    self.write_line(line)
                self.write_line("{};".format(lines[-1]))

    def write_code(self, statement: str = '') -> None:
        for stmt in statement.split(';'):
            stmt = stmt.strip()
            if stmt:
                self._split_write_statement(stmt)

    def comment(self, comment: str) -> None:
        self.write_line('// {}'.format(comment))

    @contextlib.contextmanager
    def label(self, label: str, end: str = '') -> ContextManager:
        self.write_line("{}:".format(label))
        self._buffer.append(StringIO())

        self.push_indent()

        try:
            yield
        finally:
            if end:
                self.write_code(end)

            text = self._buffer.pop().getvalue()

            self.pop_indent()

            self._buffer[-1].write(text)

    @contextlib.contextmanager
    def case(self, *args, end: str = '') -> None:
        for label in args[:-1]:
            self.write_line("case {}:".format(label))
        with self.label("case {}".format(args[-1]), end=end):
            yield

