# Example Visitors
from Expr import *
from plox_token import PloxToken
from tokenType import TokenType, TokenType as TT

class AstPrinter(ExprVisitor):
    def stringify(self, expr: Expr) -> str:
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
    
    def visitConditional(self, expr: Conditional):
        pass

    def paranthesize(self, name: str, *exprs: Expr) -> str:
        output = "(" + name
        for expr in exprs:
            try:
                x = expr.accept(self)
            except:
                x = "[INVALID]"
            output += " " + x
        output += ")"
        return output


class RPNPrinter(ExprVisitor):
    def stringify(self, expr: Expr) -> str:
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
            PloxToken(TT.MINUS, "-", None, 1),
            Literal(123)
        ),
        PloxToken(TT.STAR, "*", None, 1),
        Grouping(Literal(45.67))
    )

    expression2 = Binary(
        Unary(
            PloxToken(TokenType.MINUS, "-", None, 1),
            Literal(123)
        ),
        PloxToken(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal("str")
        )
    )

    ast_printer = AstPrinter()
    rpn_printer = RPNPrinter()
    print(ast_printer.stringify(expression))
    print(rpn_printer.stringify(expression))
