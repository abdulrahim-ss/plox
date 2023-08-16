from typing import List

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


class If(Stmt):
	def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch

	def accept(self, visitor):
		return visitor.visitIf(self)


class While(Stmt):
	def __init__(self, condition: Expr, body: Stmt):
		self.condition = condition
		self.body = body

	def accept(self, visitor):
		return visitor.visitWhile(self)


class Print(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrint(self)


class Block(Stmt):
	def __init__(self, statements: List[Stmt]):
		self.statements = statements

	def accept(self, visitor):
		return visitor.visitBlock(self)


class Var(Stmt):
	def __init__(self, name: PloxToken, Initializer: Expr):
		self.name = name
		self.Initializer = Initializer

	def accept(self, visitor):
		return visitor.visitVar(self)


class Function(Stmt):
	def __init__(self, name: PloxToken, function: Expr):
		self.name = name
		self.function = function

	def accept(self, visitor):
		return visitor.visitFunction(self)


class Return(Stmt):
	def __init__(self, keyword: PloxToken, value: Expr):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor):
		return visitor.visitReturn(self)


class Break(Stmt):
	def __init__(self):
		pass

	def accept(self, visitor):
		return visitor.visitBreak(self)


class Continue(Stmt):
	def __init__(self):
		pass

	def accept(self, visitor):
		return visitor.visitContinue(self)


class ClassStmt(Stmt):
	def __init__(self, name: PloxToken, methods: List[Function]):
		self.name = name
		self.methods = methods

	def accept(self, visitor):
		return visitor.visitClassStmt(self)


class Empty(Stmt):
	def __init__(self):
		pass

	def accept(self, visitor):
		return visitor.visitEmpty(self)


class StmtVisitor:
	def visitExpression(self, stmt: Expression):
		raise NotImplementedError

	def visitIf(self, stmt: If):
		raise NotImplementedError

	def visitWhile(self, stmt: While):
		raise NotImplementedError

	def visitPrint(self, stmt: Print):
		raise NotImplementedError

	def visitBlock(self, stmt: Block):
		raise NotImplementedError

	def visitVar(self, stmt: Var):
		raise NotImplementedError

	def visitFunction(self, stmt: Function):
		raise NotImplementedError

	def visitReturn(self, stmt: Return):
		raise NotImplementedError

	def visitBreak(self, stmt: Break):
		raise NotImplementedError

	def visitContinue(self, stmt: Continue):
		raise NotImplementedError

	def visitClassStmt(self, stmt: ClassStmt):
		raise NotImplementedError

	def visitEmpty(self, stmt: Empty):
		raise NotImplementedError

