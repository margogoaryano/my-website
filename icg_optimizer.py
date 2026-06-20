# ============================================================
# KOMPONEN 4: ICG - INTERMEDIATE CODE GENERATOR
# Menghasilkan Three Address Code (TAC)
#
# KOMPONEN 5: OPTIMIZER
# Teknik optimasi:
#   1. Constant Folding  – hitung ekspresi konstanta saat compile
#   2. Dead Code Elim.   – hapus kode yang tidak pernah dieksekusi
# ============================================================

from ast_nodes import *


# ── Instruksi TAC ───────────────────────────────────────────
class TACInstruction:
    """
    Format: result = arg1 op arg2
    Atau bentuk khusus: LABEL, GOTO, IF GOTO, PARAM, CALL, PRINT, READ
    """
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op     = op
        self.arg1   = arg1
        self.arg2   = arg2
        self.result = result

    def __str__(self):
        op = self.op
        if op == 'ASSIGN':
            return f'\t{self.result} := {self.arg1}'
        if op == 'BINOP':
            return f'\t{self.result} := {self.arg1} {self.arg2[0]} {self.arg2[1]}'
        if op == 'UNARY':
            return f'\t{self.result} := {self.arg1} {self.arg2}'   # arg1=op, arg2=operand
        if op == 'LABEL':
            return f'{self.result}:'
        if op == 'GOTO':
            return f'\tGOTO {self.result}'
        if op == 'IF_FALSE':
            return f'\tIF_FALSE {self.arg1} GOTO {self.result}'
        if op == 'PRINT':
            return f'\tPRINT {self.arg1}'
        if op == 'READ':
            return f'\tREAD {self.result}'
        return f'\t{op} {self.arg1} {self.arg2} -> {self.result}'


# ── Generator TAC ───────────────────────────────────────────
class ICGGenerator:
    def __init__(self):
        self.instructions = []
        self._temp_count  = 0
        self._label_count = 0

    def _new_temp(self) -> str:
        self._temp_count += 1
        return f't{self._temp_count}'

    def _new_label(self) -> str:
        self._label_count += 1
        return f'L{self._label_count}'

    def _emit(self, op, arg1=None, arg2=None, result=None):
        instr = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr

    # ── entry ────────────────────────────────────────────────
    def generate(self, ast: ProgramNode):
        self._visit_block(ast.block)
        return self.instructions

    # ── visitor ─────────────────────────────────────────────
    def _visit_block(self, node: BlockNode):
        for stmt in node.statements:
            self._visit_stmt(stmt)

    def _visit_stmt(self, node):
        if node is None:
            return
        if isinstance(node, AssignNode):
            self._visit_assign(node)
        elif isinstance(node, IfNode):
            self._visit_if(node)
        elif isinstance(node, WhileNode):
            self._visit_while(node)
        elif isinstance(node, WritelnNode):
            self._visit_writeln(node)
        elif isinstance(node, ReadlnNode):
            self._visit_readln(node)
        elif isinstance(node, BlockNode):
            self._visit_block(node)

    def _visit_assign(self, node: AssignNode):
        src = self._visit_expr(node.expr)
        self._emit('ASSIGN', arg1=src, result=node.var_name)

    def _visit_if(self, node: IfNode):
        cond  = self._visit_expr(node.condition)
        l_else  = self._new_label()
        l_end   = self._new_label()

        self._emit('IF_FALSE', arg1=cond, result=l_else)
        self._visit_stmt(node.then_stmt)
        if node.else_stmt:
            self._emit('GOTO', result=l_end)
        self._emit('LABEL', result=l_else)
        if node.else_stmt:
            self._visit_stmt(node.else_stmt)
            self._emit('LABEL', result=l_end)

    def _visit_while(self, node: WhileNode):
        l_start = self._new_label()
        l_end   = self._new_label()

        self._emit('LABEL', result=l_start)
        cond = self._visit_expr(node.condition)
        self._emit('IF_FALSE', arg1=cond, result=l_end)
        self._visit_stmt(node.body)
        self._emit('GOTO', result=l_start)
        self._emit('LABEL', result=l_end)

    def _visit_writeln(self, node: WritelnNode):
        for arg in node.args:
            val = self._visit_expr(arg)
            self._emit('PRINT', arg1=val)

    def _visit_readln(self, node: ReadlnNode):
        for name in node.args:
            self._emit('READ', result=name)

    # ── expression → returns temp/value name ────────────────
    def _visit_expr(self, node) -> str:
        if isinstance(node, IntLiteralNode):
            return str(node.value)
        if isinstance(node, BoolLiteralNode):
            return 'true' if node.value else 'false'
        if isinstance(node, StringLiteralNode):
            return f'"{node.value}"'
        if isinstance(node, VarNode):
            return node.name
        if isinstance(node, UnaryOpNode):
            return self._visit_unary(node)
        if isinstance(node, BinOpNode):
            return self._visit_binop(node)
        return '?'

    def _visit_unary(self, node: UnaryOpNode) -> str:
        operand = self._visit_expr(node.operand)
        t = self._new_temp()
        self._emit('UNARY', arg1=node.op, arg2=operand, result=t)
        return t

    def _visit_binop(self, node: BinOpNode) -> str:
        left  = self._visit_expr(node.left)
        right = self._visit_expr(node.right)
        t     = self._new_temp()
        self._emit('BINOP', arg1=left, arg2=(node.op, right), result=t)
        return t


