import re
from datetime import datetime


class SignParser:
    def __init__(self):
        self._RE_ERROR_CODE = re.compile(r"(?<=\[ErrorCode:\s)\dx\d{8}(?=\])")
        self._RE_SPLIT = re.compile(r"(?<=\d-{7}\n)(.*?)(?=\d-{7}\n|={9})", re.DOTALL)

        _RE_SNILS = re.compile(r"(?<=(SNILS|СНИЛС)=)\d+")
        self._RE_SN = re.compile(r"(?<=SN=)\w+")
        self._RE_G = re.compile(r"(?<=G=)\w+\s\w+")
        _RE_SHA = re.compile(r"SHA1\s(Hash|отпечаток)\s*:\s*(\w*?)(?=\n)")
        _RE_BEFORE = re.compile(r"(Not valid before|Выдан)\s*:\s*(.*?)(?=\n)", re.DOTALL)
        _RE_AFTER = re.compile(r"(Not valid after|Истекает)\s*:\s*(.*?)(?=\n)", re.DOTALL)
        _RE_T = re.compile(r"(?<=\sT=)[^,]+")

        self._titles = ["snils", "sha", "t", "before", "after"]
        self._regexps = [_RE_SNILS, _RE_SHA, _RE_T, _RE_BEFORE, _RE_AFTER]

        self._find_keys = ["snils", "name"]
        self._required_keys = ["snils", "sn", "g", "before", "after"]

        self._signs = []
        self._error_code = ""
        self._signs_unparsed = []
        self._is_error = False

        self._date_format = "%d/%m/%Y %H:%M:%S UTC"
    
    def parse(self, text):
        self._error_code = self.get_error_code(text)
        self._is_error = self.check_is_error(self._error_code)

        if self._is_error:
            return f"Получена ошибка: {self._error_code}"
        
        self._signs_unparsed = re.findall(self._RE_SPLIT, text)
        if not self._signs_unparsed:
            return "Не найдено ни одной подписи"
        
        double_snils = {}
        for sign_unparsed in self._signs_unparsed:
            sign_parsed = self._parse_one_sign(sign_unparsed)
            if sign_parsed:
                if sign_parsed["snils"] in double_snils:
                    double_snils[sign_parsed["snils"]] += 1
                else:
                    double_snils[sign_parsed["snils"]] = 1
                self._signs.append(sign_parsed)
        
        for sign in self._signs:
            if double_snils[sign["snils"]] > 1:
                sign["double"] = True
            else:
                sign["double"] = False
        
        for snils, _ in list(filter(lambda x: x[0] if x[1] > 1 else None, double_snils.items())):
            same_signs_list = list(sorted(self.get_signs(key=snils), key=lambda x: x["before"]))
            for sign in self._signs:
                if sign["snils"] == snils:
                    if sign == same_signs_list[-1]:
                        sign["new"] = True
                    else:
                        sign["new"] = False

        if not self._signs:
            return "Произошла ошибка при парсинге подписей"
        
        return

    def _parse_one_sign(self, text):
        sign = {}
        for title, regexp in zip(self._titles, self._regexps):
            match = re.search(regexp, text)
            if match:
                if len(match.groups()) <= 1:
                    sign[title] = match.group()
                else:
                    if title in ["before", "after"]:
                        sign[title] = datetime.strptime(match.group(2), self._date_format)
                        if title == "after":
                            sign["expired"] = sign["after"] < datetime.now()
                    else:
                        sign[title] = match.group(2)
            else:
                if title in self._required_keys:
                    return None
                
        g = re.search(self._RE_G, text).group()
        sn = re.search(self._RE_SN, text).group()
        sign["name"] = sn + " " + g

        return sign
    
    def get_error_code(self, text=""):
        if not text:
            return self._error_code
        else:
            match = re.search(self._RE_ERROR_CODE, text)
            if match:
                return match.group()

    def get_signs(self, key=""):
        if not key:
            return self._signs
        else:
            if "," in key:
                keys = key.split(",")
            else:
                keys = [key]
            found_signs = []
            for key in keys:
                key = key.strip()
                for sign in self._signs:
                    for find_key in self._find_keys:
                        if key.lower() in sign[find_key].lower():
                            found_signs.append(sign)
                            continue
            return found_signs
    
    def get_doubles(self):
        return list(sorted(filter(lambda x: x["double"], self._signs), key=lambda x: x["snils"]))
                
    @staticmethod
    def check_is_error(error_code):
        return error_code != "0x00000000"

if __name__ == "__main__":
    with open("signs.txt", 'r') as file:
        text = file.read()
    
    parser = SignParser()
    print(parser.parse(text))
    print(*parser.get_signs(), sep="\n")
    # print(*parser.get_doubles(), sep="\n")
    