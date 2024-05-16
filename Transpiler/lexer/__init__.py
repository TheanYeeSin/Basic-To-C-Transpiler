from Transpiler.token import Token, TokenTypes
import sys

class Lexer:
    def __init__(self, input: str) -> None:
        self.input = input + "\n"
        self.current_char = ""
        self.current_pos = -1
        self.next_char()
    
    def next_char(self) -> None:
        """Process the next character."""
        self.current_pos += 1
        if self.current_pos >= len(self.input):
            self.current_char = "\0" # End of the file
        else:
            self.current_char = self.input[self.current_pos]
    
    def peek(self) -> str:
        """Return the next character."""
        if self.current_pos + 1 >= len(self.input):
            return "\0"
        return self.input[self.current_pos + 1]
    
    def abort(self, message: str) -> None:
        """Return error message when invalid token found."""
        sys.exit("Lexing error. Error: " + message)
    
    def skip_white_space(self) -> None:
        while self.current_char == ' ' or self.current_char == '\t' or self.current_char == '\r':
            self.next_char()
    
    def skip_comment(self) -> None:
        """Skip comments in the code."""
        if self.current_char == '#':
            while self.current_char != '\n':
                self.next_char()
    
    def get_token(self) -> Token:
        """Return the next token."""
        self.skip_white_space()
        self.skip_comment()
        
        token = None
        
        if self.current_char == '+':
            # PLUS
            token = Token(self.current_char, TokenTypes.PLUS)
        elif self.current_char == '-':
            # MINUS
            token = Token(self.current_char, TokenTypes.MINUS)
        elif self.current_char == '*':
            # ASTERISK
            token = Token(self.current_char, TokenTypes.ASTERISK)
        elif self.current_char == '/':
            # SLASH
            token = Token(self.current_char, TokenTypes.SLASH)
        elif self.current_char == '\n':
            # NEWLINE
            token = Token(self.current_char, TokenTypes.NEWLINE)
        elif self.current_char == '\0':
            # EOF
            token = Token('', TokenTypes.EOF)
        elif self.current_char == '=':
            # = or ==
            if self.peek() == '=':
                last_character = self.current_char
                self.next_char()
                token = Token(last_character + self.current_char, TokenTypes.EQEQ)
            else:
                token = Token(self.current_char, TokenTypes.EQ)
        elif self.current_char == '>':
            # > or >=
            if self.peek() == '=':
                last_character = self.current_char
                self.next_char()
                token = Token(last_character + self.current_char, TokenTypes.GTEQ)
            else:
                token = Token(self.current_char, TokenTypes.GT)
        elif self.current_char == '<':
            # < or <=
            if self.peek() == '=':
                last_character = self.current_char
                self.next_char()
                token = Token(last_character + self.current_char, TokenTypes.LTEQ)
            else:
                token = Token(self.current_char, TokenTypes.LT)
        elif self.current_char == '!':
            # != 
            if self.peek() == '=':
                last_character = self.current_char
                self.next_char()
                token = Token(last_character + self.current_char, TokenTypes.NOTEQ)
            else:
                self.abort("Expected !=, but got !" + self.peek())
        elif self.current_char == '\"':
            # Characters between quotations
            self.next_char()
            start_pos = self.current_pos
            
            while self.current_char != '\"':
                if (self.current_char == '\r' or 
                    self.current_char == '\n' or 
                    self.current_char == '\t' or 
                    self.current_char == '\\' or 
                    self.current_char == '%'):
                    self.abort("Illegar character in string.")
                self.next_char()
                
            token_text = self.input[start_pos: self.current_pos] # Get the substring
            token = Token(token_text, TokenTypes.STRING)
            
        elif self.current_char.isdigit():
            # Characters are numbers
            start_pos = self.current_pos
            while self.peek().isdigit():
                self.next_char()
                
            if self.peek() == '.': # Decimal
                self.next_char()
                
                if not self.peek().isdigit():
                    # Error
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.next_char()
            token_text = self.input[start_pos : self.current_pos + 1]
            token = Token(token_text, TokenTypes.NUMBER)
            
        elif self.current_char.isalpha():
            start_pos = self.current_pos
            while self.peek().isalnum():
                self.next_char()
                
            token_text = self.input[start_pos : self.current_pos + 1]
            keyword = Token.check_keyword(token_text)
            if keyword is None: #
                token = Token(token_text, TokenTypes.IDENT)
            else:
                token = Token(token_text, keyword)
        else:
            self.abort("Unknown token: " + self.current_char)
        
        self.next_char()
        
        return token