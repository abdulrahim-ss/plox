from plox_token import PloxToken
from Expr import Expr


class Stmt:
	def accept(self, visitor):
		pass


class Expression(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitExpression(self)


class Print(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrint(self)


class Var(Stmt):
	def __init__(self, name: PloxToken, Initializer: Expr):
		self.name = name
		self.Initializer = Initializer

	def accept(self, visitor):
		return visitor.visitVar(self)


class StmtVisitor:
	def visitExpression(self, expr:Expression):
		raise NotImplementedError

	def visitPrint(self, expr:Print):
		raise NotImplementedError

	def visitVar(self, expr:Var):
		raise NotImplementedError

