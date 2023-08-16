from typing import List

from plox_token import PloxToken

class Expr:
	def accept(self, visitor):
		pass


class Assign(Expr):
	def __init__(self, name: PloxToken, value: Expr):
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visitAssign(self)


class Binary(Expr):
	def __init__(self, left: Expr, operator: PloxToken, right: Expr):
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


class Logical(Expr):
	def __init__(self, left: Expr, operator: PloxToken, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitLogical(self)


class Unary(Expr):
	def __init__(self, operator: PloxToken, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visitUnary(self)


class Call(Expr):
	def __init__(self, callee: Expr, paren: PloxToken, arguments: List[Expr]):
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor):
		return visitor.visitCall(self)


class Get(Expr):
	def __init__(self, obj: Expr, name: PloxToken):
		self.obj = obj
		self.name = name

	def accept(self, visitor):
		return visitor.visitGet(self)


class Set(Expr):
	def __init__(self, obj: Expr, name: PloxToken, value: Expr):
		self.obj = obj
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visitSet(self)


class Parent(Expr):
	def __init__(self, keyword: PloxToken, method: PloxToken):
		self.keyword = keyword
		self.method = method

	def accept(self, visitor):
		return visitor.visitParent(self)


class This(Expr):
	def __init__(self, keyword: PloxToken):
		self.keyword = keyword

	def accept(self, visitor):
		return visitor.visitThis(self)


class Conditional(Expr):
	def __init__(self, condition: Expr, then_clause: Expr, else_clause: Expr):
		self.condition = condition
		self.then_clause = then_clause
		self.else_clause = else_clause

	def accept(self, visitor):
		return visitor.visitConditional(self)


class Variable(Expr):
	def __init__(self, name: PloxToken):
		self.name = name

	def accept(self, visitor):
		return visitor.visitVariable(self)


class FuncExpr(Expr):
	def __init__(self, params: List[PloxToken], body: list, type: str):
		self.params = params
		self.body = body
		self.type = type

	def accept(self, visitor):
		return visitor.visitFuncExpr(self)


class ExprVisitor:
	def visitAssign(self, expr: Assign):
		raise NotImplementedError

	def visitBinary(self, expr: Binary):
		raise NotImplementedError

	def visitGrouping(self, expr: Grouping):
		raise NotImplementedError

	def visitLiteral(self, expr: Literal):
		raise NotImplementedError

	def visitLogical(self, expr: Logical):
		raise NotImplementedError

	def visitUnary(self, expr: Unary):
		raise NotImplementedError

	def visitCall(self, expr: Call):
		raise NotImplementedError

	def visitGet(self, expr: Get):
		raise NotImplementedError

	def visitSet(self, expr: Set):
		raise NotImplementedError

	def visitParent(self, expr: Parent):
		raise NotImplementedError

	def visitThis(self, expr: This):
		raise NotImplementedError

	def visitConditional(self, expr: Conditional):
		raise NotImplementedError

	def visitVariable(self, expr: Variable):
		raise NotImplementedError

	def visitFuncExpr(self, expr: FuncExpr):
		raise NotImplementedError

