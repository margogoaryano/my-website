# ============================================================
# TEST CASES - Menguji semua komponen kompiler MiniPascal
# ============================================================

import sys
sys.path.insert(0, '.')
from scanner import Scanner
from parser import Parser
from semantic import SemanticAnalyzer
from icg_optimizer import ICGGenerator, Optimizer

def run_test(title, source, expect_error=False):
    print(f'\n{"─"*60}')
    print(f'  TEST: {title}')
    print(f'{"─"*60}')

    scanner = Scanner(source)
    tokens  = scanner.tokenize()
    parser  = Parser(tokens)
    ast     = parser.parse()
    sem     = SemanticAnalyzer()
    sem.analyze(ast)

    all_errors = scanner.errors + parser.errors + sem.errors
    if all_errors:
        print('  ERROR TERDETEKSI:')
        for e in all_errors:
            print(f'    ✗ {e}')
        if expect_error:
            print('  → [PASS] Error memang diharapkan')
        else:
            print('  → [FAIL] Seharusnya tidak ada error')
    else:
        if expect_error:
            print('  → [FAIL] Seharusnya ada error tapi tidak ditemukan')
        else:
            icg     = ICGGenerator()
            tac     = icg.generate(ast)
            opt     = Optimizer(tac)
            opt_tac = opt.optimize()
            print(f'  → [PASS] OK | {len(tokens)-1} token | {len(opt_tac)} instruksi TAC')


# ── Test 1: Program valid sederhana
run_test('Program Valid - Assignment & Writeln', """
program Test1;
var x : integer;
begin
  x := 42;
  writeln(x)
end.
""")

# ── Test 2: If-then-else
run_test('If-Then-Else', """
program Test2;
var a, b : integer;
begin
  a := 10;
  b := 20;
  if a < b then
    writeln(a)
  else
    writeln(b)
end.
""")

# ── Test 3: While-do + begin-end
run_test('While-Do dengan begin-end', """
program Test3;
var i, sum : integer;
begin
  i := 1;
  sum := 0;
  while i <= 10 do
  begin
    sum := sum + i;
    i := i + 1
  end;
  writeln(sum)
end.
""")

# ── Test 4: Error - variabel tidak dideklarasikan
run_test('Error: Variabel tidak dideklarasikan', """
program Test4;
var x : integer;
begin
  y := 5
end.
""", expect_error=True)

# ── Test 5: Error - tipe tidak cocok
run_test('Error: Tipe tidak cocok (integer := boolean)', """
program Test5;
var x : integer;
    flag : boolean;
begin
  x := true
end.
""", expect_error=True)

# ── Test 6: Error - kondisi if bukan boolean
run_test('Error: Kondisi if bukan boolean', """
program Test6;
var x : integer;
begin
  x := 5;
  if x then
    writeln(x)
end.
""", expect_error=True)

# ── Test 7: Constant folding
run_test('Constant Folding: 3+4, 10*2, 100-50', """
program Test7;
var result : integer;
begin
  result := 3 + 4;
  result := 10 * 2;
  result := 100 - 50
end.
""")

print('\n' + '='*60)
print('  Semua test selesai dijalankan')
print('='*60)
