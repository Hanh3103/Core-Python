import ast
import os.path
import re
import textwrap
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("path", help="the path to the file")
arg = parser.parse_args()


class LineTooLongError(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S001 is too long"


class IndentationNotMultiple(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S002 Indentation is not multiple of four"


class UnnecessarySemicolon(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S003 Unnecessary semicolon"


class LessThanTwoSpaces(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S004 At least two spaces required before inline comments"


class TodoComment(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S005 TODO found"


class TooManyBlankLines(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S006 More than two blank lines used before this line"


class TooManySpacesAfterName(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S007 Too many spaces after \'class\'"


class WrongFormatClassName(Exception):
    def __init__(self, line_number, path_info, class_name):
        self.line_number = str(line_number + 1)
        self.path_info = path_info
        self.class_name = class_name

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S008 Class name \'{self.class_name}\' should use CamelCase"


class WrongFormatFunctionName(Exception):
    def __init__(self, line_number, path_info, func_name):
        self.line_number = str(line_number + 1)
        self.path_info = path_info
        self.func_name = func_name

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S009 Function name \'{self.func_name}\' should use " \
               f"snake_case "


class WrongArgumentFormat(Exception):
    def __init__(self, line_number, path_info, arg_name):
        self.line_number = str(line_number + 1)
        self.path_info = path_info
        self.arg_name = arg_name

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S010 Argument name \'{self.arg_name}\' should be " \
               f"snake_case "


class MutableArgumentValue(Exception):
    def __init__(self, line_number, path_info):
        self.line_number = str(line_number + 1)
        self.path_info = path_info

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S012 Default argument value is mutable"


class WrongVariableName(Exception):
    def __init__(self, line_number, path_info, var_name):
        self.line_number = str(line_number + 1)
        self.path_info = path_info
        self.var_name = var_name

    def __str__(self):
        return f"{self.path_info}: Line {self.line_number}: S011 Variable name \'{self.var_name}\' in function should be " \
               f"snake_case "


# Open the file in read mode
def analyze_code(path_file):
    with open(path_file, "r") as fi:
        source = fi.read()
        false_args, mut_arg_values = find_false_args_and_mut(source)
        false_var = find_false_variable_names(source)

    with open(path_file, "r") as f:
        lines = f.readlines()

        count_blank = 0
        # Check each line for length
        for i, line in enumerate(lines):
            try:
                if len(line) > 79:
                    # Raise the custom error with the line number
                    raise LineTooLongError(i, path_file)
            except LineTooLongError as e:
                print(e)
            try:
                if check_ident(line):
                    raise IndentationNotMultiple(i, path_file)
            except IndentationNotMultiple as it:
                print(it)
            try:
                if check_line_semicolon(line):
                    raise UnnecessarySemicolon(i, path_file)
            except UnnecessarySemicolon as u:
                print(u)
            try:
                if not check_inline_comment(line):
                    raise LessThanTwoSpaces(i, path_file)
            except LessThanTwoSpaces as li:
                print(li)
            try:
                if check_todo_comment(line):
                    raise TodoComment(i, path_file)
            except TodoComment as t:
                print(t)
            try:
                if line.strip() == '':
                    count_blank += 1
                else:
                    if count_blank > 2:
                        count_blank = 0
                        raise TooManyBlankLines(i, path_file)
                    else:
                        count_blank = 0
            except TooManyBlankLines as to:
                print(to)
            try:
                if check_spaces_constructor(line):
                    raise TooManySpacesAfterName(i, path_file)
            except TooManySpacesAfterName as to_ex:
                print(to_ex)
            try:
                bool_a, class_name = check_class_name(line)
                if bool_a:
                    raise WrongFormatClassName(i, path_file, class_name)
            except WrongFormatClassName as wr:
                print(wr)
            try:
                bool_b, func_name = check_function_name(line)
                if bool_b:
                    raise WrongFormatFunctionName(i, path_file, func_name)
            except WrongFormatFunctionName as wf:
                print(wf)
            try:
                if (i + 1) in false_args.keys():
                    raise WrongArgumentFormat(i, path_file, false_args.get(i+1))
            except WrongArgumentFormat as wa:
                print(wa)
            try:
                if (i + 1) in false_var.keys():
                    raise WrongVariableName(i, path_file, false_var.get(i+1))
            except WrongVariableName as wv:
                print(wv)
            try:
                if (i + 1) in mut_arg_values:
                    raise MutableArgumentValue(i, path_file)
            except MutableArgumentValue as m:
                print(m)


def analyse_code_path(path_):
    if os.path.isfile(path_) and path_.endswith(".py"):
        analyze_code(path_)
    elif os.path.isdir(path_):
        for root, dirs, files in os.walk(path_):
            for file in files:
                if file.endswith(".py"):
                    file_pa = os.path.join(root, file)
                    if file_pa.endswith('tests.py'):
                        continue
                    analyze_code(file_pa)
    else:
        print("No path found.")


def check_spaces_constructor(line):
    pattern = r'(def|class)(\s\s\s*)[\w()]+:'
    lin_ = line.strip()
    # print(line)
    if re.match(pattern, lin_):
        return True
    else:
        return False


def check_class_name(line):
    boo_tmp = False
    construction_line = r'class\s*([a-zA-Z_]\w*)\s*:'
    matching = re.search(construction_line, line.strip())
    camel_case_regex = r'^([A-Z][a-z]*)*(?:\([A-Za-z]+\))?$'
    if matching:
        class_name = matching.group(1)
        # print(class_name)
        if not re.match(camel_case_regex, class_name):
            boo_tmp = True
            return boo_tmp, class_name
    return boo_tmp, ""


def check_function_name(line):
    snake_case = r'^_*[a-z][a-z0-9]+(?:_[a-z0-9_]*)*$'
    function_line = r'def\s*([\w_]+)\('
    matching = re.search(function_line, line.strip())
    function_name = ""
    if matching:
        # tree = ast.parse(class_name)
        # if isinstance(tree, ast.Module):
        #     for node in tree.body:
        #         if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        #             func_name = node.value.func.id
        #             if func_name is not None:
        #                 function_name = func_name
        # match = re.search(r'^([\w_])*\($', func_name)
        function_name = matching.group(1)
        # print(function_name)
        if not re.match(snake_case, function_name):
            return True, function_name
    return False, function_name


def find_false_args_and_mut(source_code):
    false_args = {}
    mutable_values = set()
    false_variables = set()
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg.startswith('_') or not arg.arg.islower():
                    if arg.arg in false_args.values():
                        continue
                    else:
                        false_args[node.lineno] = arg.arg
            function_names = node.args.defaults
            for func in function_names:
                if type(func) == ast.List or type(func) == ast.Dict or type(func) == ast.Set:
                    mutable_values.add(func.lineno)
    return false_args, mutable_values


class FalseVariableNameFinder(ast.NodeVisitor):
    def __init__(self):
        self.false_variable_names = {}

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            variable_name = node.id
            if not variable_name.islower() or not variable_name.isidentifier():
                self.false_variable_names[node.lineno] = variable_name


def find_false_variable_names(source_code):
    ast_tree = ast.parse(source_code)
    visitor = FalseVariableNameFinder()
    visitor.visit(ast_tree)
    return visitor.false_variable_names


def check_line_semicolon(line):
    line_start = line.split('#', 1)
    statement = line_start[0].strip()
    if statement.endswith(';'):
        return True
    else:
        return False


def check_ident(line):
    dedent_line = textwrap.dedent(line)
    indent_line = len(line) - len(dedent_line)
    if indent_line % 4 != 0:
        return True
    else:
        return False


def check_inline_comment(line):
    if '#' in line:
        comment_index = line.index('#')
        if comment_index == 0:
            return True
        elif 0 < comment_index < len(line) - 1 and line[comment_index - 1] == ' ' and line[comment_index - 2] == ' ':
            return True
        else:
            return False
    return True


def check_todo_comment(line):
    pattern = r'#.*TODO'
    if re.search(pattern, line, re.IGNORECASE):
        return True
    else:
        return False


if __name__ == '__main__':
    pa = arg.path
    analyse_code_path(pa)
    # path = 'test_2.py'
    # analyze_code(path)
    # line_test = """def mutable_var(self, s=[]):\n"""
    # print(check_arg_function(line_test))
