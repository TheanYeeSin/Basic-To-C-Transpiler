import sys
from Transpiler.lexer import Lexer
from Transpiler.emitter import Emitter
from Transpiler.token import TokenTypes, Token

class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter
        
        self.symbols = set() # Variables declared so far
        self.labels_declared = set() # Labels declared so far.
        self.labels_gotoed = set() # Labels goto'ed so far.
        
        self.current_token: Token = None
        self.peek_token: Token = None
        self.next_token()
        self.next_token()
    
    def check_token(self, type: TokenTypes) -> bool:
        """Return true if the current token matches."""
        return type == self.current_token.type
    
    def check_peek(self, type: TokenTypes) -> bool:
        """Return true if the next token matches."""
        return type == self.peek_token.type
    
    def match(self, type: TokenTypes) -> None:
        """Try to match current token. If not, error, Advances the current token."""
        if not self.check_token(type):
            self.abort("Expected " + type.name + ", got " + self.current_token.type.name)
        self.next_token()
    
    def next_token(self) -> None:
        """Advances the current token."""
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()
    
    def abort(self, message: str) -> None:
        """Return error message"""
        sys.exit("Parser error. Error: " + message)
        
    # Production rules.
    
    def program(self) -> None:
        # program ::= {statement}
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void) {")
        
        while self.check_token(TokenTypes.NEWLINE):
            self.next_token()
        
        while not self.check_token(TokenTypes.EOF):
            self.statement()
            
        # Wraping
        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")
            
        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO to undeclared label: " + label)
        
            
    def statement(self) -> None:
        # Check the first token to see what kind of statement this is.
        
        # "PRINT" (expression | string)
        if self.check_token(TokenTypes.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()
            
            if self.check_token(TokenTypes.STRING):
                # Simple string.
                self.emitter.emit_line("printf(\"" + self.current_token.text + "\\n\");")
                self.next_token()
            else:
                # Expect an expression.
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit_line("));")
                
        # "IF" comparison "THEN" {statement} "ENDIF"
        elif self.check_token(TokenTypes.IF):
            print("STATEMENT-IF")
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()
            
            self.match(TokenTypes.THEN)
            self.nl()
            self.emitter.emit_line("){")
            
            while not self.check_token(TokenTypes.ENDIF):
                self.statement()
                
            self.match(TokenTypes.ENDIF)
            self.emitter.emit_line("}")
            
        # "WHILE" comparison "REPEAT" {statement} "ENDWHILE"
        elif self.check_token(TokenTypes.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.emitter.emit("while(")
            self.comparison()
            
            self.match(TokenTypes.REPEAT)
            self.nl()
            self.emitter.emit_line("){")
            
            while not self.check_token(TokenTypes.ENDWHILE):
                self.statement()
                
            self.match(TokenTypes.ENDWHILE)
            self.emitter.emit_line("}")
            
        # "LABEL" ident
        elif self.check_token(TokenTypes.LABEL):
            print("STATEMENT-LABEL")
            self.next_token()
            
            if self.current_token.text in self.labels_declared:
                self.abort("Label already exists: " + self.current_token.text)
                
            self.labels_declared.add(self.current_token.text)
            
            self.emitter.emit_line(self.current_token.text + ":")
            self.match(TokenTypes.IDENT)
            
        # "GOTO" ident
        elif self.check_token(TokenTypes.GOTO):
            print("STATEMENT-GOTO")
            self.next_token()
            self.labels_gotoed.add(self.current_token.text)
            self.emitter.emit_line("goto " + self.current_token.text + ";")
            self.match(TokenTypes.IDENT)
            
        # "LET" ident "=" expression
        elif self.check_token(TokenTypes.LET):
            print("STATEMENT-LET")
            self.next_token()
            
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.header_line("float " + self.current_token.text + ";")
            
            self.emitter.emit(self.current_token.text + " = ")
            self.match(TokenTypes.IDENT)
            self.match(TokenTypes.EQ)
            self.expression()
            self.emitter.emit_line(";")
            
        # "INPUT" ident
        elif self.check_token(TokenTypes.INPUT):
            print("STATEMENT-INPUT")
            self.next_token()
            
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.header_line("float " + self.current_token.text + ";")
                
            self.emitter.emit_line("if(0 == scanf(\"%" + "f\", &" + self.current_token.text + ")) {")
            self.emitter.emit_line(self.current_token.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emit_line("*s\");")
            self.emitter.emit_line("}")
            self.match(TokenTypes.IDENT)
        
        # Invalid statement. Error!
        else:
            self.abort("Invalid statement at " + self.current_token.text + " (" + self.current_token.type.name + ")")
        
        # Newline.
        self.nl()
        
    def nl(self) -> None:
        print("NEWLINE")
        
        # Require at least one newline.
        self.match(TokenTypes.NEWLINE)
        
        # But we will allow extra newlines too, of course
        while self.check_token(TokenTypes.NEWLINE):
            self.next_token()
            
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self) -> None:
        print("COMPARISON")
        
        self.expression()
        
        if self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.expression()
            
        else:
            self.abort("Expected comparison operator at: " + self.current_token.text)
            
        while self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.expression()
            
    def is_comparison_operator(self) -> bool:
        """Return true if the current token is a comparison operator."""
        return (self.check_token(TokenTypes.GT) or
                self.check_token(TokenTypes.GTEQ) or
                self.check_token(TokenTypes.LT) or
                self.check_token(TokenTypes.LTEQ) or
                self.check_token(TokenTypes.EQEQ) or
                self.check_token(TokenTypes.NOTEQ))
    
    # expression ::= term {( "-" | "+" ) term}    
    def expression(self) -> None:
        print("EXPRESSION")
        self.term()
        
        # Can have more than 1 terms with (+/-)
        while self.check_token(TokenTypes.PLUS) or self.check_token(TokenTypes.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.term()
       
    # term ::= unary {( "/" | "*" ) unary}     
    def term(self) -> None:
        print("TERM")
        
        self.unary()
        
        # Can have more than 1 unaries
        while self.check_token(TokenTypes.ASTERISK) or self.check_token(TokenTypes.SLASH):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.unary()
            
    # unary ::= ["+" | "-"] primary
    def unary(self) -> None:
        print("UNARY")
        
        # Optional unary +/-
        if self.check_token(TokenTypes.PLUS) or self.check_token(TokenTypes.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        self.primary()
        
    # primary ::= number | ident
    def primary(self) -> None:
        print("PRIMARY (" + self.current_token.text + ")")
        
        if self.check_token(TokenTypes.NUMBER):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        elif self.check_token(TokenTypes.IDENT):
            # Ensure the variable already exists.
            if self.current_token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.current_token.text)
            self.emitter.emit(self.current_token.text)
            self.next_token()
        else:
            # Error
            self.abort("Unexpected token at " + self.current_token.text)
            
    
            
    
        
        