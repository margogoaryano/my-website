# ============================================================
# KOMPONEN 3: SEMANTIC ANALYZER
# - Membangun Symbol Table
# - Memeriksa tipe data (type checking)
# - Memastikan variabel dideklarasikan sebelum dipakai
# ============================================================

from ast_nodes import *


class SemanticError(Exception):
    def __init__(self, msg, line):
        super().__init__(f'[Baris {line}] Error Semantik: {msg}')
        self.line = line


# ── Symbol Table ────────────────────────────────────────────
class SymbolTable:
    """
    Menyimpan informasi variabel: nama → tipe
    Contoh: {'x': 'integer', 'flag': 'boolean'}
    """
    def __init__(self):
        self.symbols = {}   # nama_var → tipe

    def declare(self, name: str, dtype: str, line: int):
        if name in self.symbols:
            raise SemanticError(f'variabel "{name}" sudah dideklarasikan', line)
        self.symbols[name] = dtype

    def lookup(self, name: str, line: int) -> str:
        if name not in self.symbols:
            raise SemanticError(f'variabel "{name}" belum dideklarasikan', line)
        return self.symbols[name]

    def display(self):
        print('\n╔══════════════════════════════╗')
        print('║        SYMBOL TABLE          ║')
        print('╠══════════════════╦═══════════╣')
        print('║ Nama Variabel    ║ Tipe      ║')
        print('╠══════════════════╬═══════════╣')
        for name, dtype in self.symbols.items():
            print(f'║ {name:<16}  ║ {dtype:<9} ║')
        print('╚══════════════════╩═══════════╝')


# ── Type mapping dari keyword ke nama tipe ──────────────────
TYPE_MAP = {
    'integer_kw' : 'integer',
    'boolean_kw' : 'boolean',
    'string_kw'  : 'string',
    'integer'    : 'integer',   # sudah terpetakan
    'boolean'    : 'boolean',
    'string'     : 'string',
}


# ── Semantic Analyzer utama ─────────────────────────────────
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors       = []

    def analyze(self, ast: ProgramNode):
        if ast is None:
            return
        try:
            self._visit_program(ast)
        except SemanticError as e:
            self.errors.append(str(e))

    # ── visitor ─────────────────────────────────────────────
    def _visit_program(self, node: ProgramNode):
        # Daftarkan semua variabel ke symbol table
        for decl in node.var_decl:
            self._visit_var_decl(decl)
        # Analisis blok utama
        self._visit_block(node.block)

    def _visit_var_decl(self, node: VarDeclNode):
        dtype = TYPE_MAP.get(node.type_name, node.type_name)
        for name in node.names:
            try:
                self.symbol_table.declare(name, dtype, node.line)
            except SemanticError as e:
                self.errors.append(str(e))

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
        try:
            var_type  = self.symbol_table.lookup(node.var_name, node.line)
            expr_type = self._infer_type(node.expr)
            if var_type != expr_type:
                raise SemanticError(
                    f'tidak cocok tipe: variabel "{node.var_name}" bertipe {var_type} '
                    f'tapi ekspresi bertipe {expr_type}',
                    node.line
                )
        except SemanticError as e:
            self.errors.append(str(e))

    def _visit_if(self, node: IfNode):
        try:
            cond_type = self._infer_type(node.condition)
            if cond_type != 'boolean':
                raise SemanticError(
                    f'kondisi if harus bertipe boolean, bukan {cond_type}',
                    node.line
                )
        except SemanticError as e:
            self.errors.append(str(e))
        self._visit_stmt(node.then_stmt)
        if node.else_stmt:
            self._visit_stmt(node.else_stmt)

    def _visit_while(self, node: WhileNode):
        try:
            cond_type = self._infer_type(node.condition)
            if cond_type != 'boolean':
                raise SemanticError(
                    f'kondisi while harus bertipe boolean, bukan {cond_type}',
                    node.line
                )
        except SemanticError as e:
            self.errors.append(str(e))
        self._visit_stmt(node.body)

    def _visit_writeln(self, node: WritelnNode):
        for arg in node.args:
            try:
                self._infer_type(arg)   # pastikan ekspresi valid
            except SemanticError as e:
                self.errors.append(str(e))

    def _visit_readln(self, node: ReadlnNode):
        for name in node.args:
            try:
                self.symbol_table.lookup(name, node.line)
            except SemanticError as e:
                self.errors.append(str(e))

    # ── Type inference ───────────────────────────────────────
    def _infer_type(self, node) -> str:
        if isinstance(node, IntLiteralNode):
            return 'integer'
        if isinstance(node, BoolLiteralNode):
            return 'boolean'
        if isinstance(node, StringLiteralNode):
            return 'string'
        if isinstance(node, VarNode):
            return self.symbol_table.lookup(node.name, node.line)
        if isinstance(node, UnaryOpNode):
            return self._infer_unary(node)
        if isinstance(node, BinOpNode):
            return self._infer_binop(node)
        return 'unknown'

    def _infer_unary(self, node: UnaryOpNode) -> str:
        operand_type = self._infer_type(node.operand)
        if node.op == '-':
            if operand_type != 'integer':
                raise SemanticError(
                    f'operator "-" hanya berlaku untuk integer, bukan {operand_type}',
                    node.line
                )
            return 'integer'
        if node.op == 'not':
            if operand_type != 'boolean':
                raise SemanticError(
                    f'operator "not" hanya berlaku untuk boolean, bukan {operand_type}',
                    node.line
                )
            return 'boolean'
        return 'unknown'

    def _infer_binop(self, node: BinOpNode) -> str:
        lt = self._infer_type(node.left)
        rt = self._infer_type(node.right)

        # Aritmatika integer
        if node.op in ('+', '-', '*', '/', 'div', 'mod'):
            if lt != 'integer' or rt != 'integer':
                raise SemanticError(
                    f'operator "{node.op}" membutuhkan integer, '
                    f'bukan {lt} dan {rt}',
                    node.line
                )
            return 'integer'

        # Perbandingan → hasil boolean
        if node.op in ('=', '<>', '<', '>', '<=', '>='):
            if lt != rt:
                raise SemanticError(
                    f'perbandingan "{node.op}" antara {lt} dan {rt} tidak valid',
                    node.line
                )
            return 'boolean'

        # Logika boolean
        if node.op in ('and', 'or'):
            if lt != 'boolean' or rt != 'boolean':
                raise SemanticError(
                    f'operator "{node.op}" membutuhkan boolean, '
                    f'bukan {lt} dan {rt}',
                    node.line
                )
            return 'boolean'

        return 'unknown'
