error_codes = {
    None: "Ошибка не была найдена",
    "0x8010006b": "Ошибка доступа, не удалось получить пароль",
    "0x2000012e": "Подпись дублирована"
}


def get_error(error_code: str):
    if error_code in error_codes:
        return error_codes[error_code]
    return error_code