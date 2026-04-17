"""
Утилиты для работы со строками.

Содержит функции для преобразования строк между различными форматами.
"""


def camel_to_snake(camel_str: str) -> str:
    """Convert CamelCase string to snake_case.

    Args:
        camel_str: String in CamelCase format.

    Returns:
        String in snake_case format.
    """
    if not camel_str:
        return camel_str

    snake_chars = []
    for i, char in enumerate(camel_str):
        if char.isupper() and i > 0:
            prev_char = camel_str[i - 1]
            next_char = camel_str[i + 1] if i + 1 < len(camel_str) else ""
            # Добавляем подчеркивание если:
            # 1. Предыдущий символ строчный
            # 2. Предыдущий символ цифра
            # 3. Предыдущий символ заглавный, а следующий строчный
            #    (например, "HTTPRequest")
            if (
                prev_char.islower()
                or prev_char.isdigit()
                or (prev_char.isupper() and next_char.islower())
            ):
                snake_chars.append("_")
        snake_chars.append(char.lower())
    return "".join(snake_chars)
