

class Emitter:
    def __init__(self, full_path) -> None:
        self.full_path = full_path
        self.header = ""
        self.code = ""
    
    def emit(self, code: str) -> None:
        self.code += code
        
    def emit_line(self, code: str) -> None:
        self.code += code + '\n'
        
    def header_line(self, code: str) -> None:
        self.header += code + '\n'
        
    def write_file(self) -> None:
        with open(self.full_path, 'w') as output_file:
            output_file.write(self.header + self.code)