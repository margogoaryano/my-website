# ============================================================
# KOMPILER MINIPASCAL - KELOMPOK 5
# Teknik Kompilasi - Universitas Lancang Kuning
# ============================================================
# KOMPONEN 1: SCANNER (LEXER)
# Mengubah teks source code menjadi token-token
# ============================================================

import re

# ── Definisi semua tipe token ────────────────────────────────
class TokenType:
    # Tipe data & literal
    INTEGER     = 'INTEGER'
    STRING      = 'STRING'
    IDENTIFIER  = 'IDENTIFIER'

    # Keyword MiniPascal
    PROGRAM     = 'PROGRAM'
    VAR         = 'VAR'
    BEGIN       = 'BEGIN'
    END         = 'END'
    IF          = 'IF'
    THEN        = 'THEN'
    ELSE        = 'ELSE'
    WHILE       = 'WHILE'
    DO          = 'DO'
    WRITELN     = 'WRITELN'
    READLN      = 'READLN'
    DIV         = 'DIV'
    MOD         = 'MOD'
    AND         = 'AND'
    OR          = 'OR'
    NOT         = 'NOT'
    TRUE        = 'TRUE'
    FALSE       = 'FALSE'
    INTEGER_KW  = 'INTEGER_KW'   # keyword "integer" (tipe data)
    BOOLEAN_KW  = 'BOOLEAN_KW'
    STRING_KW   = 'STRING_KW'

    # Operator
    ASSIGN      = 'ASSIGN'       # :=
    PLUS        = 'PLUS'         # +
    MINUS       = 'MINUS'        # -
    MULTIPLY    = 'MULTIPLY'     # *
    DIVIDE      = 'DIVIDE'       # /
    EQ          = 'EQ'           # =
    NEQ         = 'NEQ'          # <>
    LT          = 'LT'           # <
    GT          = 'GT'           # >
    LTE         = 'LTE'          # <=
    GTE         = 'GTE'          # >=

    # Tanda baca
    SEMICOLON   = 'SEMICOLON'    # ;
    COLON       = 'COLON'        # :
    COMMA       = 'COMMA'        # ,
    DOT         = 'DOT'          # .
    LPAREN      = 'LPAREN'       # (
    RPAREN      = 'RPAREN'       # )

    # Spesial
    EOF         = 'EOF'


# Peta keyword → TokenType
KEYWORDS = {
    'program'  : TokenType.PROGRAM,
    'var'      : TokenType.VAR,
    'begin'    : TokenType.BEGIN,
    'end'      : TokenType.END,
    'if'       : TokenType.IF,
    'then'     : TokenType.THEN,
    'else'     : TokenType.ELSE,
    'while'    : TokenType.WHILE,
    'do'       : TokenType.DO,
    'writeln'  : TokenType.WRITELN,
    'readln'   : TokenType.READLN,
    'div'      : TokenType.DIV,
    'mod'      : TokenType.MOD,
    'and'      : TokenType.AND,
    'or'       : TokenType.OR,
    'not'      : TokenType.NOT,
    'true'     : TokenType.TRUE,
    'false'    : TokenType.FALSE,
    'integer'  : TokenType.INTEGER_KW,
    'boolean'  : TokenType.BOOLEAN_KW,
    'string'   : TokenType.STRING_KW,
}


# ── Kelas Token ──────────────────────────────────────────────
class Token:
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line          # nomor baris (untuk error message)

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line})'


# ── Scanner utama ────────────────────────────────────────────
class Scanner:
    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0
        self.line    = 1
        self.tokens  = []
        self.errors  = []          # kumpulkan error leksikal

    # ── helper ──────────────────────────────────────────────
    def _current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def _peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self._current()
            # Whitespace
            if ch in ' \t\r\n':
                self._advance()
            # Komentar { ... }
            elif ch == '{':
                self._advance()
                while self.pos < len(self.source) and self._current() != '}':
                    self._advance()
                if self.pos < len(self.source):
                    self._advance()   # lewati '}'
                else:
                    self.errors.append(f'[Baris {self.line}] Error Leksikal: komentar tidak ditutup')
            # Komentar (* ... *)
            elif ch == '(' and self._peek() == '*':
                self._advance(); self._advance()
                while self.pos < len(self.source):
                    if self._current() == '*' and self._peek() == ')':
                        self._advance(); self._advance()
                        break
                    self._advance()
                else:
                    self.errors.append(f'[Baris {self.line}] Error Leksikal: komentar (* tidak ditutup')
            else:
                break

    # ── scan satu token ─────────────────────────────────────
    def _next_token(self):
        self._skip_whitespace_and_comments()

        if self.pos >= len(self.source):
            return Token(TokenType.EOF, None, self.line)

        ch   = self._current()
        line = self.line

        # ─ Integer literal ───────────────────────────────────
        if ch.isdigit():
            start = self.pos
            while self.pos < len(self.source) and self._current().isdigit():
                self._advance()
            value = int(self.source[start:self.pos])
            return Token(TokenType.INTEGER, value, line)

        # ─ Identifier / keyword ──────────────────────────────
        if ch.isalpha() or ch == '_':
            start = self.pos
            while self.pos < len(self.source) and (self._current().isalnum() or self._current() == '_'):
                self._advance()
            word    = self.source[start:self.pos]
            ttype   = KEYWORDS.get(word.lower(), TokenType.IDENTIFIER)
            value   = word.lower() if ttype != TokenType.IDENTIFIER else word
            return Token(ttype, value, line)

        # ─ String literal ────────────────────────────────────
        if ch == "'":
            self._advance()
            start = self.pos
            while self.pos < len(self.source) and self._current() != "'":
                self._advance()
            if self.pos >= len(self.source):
                self.errors.append(f'[Baris {line}] Error Leksikal: string tidak ditutup')
                return Token(TokenType.STRING, '', line)
            value = self.source[start:self.pos]
            self._advance()   # lewati penutup '
            return Token(TokenType.STRING, value, line)

        # ─ Operator 2-karakter ───────────────────────────────
        two = self.source[self.pos:self.pos+2]
        if two == ':=':
            self._advance(); self._advance()
            return Token(TokenType.ASSIGN, ':=', line)
        if two == '<>':
            self._advance(); self._advance()
            return Token(TokenType.NEQ, '<>', line)
        if two == '<=':
            self._advance(); self._advance()
            return Token(TokenType.LTE, '<=', line)
        if two == '>=':
            self._advance(); self._advance()
            return Token(TokenType.GTE, '>=', line)

        # ─ Operator & tanda baca 1-karakter ─────────────────
        single = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.EQ,
            '<': TokenType.LT,
            '>': TokenType.GT,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
        }
        if ch in single:
            self._advance()
            return Token(single[ch], ch, line)

        # ─ Karakter tidak dikenal ────────────────────────────
        self.errors.append(f'[Baris {line}] Error Leksikal: karakter tidak dikenal "{ch}"')
        self._advance()
        return self._next_token()

    # ── API publik: tokenize seluruh source ─────────────────
    def tokenize(self):
        while True:
            tok = self._next_token()
            self.tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return self.tokens
