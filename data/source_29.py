from typing import List

def isValid(code: str) -> bool:
    if code[0] != '<' or code[-1] != '>':
        return False

    containsTag = False
    stack: List[str] = []

    def isValidCdata(s: str) -> bool:
        return s.startswith('[CDATA[')

    def isValidTagName(tagName: str, isEndTag: bool) -> bool:
        nonlocal containsTag
        if not tagName or len(tagName) > 9:
            return False
        if any(not c.isupper() for c in tagName):
            return False
        if isEndTag:
            return stack and stack.pop() == tagName
        containsTag = True
        stack.append(tagName)
        return True

    i = 0
    while i < len(code):
        if not stack and containsTag:
            return False
        if code[i] == '<':
            if i + 1 >= len(code):
                return False
            if stack and code[i + 1] == '!':
                closeIndex = code.find(']]>', i + 2)
                if closeIndex == -1 or not isValidCdata(code[i + 2:closeIndex]):
                    return False
                i = closeIndex + 3
                continue
            elif code[i + 1] == '/':
                closeIndex = code.find('>', i + 2)
                if closeIndex == -1 or not isValidTagName(code[i + 2:closeIndex], True):
                    return False
            else:
                closeIndex = code.find('>', i + 1)
                if closeIndex == -1 or not isValidTagName(code[i + 1:closeIndex], False):
                    return False
            i = closeIndex
        i += 1

    return not stack and containsTag
