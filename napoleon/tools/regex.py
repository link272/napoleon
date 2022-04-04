import re

TO_SNAKE_REGEX = rx = re.compile(r"\W+")


def to_snake(string):
    return TO_SNAKE_REGEX.sub(" ", string).strip().lower().replace(" ", "_")


TO_SNAKE_V2_REGEX = re.compile(r'(?<!^)(?=[A-Z])')


def to_snake_v2(string):
    return TO_SNAKE_V2_REGEX.sub('_', string).lower()
