from enum import Enum
from typing import Optional

class Token:
    def __init__(self, token_text: str, token_type: 'TokenTypes'):
        self.text = token_text
        self.type = token_type
        
    @staticmethod
    def check_keyword(token_text: str) -> Optional[str]:
        for type in TokenTypes:
            if (type.name == token_text and 
                type.value >= 100 and 
                type.value < 200):
                return type
        return None
        

class TokenTypes(Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    
    # Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211