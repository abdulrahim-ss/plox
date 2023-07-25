from Expr import *
from token import Token
from tokenType import TokenType, TokenType as TT

class AstPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visitBinary(self, expr: Binary) -> str:
        return self.paranthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visitGrouping(self, expr: Grouping) -> str:
        return self.paranthesize("group", expr.expression)

    def visitLiteral(self, expr: Literal) -> str:
        if expr.value == None: return "nill"
        return str(expr.value)
    
    def visitUnary(self, expr: Unary) -> str:
        return self.paranthesize(expr.operator.lexeme, expr.right)

    def paranthesize(self, name: str, *exprs: Expr) -> str:
        output = "(" + name
        for expr in exprs:
            output += " " + expr.accept(self)
        output += ")"
        return output


class RPNPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visitBinary(self, expr: Binary) -> str:
        return expr.left.accept(self) + " " + expr.right.accept(self) + " " + expr.operator.lexeme
    
    def visitGrouping(self, expr: Grouping) -> str:
        return expr.expression.accept(self)

    def visitLiteral(self, expr: Literal) -> str:
        if expr.value == None: return "nill"
        return str(expr.value)
    
    def visitUnary(self, expr: Unary) -> str:
        op = expr.operator
        op = "~" if op.type == TT.MINUS else op.lexeme
        return op + expr.right.accept(self)



if __name__ == "__main__":
    expression = Binary(
        Unary(
            Token(TT.MINUS, "-", None, 1),
            Literal(123)
        ),
        Token(TT.STAR, "*", None, 1),
        Grouping(Literal(45.67))
    )

    expression2 = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal("str")
        )
    )

    ast_printer = AstPrinter()
    rpn_printer = RPNPrinter()
    print(ast_printer.print(expression))
    print(rpn_printer.print(expression))
