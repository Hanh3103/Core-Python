# write your code here
import re


def input_modi(input_all):
    strings = input_all.split("|")
    string_input = strings[1]
    regex = strings[0]
    return regex, string_input


def compare_string_one_character(character, regex):
    if (len(regex) == 0) or regex == ".":
        return True
    elif len(regex) > 0 and len(character) == 0:
        return False
    else:
        return regex == character


def match_equal_length(regex: str, in_string: str) -> bool:
    if len(regex) == 0:  # regex has been totally consumed
        return True
    elif len(in_string) == 0:  # regex is longer than the input string
        return False
    elif regex[0] in ["?", "*"]:
        return match_equal_length(regex[1:], in_string)
    elif len(regex) >= 2 and regex[1] == '?' and regex[0] != "\\":
        return match_question(regex, in_string)
    elif len(regex) >= 2 and regex[1] == "*" and regex[0] != "\\":
        return match_stern(regex, in_string)
    elif len(regex) >= 2 and regex[1] == "+" and regex[0] != "\\":
        return match_plus(regex, in_string)
    elif regex.startswith("\\"):
        # Escape sequence, match the following character as a literal
        if len(regex) > 1 and compare_string_one_character(in_string[0], regex[1]):
            return match_equal_length(regex[2:], in_string[1:])
        else:
            return False
    elif not compare_string_one_character(in_string[0], regex[0]):
        return False
    else:
        return match_equal_length(regex[1:], in_string[1:])


def match_question(regex: str, in_str: str) -> bool:
    if compare_string_one_character(in_str[0], regex[0]):
        return match_equal_length(regex[2:], in_str[1:])
    else:
        return match_equal_length(regex[1:], in_str)


def match_stern(regex: str, in_string: str) -> bool:
    if compare_string_one_character(in_string[0], regex[0]):
        if len(regex[2:]) != 0:
            return match_equal_length(regex[2:], in_string[(len(in_string) - len(regex[2:])):])
        if len(regex[2:]) == 0:
            return not match_equal_length(regex, in_string[1:])
    else:
        return match_equal_length(regex[1:], in_string)


def match_plus(regex: str, in_string: str) -> bool:
    # Occur 1 times
    if compare_string_one_character(in_string[0], regex[0]) and (len(in_string[1:]) == len(regex[2:])):
        return match_equal_length(regex[2:], in_string[1:])
    elif compare_string_one_character(in_string[0], regex[0]):
        if len(regex[2:]) != 0:
            return match_equal_length(regex[2:], in_string[(len(in_string) - len(regex[2:])):])
        if len(regex[2:]) == 0:
            return match_equal_length(regex, in_string[1:])
    else:
        return match_equal_length(regex[1:], in_string)


def match_string_suffix(regex: str, in_string: str) -> bool:
    if regex.startswith("\\"):
        regex = regex[1:]
    if len(in_string) == 0 and len(regex) != 0:
        return False
    if len(in_string) >= len(regex) and match_equal_length(regex, in_string[:len(regex)]):
        return True
    else:
        return match_string_suffix(regex, in_string[1:])


def match_special_case(regex: str, in_str: str) -> bool:
    if regex.startswith('^'):
        regex = regex[1:]
        if regex.endswith('$'):
            regex = regex[:-1]
            regex_tmp = r'.*[?*+].*'
            if (not re.match(regex_tmp, regex)) and len(regex) == len(in_str):
                return match_equal_length(regex, in_str)
            elif re.match(regex_tmp, regex):
                return match_equal_length(regex, in_str)
            else:
                return False
        else:
            return match_equal_length(regex, in_str[:len(regex)])
    elif regex.endswith('$'):
        regex = regex[:-1]
        if regex[0] == '\\':
            return match_equal_length(regex[1:], in_str[(len(in_str) - len(regex[1:])):])
        else:
            return match_equal_length(regex, in_str[(len(in_str) - len(regex)):])
    else:
        return match_string_suffix(regex, in_str) or match_equal_length(regex, in_str)


if __name__ == '__main__':
    user_input = input()
    reg, string_in = input_modi(user_input)
    re = match_special_case(reg, string_in)
    print(re)
