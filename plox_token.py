from tokenType import TokenType


class PloxToken:
    def __init__(self, type:TokenType, lexeme:str, literal:object, line:int) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"
    
    def __repr__(self) -> str:
        return self.__str__()