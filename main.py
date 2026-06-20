# ============================================================
# KOMPILER MINIPASCAL - KELOMPOK 5
# Teknik Kompilasi - Universitas Lancang Kuning
# ============================================================
# main.py  →  entry point utama
# Menggabungkan: Scanner → Parser → Semantic → ICG → Optimizer
# ============================================================

import sys
from scanner      import Scanner
from parser       import Parser
from semantic     import SemanticAnalyzer
from icg_optimizer import ICGGenerator, Optimizer


# ── Pretty printer untuk TAC ────────────────────────────────
def print_tac(title: str, instructions: list):
    print(f'\n╔{"═"*(len(title)+2)}╗')
    print(f'║ {title} ║')
    print(f'╚{"═"*(len(title)+2)}╝')
    for i, instr in enumerate(instructions, 1):
        print(f'  {i:3}.  {instr}')


# ── Compile ─────────────────────────────────────────────────
def compile_minipascal(source: str, verbose: bool = True):
    print('=' * 60)
    print('  KOMPILER MINIPASCAL  –  Kelompok 5')
    print('  Teknik Kompilasi | Universitas Lancang Kuning')
    print('=' * 60)

    has_error = False

    # ── FASE 1: SCANNER ─────────────────────────────────────
    print('\n[FASE 1] Scanning (Lexical Analysis)...')
    scanner = Scanner(source)
    tokens  = scanner.tokenize()

    if scanner.errors:
        has_error = True
        print('  ✗ Error Leksikal:')
        for err in scanner.errors:
            print(f'    → {err}')
    else:
        print(f'  ✓ Berhasil menghasilkan {len(tokens)-1} token')

    if verbose:
        print('\n  Daftar Token:')
        for tok in tokens:
            if tok.type != 'EOF':
                print(f'    [{tok.line:3}]  {tok.type:<15}  {repr(tok.value)}')

    # ── FASE 2: PARSER ──────────────────────────────────────
    print('\n[FASE 2] Parsing (Syntax Analysis)...')
    parser = Parser(tokens)
    ast    = parser.parse()

    if parser.errors:
        has_error = True
        print('  ✗ Error Sintaks:')
        for err in parser.errors:
            print(f'    → {err}')
    elif ast is None:
        has_error = True
        print('  ✗ Parsing gagal.')
    else:
        print('  ✓ AST berhasil dibangun')

    if has_error:
        print('\n✗ Kompilasi dihentikan karena error.')
        return False

    # ── FASE 3: SEMANTIC ANALYZER ───────────────────────────
    print('\n[FASE 3] Semantic Analysis...')
    sem = SemanticAnalyzer()
    sem.analyze(ast)

    if sem.errors:
        has_error = True
        print('  ✗ Error Semantik:')
        for err in sem.errors:
            print(f'    → {err}')
    else:
        print('  ✓ Analisis semantik berhasil')
        sem.symbol_table.display()

    if has_error:
        print('\n✗ Kompilasi dihentikan karena error semantik.')
        return False

    # ── FASE 4: ICG – Three Address Code ────────────────────
    print('\n[FASE 4] Intermediate Code Generation (TAC)...')
    icg  = ICGGenerator()
    tac  = icg.generate(ast)
    print_tac('THREE ADDRESS CODE (sebelum optimasi)', tac)

    # ── FASE 5: OPTIMIZER ───────────────────────────────────
    print('\n[FASE 5] Optimasi Kode...')
    opt     = Optimizer(tac)
    opt_tac = opt.optimize()
    print_tac('THREE ADDRESS CODE (setelah optimasi)', opt_tac)

    saved = len(tac) - len(opt_tac)
    print(f'\n  ✓ Optimasi selesai. Instruksi dieliminasi: {saved}')

    print('\n' + '=' * 60)
    print('  ✓ KOMPILASI BERHASIL')
    print('=' * 60)
    return True


# ── Contoh program MiniPascal ────────────────────────────────
CONTOH_PROGRAM = """
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
"""

CONTOH_CONSTANT_FOLDING = """
program TestFolding;
var
  a : integer;
begin
  a := 3 + 4;
  a := 10 * 2;
  a := 100 - 50
end.
"""


# ── Main ─────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Baca dari file
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                source = f.read()
            compile_minipascal(source)
        except FileNotFoundError:
            print(f'File tidak ditemukan: {filename}')
    else:
        # Jalankan contoh bawaan
        print('\n>>> Menjalankan contoh program utama:')
        compile_minipascal(CONTOH_PROGRAM)

        print('\n\n>>> Menjalankan contoh constant folding:')
        compile_minipascal(CONTOH_CONSTANT_FOLDING, verbose=False)