# ============================================================
# KOMPONEN 5: OPTIMIZER
# ============================================================

class Optimizer:
    def __init__(self, instructions: list):
        self.instructions = instructions[:]

    def optimize(self) -> list:
        self.instructions = self._constant_folding(self.instructions)
        self.instructions = self._dead_code_elimination(self.instructions)
        return self.instructions

    # ── Teknik 1: Constant Folding ──────────────────────────
    # Hitung ekspresi dengan dua operand konstanta saat compile time
    def _constant_folding(self, instrs: list) -> list:
        result = []
        for instr in instrs:
            if instr.op == 'BINOP':
                left  = instr.arg1
                op, right = instr.arg2
                lv = self._try_int(left)
                rv = self._try_int(right)
                if lv is not None and rv is not None:
                    folded = self._eval_binop(op, lv, rv)
                    if folded is not None:
                        # Ganti dengan ASSIGN langsung
                        new_instr = TACInstruction('ASSIGN', arg1=str(folded), result=instr.result)
                        result.append(new_instr)
                        continue
            result.append(instr)
        return result

    def _try_int(self, val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def _eval_binop(self, op, a, b):
        try:
            if op == '+':   return a + b
            if op == '-':   return a - b
            if op == '*':   return a * b
            if op == 'div': return a // b if b != 0 else None
            if op == 'mod': return a % b  if b != 0 else None
            if op == '=':   return 1 if a == b else 0
            if op == '<>':  return 1 if a != b else 0
            if op == '<':   return 1 if a < b  else 0
            if op == '>':   return 1 if a > b  else 0
            if op == '<=':  return 1 if a <= b else 0
            if op == '>=':  return 1 if a >= b else 0
        except Exception:
            pass
        return None

    # ── Teknik 2: Dead Code Elimination ─────────────────────
    # Hapus instruksi setelah GOTO tanpa ada LABEL yang menargetkan ke sana
    def _dead_code_elimination(self, instrs: list) -> list:
        result   = []
        dead     = False
        labels   = {i.result for i in instrs if i.op == 'LABEL'}

        for instr in instrs:
            if instr.op == 'LABEL':
                dead = False   # label baru → kode kembali aktif
                result.append(instr)
            elif dead:
                pass   # buang instruksi mati
            else:
                result.append(instr)
                if instr.op == 'GOTO':
                    dead = True   # setelah GOTO tanpa kondisi, kode mati

        return result
