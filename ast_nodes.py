# ============================================================
# KOMPONEN 2 (bagian A): DEFINISI NODE AST
# Abstract Syntax Tree untuk MiniPascal
# ============================================================

class ASTNode:
    """Kelas dasar semua node AST."""
    pass

# ── Program ─────────────────────────────────────────────────
class ProgramNode(ASTNode):
    def __init__(self, name, var_decl, block):
        self.name     = name       # nama program
        self.var_decl = var_decl   # list VarDeclNode
        self.block    = block      # BlockNode (begin…end)

# ── Deklarasi Variabel ───────────────────────────────────────
class VarDeclNode(ASTNode):
    def __init__(self, names, type_name, line):
        self.names     = names      # list nama variabel
        self.type_name = type_name  # 'integer' | 'boolean' | 'string'
        self.line      = line

# ── Blok (begin…end) ────────────────────────────────────────
class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements   # list statement

# ── Statement: Assignment ────────────────────────────────────
class AssignNode(ASTNode):
    def __init__(self, var_name, expr, line):
        self.var_name = var_name
        self.expr     = expr
        self.line     = line

# ── Statement: If-Then-Else ──────────────────────────────────
class IfNode(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt, line):
        self.condition  = condition
        self.then_stmt  = then_stmt
        self.else_stmt  = else_stmt   # None jika tidak ada else
        self.line       = line

# ── Statement: While-Do ─────────────────────────────────────
class WhileNode(ASTNode):
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body      = body
        self.line      = line

# ── Statement: Writeln ───────────────────────────────────────
class WritelnNode(ASTNode):
    def __init__(self, args, line):
        self.args = args   # list ekspresi
        self.line = line

# ── Statement: Readln ────────────────────────────────────────
class ReadlnNode(ASTNode):
    def __init__(self, args, line):
        self.args = args   # list nama variabel
        self.line = line

# ── Ekspresi: Operasi Biner ──────────────────────────────────
class BinOpNode(ASTNode):
    def __init__(self, left, op, right, line):
        self.left  = left
        self.op    = op    # string operator: '+', '-', '*', 'div', dll
        self.right = right
        self.line  = line

# ── Ekspresi: Operasi Unary ──────────────────────────────────
class UnaryOpNode(ASTNode):
    def __init__(self, op, operand, line):
        self.op      = op       # '-' atau 'not'
        self.operand = operand
        self.line    = line

# ── Ekspresi: Literal Integer ────────────────────────────────
class IntLiteralNode(ASTNode):
    def __init__(self, value, line):
        self.value = value   # int
        self.line  = line

# ── Ekspresi: Literal Boolean ────────────────────────────────
class BoolLiteralNode(ASTNode):
    def __init__(self, value, line):
        self.value = value   # True / False
        self.line  = line

# ── Ekspresi: Literal String ─────────────────────────────────
class StringLiteralNode(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line  = line

# ── Ekspresi: Nama Variabel ──────────────────────────────────
class VarNode(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line
