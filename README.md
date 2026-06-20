# KOMPILER MINIPASCAL – KELOMPOK 5
**Mata Kuliah:** Teknik Kompilasi  
**Universitas Lancang Kuning – Pekanbaru**

---

## Anggota Kelompok 5
| No | Nama | NIM |
|----|------|-----|
| 1 | Diva Filisa | 2137154 |
| 2 | Margogo Aryano | 2130544 |
| 3 | Melati Surya Ningsih | 2104419 |
| 4 | Muhammad Ridho Renaldi | 2104431 |
| 5 | Oza Sulta Winanda | ... |
| 6 | (Anggota 6) | ... |

**Bahasa Target:** MiniPascal  
**Fitur:** Integer, assignment `:=`, if-then-else, while-do, begin-end

---

## Struktur File

```
minipascal/
├── scanner.py          # Komponen 1: Scanner / Lexer
├── ast_nodes.py        # Definisi node AST
├── parser.py           # Komponen 2: Parser + AST Builder
├── semantic.py         # Komponen 3: Semantic Analyzer + Symbol Table
├── icg_optimizer.py    # Komponen 4: ICG (TAC) + Komponen 5: Optimizer
├── main.py             # Entry point utama
├── test_compiler.py    # Test cases
└── README.md
```

---

## Cara Menjalankan

### Prasyarat
- Python 3.7 atau lebih baru
- Tidak memerlukan library tambahan

### Jalankan contoh bawaan:
```bash
python main.py
```

### Jalankan dengan file sumber:
```bash
python main.py program_saya.pas
```

### Jalankan test cases:
```bash
python test_compiler.py
```

---

## Komponen yang Diimplementasikan

### 1. Scanner (Lexer) — `scanner.py`
Mengubah teks source code menjadi stream token.
- Mengenali keyword MiniPascal: `program`, `var`, `begin`, `end`, `if`, `then`, `else`, `while`, `do`, `writeln`, `readln`, `div`, `mod`, `and`, `or`, `not`, `true`, `false`
- Tipe data: `integer`, `boolean`, `string`
- Operator: `:=`, `+`, `-`, `*`, `/`, `=`, `<>`, `<`, `>`, `<=`, `>=`
- Menangani komentar `{ }` dan `(* *)`
- Melaporkan error leksikal (karakter tidak dikenal, string/komentar tidak ditutup)

### 2. Parser + AST — `parser.py` + `ast_nodes.py`
Memverifikasi sintaks dan membangun Abstract Syntax Tree.
- Implementasi recursive descent parser
- Grammar sesuai spesifikasi MiniPascal
- Mendukung ekspresi dengan precedence yang benar: `or < and < not < comparison < +/- < *//div/mod < unary`
- Melaporkan error sintaks dengan nomor baris

### 3. Semantic Analyzer — `semantic.py`
Memeriksa kebenaran semantik program.
- **Symbol Table:** Menyimpan nama dan tipe setiap variabel
- **Type Checking:** Memastikan tipe ekspresi cocok
- Deteksi variabel yang belum dideklarasikan
- Deteksi variabel yang didefinisikan ulang
- Memastikan kondisi `if` dan `while` bertipe boolean

### 4. ICG – Three Address Code — `icg_optimizer.py`
Menghasilkan kode antara dalam format Three Address Code (TAC).
- Format: `result := arg1 op arg2`
- Mendukung: ASSIGN, BINOP, UNARY, LABEL, GOTO, IF_FALSE, PRINT, READ
- Variabel temporari otomatis: `t1`, `t2`, ...
- Label otomatis: `L1`, `L2`, ...

### 5. Optimizer — `icg_optimizer.py`
Mengoptimasi TAC dengan dua teknik:
1. **Constant Folding:** Menghitung ekspresi konstanta saat compile time  
   Contoh: `t1 := 3 + 4` → `t1 := 7`
2. **Dead Code Elimination:** Menghapus kode yang tidak pernah dieksekusi (setelah `GOTO`)

### 6. Error Handling
Menangani tiga kategori error:
- **Error Leksikal:** Karakter tidak dikenal, literal tidak ditutup
- **Error Sintaks:** Struktur program tidak sesuai grammar
- **Error Semantik:** Tipe tidak cocok, variabel tidak dideklarasikan

---

## Contoh Program MiniPascal

```pascal
program ContohMiniPascal;
var
  x, y, hasil : integer;
  flag        : boolean;
begin
  x := 10;
  y := 5;
  hasil := x + y * 2;

  if x > y then
    writeln(x)
  else
    writeln(y);

  flag := x > 0;

  while x > 0 do
  begin
    hasil := hasil + 1;
    x := x - 1
  end;

  writeln(hasil)
end.
```

---

## Tata Bahasa (Grammar) MiniPascal

```
program    → 'program' id ';' var_section? block '.'
var_section→ 'var' var_decl+
var_decl   → id_list ':' type ';'
id_list    → id (',' id)*
type       → 'integer' | 'boolean' | 'string'
block      → 'begin' statement_list 'end'
stmt_list  → (statement ';'?)*
statement  → assignment | if_stmt | while_stmt
           | writeln | readln | block
assignment → id ':=' expr
if_stmt    → 'if' expr 'then' statement ('else' statement)?
while_stmt → 'while' expr 'do' statement
writeln    → 'writeln' '(' expr (',' expr)* ')'
readln     → 'readln' '(' id (',' id)* ')'
expr       → or_expr
or_expr    → and_expr ('or' and_expr)*
and_expr   → not_expr ('and' not_expr)*
not_expr   → 'not' not_expr | comparison
comparison → add_expr (('='|'<>'|'<'|'>'|'<='|'>=') add_expr)*
add_expr   → mul_expr (('+'|'-') mul_expr)*
mul_expr   → unary (('*'|'/'|'div'|'mod') unary)*
unary      → '-' primary | primary
primary    → INTEGER | BOOLEAN | STRING | id | '(' expr ')'
```
