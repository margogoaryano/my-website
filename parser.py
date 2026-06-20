# ============================================================
# KOMPONEN 2: PARSER
# Membaca token dari Scanner → membangun AST
# Grammar MiniPascal:
#   program  → PROGRAM id ; var_section block .
#   var      → VAR (id_list : type ;)+
#   block    → BEGIN stmt_list END
#   stmt     → assign | if | while | writeln | readln | block | ε
#   assign   → id := expr
#   if       → IF expr THEN stmt [ELSE stmt]
#   while    → WHILE expr DO stmt
# ============================================================

from scanner import TokenType, Token
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, msg, line):
        super().__init__(f'[Baris {line}] Error Sintaks: {msg}')
        self.line = line


class Parser:
    def __init__(self, tokens: list):
        self.tokens  = tokens
        self.pos     = 0
        self.errors  = []

    # ── helper ──────────────────────────────────────────────
    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset=1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]   # EOF

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _expect(self, ttype, msg=None) -> Token:
        tok = self._current()
        if tok.type != ttype:
            err_msg = msg or f'diharapkan {ttype} tapi ditemukan "{tok.value}" ({tok.type})'
            raise ParseError(err_msg, tok.line)
        return self._advance()

    def _match(self, *ttypes) -> bool:
        return self._current().type in ttypes

    # ── entry point ─────────────────────────────────────────
    def parse(self) -> ProgramNode:
        try:
            node = self._parse_program()
            return node
        except ParseError as e:
            self.errors.append(str(e))
            return None

    # ── grammar rules ───────────────────────────────────────
    def _parse_program(self):
        self._expect(TokenType.PROGRAM, 'program harus diawali kata "program"')
        name_tok = self._expect(TokenType.IDENTIFIER, 'nama program dibutuhkan')
        self._expect(TokenType.SEMICOLON, 'diharapkan ";" setelah nama program')

        var_decls = []
        if self._match(TokenType.VAR):
            var_decls = self._parse_var_section()

        block = self._parse_block()
        self._expect(TokenType.DOT, 'program harus diakhiri dengan "."')
        return ProgramNode(name_tok.value, var_decls, block)

    def _parse_var_section(self):
        self._advance()   # lewati VAR
        decls = []
        while self._match(TokenType.IDENTIFIER):
            decls.append(self._parse_var_decl())
        return decls

    def _parse_var_decl(self):
        line   = self._current().line
        names  = [self._expect(TokenType.IDENTIFIER).value]
        while self._match(TokenType.COMMA):
            self._advance()
            names.append(self._expect(TokenType.IDENTIFIER).value)
        self._expect(TokenType.COLON, 'diharapkan ":" setelah nama variabel')
        type_tok = self._current()
        if type_tok.type not in (TokenType.INTEGER_KW, TokenType.BOOLEAN_KW, TokenType.STRING_KW):
            raise ParseError(f'tipe data tidak dikenal: "{type_tok.value}"', type_tok.line)
        self._advance()
        self._expect(TokenType.SEMICOLON, 'diharapkan ";" setelah deklarasi variabel')
        return VarDeclNode(names, type_tok.value, line)

    def _parse_block(self):
        self._expect(TokenType.BEGIN, 'diharapkan "begin"')
        stmts = self._parse_statement_list()
        self._expect(TokenType.END, 'diharapkan "end" untuk menutup "begin"')
        return BlockNode(stmts)

    def _parse_statement_list(self):
        stmts = []
        while not self._match(TokenType.END, TokenType.EOF):
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            # titik koma antar statement (opsional sebelum END)
            if self._match(TokenType.SEMICOLON):
                self._advance()
        return stmts

    def _parse_statement(self):
        tok = self._current()

        if tok.type == TokenType.IDENTIFIER:
            return self._parse_assignment()
        elif tok.type == TokenType.IF:
            return self._parse_if()
        elif tok.type == TokenType.WHILE:
            return self._parse_while()
        elif tok.type == TokenType.WRITELN:
            return self._parse_writeln()
        elif tok.type == TokenType.READLN:
            return self._parse_readln()
        elif tok.type == TokenType.BEGIN:
            return self._parse_block()
        elif tok.type in (TokenType.END, TokenType.ELSE, TokenType.EOF):
            return None   # statement kosong / akhir blok
        else:
            raise ParseError(f'statement tidak valid dimulai dengan "{tok.value}"', tok.line)

    def _parse_assignment(self):
        line     = self._current().line
        var_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.ASSIGN, f'diharapkan ":=" setelah "{var_name}"')
        expr = self._parse_expr()
        return AssignNode(var_name, expr, line)

    def _parse_if(self):
        line = self._current().line
        self._advance()   # IF
        cond = self._parse_expr()
        self._expect(TokenType.THEN, 'diharapkan "then" setelah kondisi if')
        then_stmt = self._parse_statement()
        else_stmt = None
        if self._match(TokenType.ELSE):
            self._advance()
            else_stmt = self._parse_statement()
        return IfNode(cond, then_stmt, else_stmt, line)

    def _parse_while(self):
        line = self._current().line
        self._advance()   # WHILE
        cond = self._parse_expr()
        self._expect(TokenType.DO, 'diharapkan "do" setelah kondisi while')
        body = self._parse_statement()
        return WhileNode(cond, body, line)

    def _parse_writeln(self):
        line = self._current().line
        self._advance()   # WRITELN
        self._expect(TokenType.LPAREN, 'diharapkan "(" setelah writeln')
        args = [self._parse_expr()]
        while self._match(TokenType.COMMA):
            self._advance()
            args.append(self._parse_expr())
        self._expect(TokenType.RPAREN, 'diharapkan ")" penutup writeln')
        return WritelnNode(args, line)

    def _parse_readln(self):
        line = self._current().line
        self._advance()   # READLN
        self._expect(TokenType.LPAREN)
        names = [self._expect(TokenType.IDENTIFIER).value]
        while self._match(TokenType.COMMA):
            self._advance()
            names.append(self._expect(TokenType.IDENTIFIER).value)
        self._expect(TokenType.RPAREN)
        return ReadlnNode(names, line)

    # ── Ekspresi (precedence climbing) ──────────────────────
    def _parse_expr(self):
        return self._parse_or_expr()

    def _parse_or_expr(self):
        node = self._parse_and_expr()
        while self._match(TokenType.OR):
            op   = self._advance()
            right = self._parse_and_expr()
            node  = BinOpNode(node, 'or', right, op.line)
        return node

    def _parse_and_expr(self):
        node = self._parse_not_expr()
        while self._match(TokenType.AND):
            op    = self._advance()
            right = self._parse_not_expr()
            node  = BinOpNode(node, 'and', right, op.line)
        return node

    def _parse_not_expr(self):
        if self._match(TokenType.NOT):
            op = self._advance()
            return UnaryOpNode('not', self._parse_not_expr(), op.line)
        return self._parse_comparison()

    def _parse_comparison(self):
        node = self._parse_add_expr()
        CMP  = {
            TokenType.EQ: '=', TokenType.NEQ: '<>',
            TokenType.LT: '<', TokenType.GT: '>',
            TokenType.LTE: '<=', TokenType.GTE: '>=',
        }
        while self._current().type in CMP:
            op    = self._advance()
            right = self._parse_add_expr()
            node  = BinOpNode(node, CMP[op.type], right, op.line)
        return node

    def _parse_add_expr(self):
        node = self._parse_mul_expr()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op    = self._advance()
            right = self._parse_mul_expr()
            node  = BinOpNode(node, op.value, right, op.line)
        return node

    def _parse_mul_expr(self):
        node = self._parse_unary()
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.DIV, TokenType.MOD):
            op    = self._advance()
            right = self._parse_unary()
            node  = BinOpNode(node, op.value, right, op.line)
        return node

    def _parse_unary(self):
        if self._match(TokenType.MINUS):
            op = self._advance()
            return UnaryOpNode('-', self._parse_primary(), op.line)
        return self._parse_primary()

    def _parse_primary(self):
        tok = self._current()

        if tok.type == TokenType.INTEGER:
            self._advance()
            return IntLiteralNode(tok.value, tok.line)
        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLiteralNode(True, tok.line)
        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLiteralNode(False, tok.line)
        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteralNode(tok.value, tok.line)
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return VarNode(tok.value, tok.line)
        if tok.type == TokenType.LPAREN:
            self._advance()
            node = self._parse_expr()
            self._expect(TokenType.RPAREN, 'diharapkan ")" penutup ekspresi')
            return node

        raise ParseError(f'ekspresi tidak valid: "{tok.value}"', tok.line)
