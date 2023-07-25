from token import Token

class Expr:
	def accept(self, visitor):
		pass


class Binary(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitBinary(self)


class Grouping(Expr):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitGrouping(self)


class Literal(Expr):
	def __init__(self, value: object):
		self.value = value

	def accept(self, visitor):
		return visitor.visitLiteral(self)


class Unary(Expr):
	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitUnary(self)


class ExprVisitor:
	def visitBinary(self, expr:Binary):
		raise NotImplementedError

	def visitGrouping(self, expr:Grouping):
		raise NotImplementedError

	def visitLiteral(self, expr:Literal):
		raise NotImplementedError

	def visitUnary(self, expr:Unary):
		raise NotImplementedError

