#!/usr/bin/env python3
"""
hill_toolkit.py -- Hill cipher toolkit for the Stage 1 Specialist Mathematics
investigation "Encryption Using Matrices".
"""

import argparse
import itertools
import math
import sys
import unittest
from collections import Counter

MOD = 26


class InvalidKeyError(ValueError):
    """Raised when a key matrix is not invertible modulo m."""


# ---------------------------------------------------------------------------
# 1. Letters, text preparation and blocks
# ---------------------------------------------------------------------------
def letter_to_number(letter):
    """A=1, ..., Y=25, Z=0 (the convention of the task sheet)."""
    letter = letter.upper()
    if len(letter) != 1 or not ("A" <= letter <= "Z"):
        raise ValueError(f"Not a letter A-Z: {letter!r}")
    return (ord(letter) - ord("A") + 1) % 26


def number_to_letter(number):
    """Inverse of letter_to_number; 0 is written as Z."""
    number %= 26
    return "Z" if number == 0 else chr(ord("A") + number - 1)


def clean_text(text):
    """Keep letters only and use capitals (spaces and punctuation are removed)."""
    return "".join(ch for ch in text.upper() if "A" <= ch <= "Z")


def pad_text(text, n, pad="X"):
    """Add the padding letter so that the length is a multiple of the block size n."""
    remainder = len(text) % n
    return text if remainder == 0 else text + pad * (n - remainder)


def to_blocks(text, n):
    """Split a capital-letter string into blocks of n numbers."""
    if len(text) % n != 0:
        raise ValueError(f"Length {len(text)} is not a multiple of the block size {n}.")
    numbers = [letter_to_number(ch) for ch in text]
    return [tuple(numbers[i:i + n]) for i in range(0, len(numbers), n)]


def block_to_text(block):
    return "".join(number_to_letter(v) for v in block)


# ---------------------------------------------------------------------------
# 2. Modular arithmetic and matrices
# ---------------------------------------------------------------------------
def egcd(a, b):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, s, t = egcd(b, a % b)
    return (g, t, s - (a // b) * t)


def mod_inverse(a, m=MOD):
    g, s, _ = egcd(a % m, m)
    return s % m if g == 1 else None


def minor(M, i, j):
    return [row[:j] + row[j + 1:] for k, row in enumerate(M) if k != i]


def det(M):
    n = len(M)
    if n == 1:
        return M[0][0]
    if n == 2:
        return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    return sum((-1) ** j * M[0][j] * det(minor(M, 0, j)) for j in range(n))


def adjugate(M):
    n = len(M)
    if n == 1:
        return [[1]]
    return [[(-1) ** (i + j) * det(minor(M, j, i)) for j in range(n)] for i in range(n)]


def check_square(M):
    if not M or any(len(row) != len(M) for row in M):
        raise ValueError("The key must be a non-empty square matrix.")
    if len(M) < 2:
        raise ValueError("The key must be at least 2 x 2.")


def mat_mul(A, B, m=None):
    prod = [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]
    return prod if m is None else [[v % m for v in row] for row in prod]


def mat_vec(M, v, m=None):
    out = [sum(M[i][k] * v[k] for k in range(len(v))) for i in range(len(M))]
    return out if m is None else [x % m for x in out]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def is_valid_key(K, m=MOD):
    check_square(K)
    return math.gcd(det(K) % m, m) == 1


def inverse_matrix(K, m=MOD):
    check_square(K)
    d = det(K) % m
    d_inv = mod_inverse(d, m)
    if d_inv is None:
        raise InvalidKeyError(
            f"det K = {det(K)} = {d} (mod {m}) and gcd({d}, {m}) = {math.gcd(d, m)} != 1, "
            "so K has no inverse.")
    return [[(d_inv * v) % m for v in row] for row in adjugate(K)]


def inverse_report(K, m=MOD):
    d = det(K)
    d_mod = d % m
    g = math.gcd(d_mod, m)
    if g != 1:
        return d, d_mod, g, None, None, False
    Kinv = inverse_matrix(K, m)
    ok = (mat_mul(K, Kinv, m) == identity(len(K)) and mat_mul(Kinv, K, m) == identity(len(K)))
    return d, d_mod, g, mod_inverse(d_mod, m), Kinv, ok


# ---------------------------------------------------------------------------
# 3. Encryption and decryption
# ---------------------------------------------------------------------------
def transform(text, M, m=MOD):
    n = len(M)
    steps, out = [], []
    for block in to_blocks(text, n):
        raw = mat_vec(M, block)
        red = [v % m for v in raw]
        letters = block_to_text(red)
        steps.append({"in": block_to_text(block), "x": block, "raw": raw,
                      "red": tuple(red), "out": letters})
        out.append(letters)
    return "".join(out), steps


def encrypt(plaintext, K, m=MOD, pad=True):
    check_square(K)
    if not is_valid_key(K, m):
        raise InvalidKeyError("Invalid key: gcd(det K, 26) != 1, so decryption would be impossible.")
    text = clean_text(plaintext)
    if not text:
        raise ValueError("The plaintext contains no letters.")
    n = len(K)
    if pad:
        text = pad_text(text, n)
    cipher, steps = transform(text, K, m)
    return cipher, steps, text


def decrypt(ciphertext, K, m=MOD):
    check_square(K)
    text = clean_text(ciphertext)
    if not text:
        raise ValueError("The ciphertext contains no letters.")
    Kinv = inverse_matrix(K, m)
    plain, steps = transform(text, Kinv, m)
    return plain, steps, Kinv


def format_steps(steps, label="Mx", limit=None, modulus=MOD):
    lines = []
    for idx, s in enumerate(steps[:limit], start=1):
        lines.append(f"  • Block {idx:>2}: '{s['in']}'  x=({', '.join(map(str, s['x']))})  "
                     f"{label}=({', '.join(map(str, s['raw']))})  "
                     f"mod {modulus}=({', '.join(map(str, s['red']))})  ➔ '{s['out']}'")
    if limit is not None and len(steps) > limit:
        lines.append(f"  ... ({len(steps) - limit} more blocks)")
    return "\n".join(lines)


def fmt_matrix(M):
    return "[" + "; ".join(" ".join(str(v) for v in row) for row in M) + "]"


# ---------------------------------------------------------------------------
# 4. Counting valid keys
# ---------------------------------------------------------------------------
def factorize(m):
    factors, p = {}, 2
    while p * p <= m:
        while m % p == 0:
            factors[p] = factors.get(p, 0) + 1
            m //= p
        p += 1
    if m > 1:
        factors[m] = factors.get(m, 0) + 1
    return factors


def count_gl_prime(n, p):
    result = 1
    for i in range(n):
        result *= p ** n - p ** i
    return result


def count_invertible_formula(n, m):
    total = 1
    for p, k in factorize(m).items():
        total *= p ** ((k - 1) * n * n) * count_gl_prime(n, p)
    return total


def count_valid_2x2_bruteforce(m):
    return sum(1 for a, b, c, d in itertools.product(range(m), repeat=4)
               if math.gcd((a * d - b * c) % m, m) == 1)


def count_invertible_bruteforce(n, m):
    return sum(1 for entries in itertools.product(range(m), repeat=n * n)
               if math.gcd(det([list(entries[i * n:(i + 1) * n]) for i in range(n)]) % m, m) == 1)


# ---------------------------------------------------------------------------
# 5. Kernel test and fixed blocks
# ---------------------------------------------------------------------------
def popcount(x):
    return x.bit_count() if hasattr(int, "bit_count") else bin(x).count("1")


def solution_masks(m=MOD):
    masks = {}
    for r1 in range(m):
        for r2 in range(m):
            bits = 0
            for x in range(m):
                for y in range(m):
                    if (r1 * x + r2 * y) % m == 0:
                        bits |= 1 << (x * m + y)
            masks[(r1, r2)] = bits
    return masks


def kernel_test(m=MOD, masks=None):
    masks = masks or solution_masks(m)
    trivial_count, agrees = 0, True
    for a, b, c, d in itertools.product(range(m), repeat=4):
        trivial = popcount(masks[(a, b)] & masks[(c, d)]) == 1
        rule = math.gcd((a * d - b * c) % m, m) == 1
        trivial_count += trivial
        agrees = agrees and (trivial == rule)
    return trivial_count, agrees


def fixed_blocks(K, m=MOD):
    (a, b), (c, d) = K
    return [(x, y) for x in range(m) for y in range(m)
            if (a * x + b * y - x) % m == 0 and (c * x + d * y - y) % m == 0]


def fixed_distribution(m=MOD, masks=None):
    masks = masks or solution_masks(m)
    counter, total = Counter(), 0
    for a, b, c, d in itertools.product(range(m), repeat=4):
        if math.gcd((a * d - b * c) % m, m) != 1:
            continue
        counter[popcount(masks[((a - 1) % m, b)] & masks[(c, (d - 1) % m)])] += 1
        total += 1
    mean = sum(k * v for k, v in counter.items()) / total
    return counter, mean, total


# ---------------------------------------------------------------------------
# 6. Known-plaintext attack
# ---------------------------------------------------------------------------
def recover_key_from_blocks(plain_blocks, cipher_blocks, m=MOD):
    n = len(plain_blocks)
    if n < 2 or len(cipher_blocks) != n or any(len(b) != n for b in plain_blocks + cipher_blocks):
        raise ValueError("Need n known blocks of length n (n >= 2).")
    X = [[plain_blocks[j][i] for j in range(n)] for i in range(n)]
    Y = [[cipher_blocks[j][i] for j in range(n)] for i in range(n)]
    if not is_valid_key(X, m):
        return None
    return mat_mul(Y, inverse_matrix(X, m), m)


def attack_with_text(plain, cipher, n=2, m=MOD):
    pb, cb = to_blocks(clean_text(plain), n), to_blocks(clean_text(cipher), n)
    if len(pb) != len(cb):
        raise ValueError("Plaintext and ciphertext have different numbers of blocks.")
    for idx in itertools.combinations(range(len(pb)), n):
        K = recover_key_from_blocks([pb[i] for i in idx], [cb[i] for i in idx], m)
        if K is not None and is_valid_key(K, m) and \
                all(tuple(mat_vec(K, p, m)) == c for p, c in zip(pb, cb)):
            return K, idx
    return None


def usable_pairs(plaintext, n=2, m=MOD):
    blocks = to_blocks(clean_text(plaintext), n)
    combos = list(itertools.combinations(blocks, n))
    good = sum(1 for combo in combos
               if is_valid_key([[blk[i] for blk in combo] for i in range(n)], m))
    return good, len(combos)


def consistent_keys_2x2(pairs, m=MOD):
    keys = []
    for a, b, c, d in itertools.product(range(m), repeat=4):
        if math.gcd((a * d - b * c) % m, m) != 1:
            continue
        if all((a * x + b * y) % m == u and (c * x + d * y) % m == v
               for (x, y), (u, v) in pairs):
            keys.append((a, b, c, d))
    return keys


# ---------------------------------------------------------------------------
# 7. Cases used in the report
# ---------------------------------------------------------------------------
K1 = [[9, 4], [2, 7]]
K2 = [[4, 1], [3, 2]]
K3 = [[2, 3, 1], [1, 2, 4], [3, 1, 2]]
K_PEER = [[8, 1], [9, 3]]
CASES = [
    ("Refined key", "Genshin Impact is the most fun game", [[1,1],[1,2]], "LQGZQZWFCSDGCLMGMRBQMGAVUBNACA", "encrypt"),
    ("Main case study", "ILOVESENRENBANKA", K1, "YXOBQMWDZSDPMVYC", "encrypt"),
    ("Genshin Impact", "Genshin Impact is the most fun game.", K2, "GEWBOPMHPSGIKZRSKHOQRSSHKDQCRK", "encrypt"),
    ("Task-sheet benchmark", "ALGEBRAA", K2, "PAGEZPEE", "encrypt"),
    ("3 x 3 example (first block)", "ILO", K3, "QOQ", "encrypt"),
    ("Other student's ciphertext", "NEEDCOFFEE", K_PEER, "MKREMTBTSH", "encrypt"),
]


def verify_cases(show_steps=True):
    print("\n" + "=" * 60)
    print("🔍 VERIFYING REPORT CASES")
    print("=" * 60)
    all_ok = True
    for name, text, K, expected, _ in CASES:
        print(f"\n▶ [{name}] Key = {fmt_matrix(K)}")
        d, d_mod, g, d_inv, Kinv, ok = inverse_report(K)
        print(f"  • Det = {d} ≡ {d_mod} (mod 26), gcd = {g}, Det⁻¹ = {d_inv}")
        print(f"  • K⁻¹ = {fmt_matrix(Kinv)}, K·K⁻¹ = I: {ok}")
        cipher, steps, padded = encrypt(text, K)
        plain, dsteps, _ = decrypt(cipher, K)
        again, _, _ = encrypt(plain, K, pad=False)
        results = {
            "Ciphertext matches expected": cipher == expected,
            "Decryption returns padded text": plain == padded,
            "Re-encryption matches ciphertext": again == cipher,
        }
        print(f"  • Plaintext  : {padded}")
        print(f"  • Ciphertext : {cipher}")
        if show_steps:
            print(format_steps(steps, "Kx", limit=2))
        for label, passed in results.items():
            print(f"  ➔ {label}: {'✅ PASS' if passed else '❌ FAIL'}")
        all_ok = all_ok and ok and all(results.values())

    print("\n▶ [Other student's ciphertext: decryption direction]")
    plain, dsteps, Kinv = decrypt("MKREMTBTSH", K_PEER)
    print(f"  • K⁻¹ = {fmt_matrix(Kinv)}")
    print(format_steps(dsteps, "K⁻¹y"))
    print(f"  • Recovered Plaintext: {plain}")
    all_ok = all_ok and plain == "NEEDCOFFEE"
    print(f"\n✨ All report cases verified successfully: {all_ok}")
    return all_ok


# ---------------------------------------------------------------------------
# 8. Reports & Interactive Menu
# ---------------------------------------------------------------------------
def report_counts():
    print("\n" + "=" * 60)
    print("📊 VALID KEYS COUNTING ANALYSIS")
    print("=" * 60)
    print("1. Valid 2x2 keys by modulus (Brute Force vs Formula):")
    for m in (26, 27, 29):
        brute, formula = count_valid_2x2_bruteforce(m), count_invertible_formula(2, m)
        print(f"   • m = {m}: {brute} of {m**4} ({100*brute/m**4:.2f}%), Formula: {formula}, Match: {brute == formula}")
    print("\n2. 3x3 counts (Brute Force vs Formula):")
    for p in (2, 3):
        brute, formula = count_invertible_bruteforce(3, p), count_gl_prime(3, p)
        print(f"   • p = {p}: Brute Force {brute}, Formula {formula}, Match: {brute == formula}")
    n3 = count_invertible_formula(3, 26)
    print(f"   • Valid 3x3 keys mod 26 (Formula): {n3} ({100*n3/26**9:.2f}% of 26⁹)")


def report_fixed():
    print("\n" + "=" * 60)
    print("🧩 KERNEL TEST & FIXED BLOCKS ANALYSIS")
    print("=" * 60)
    masks = solution_masks()
    kt = kernel_test(26, masks)
    print(f"3. Kernel test (Kv = 0 only for v = 0): {kt[0]} matrices, agrees with rule: {kt[1]}")
    print(f"4. Fixed blocks for key {fmt_matrix(K1)}: {fixed_blocks(K1)}")
    counter, mean, total = fixed_distribution(26, masks)
    print(f"   • Mean fixed blocks per key: {mean:.2f}")
    print("   Distribution:", dict(sorted(counter.items())))
    print("   K2 fixed blocks:", len(fixed_blocks(K2)))
    print("   Exactly 4: %.1f%%; at least 26: %.1f%%" % (100*counter[4]/total, 100*sum(v for k,v in counter.items() if k>=26)/total))
    only_zz = counter[1]
    print(f"   • Keys fixing only ZZ: {100*only_zz/total:.1f}%")


def report_attack():
    print("\n" + "=" * 60)
    print("🔓 KNOWN-PLAINTEXT ATTACK DEMONSTRATION")
    print("=" * 60)
    pairs = [((9, 12), (25, 24))]
    print(f"5. Consistent keys for IL ➔ YX: {len(consistent_keys_2x2(pairs))}")
    pairs.append(((5, 19), (17, 13)))
    print(f"   After adding ES ➔ QM: {consistent_keys_2x2(pairs)}")
    print(f"   Recovered key (IL, ES): {recover_key_from_blocks([(9, 12), (5, 19)], [(25, 24), (17, 13)])}")
    print("   Usable pairs:", usable_pairs("ILOVESENRENBANKA"))
    c3, _, _ = encrypt("ILOVESENR", K3)
    print("   3x3 recovery:", attack_with_text("ILOVESENR", c3, n=3))
    cipher, _, _ = encrypt("ILOVESENRENBANKA", K1)
    print(f"   Attack on full message: {attack_with_text('ILOVESENRENBANKA', cipher)}")


class HillTests(unittest.TestCase):
    def test_refined_key(self):
        k = [[1, 1], [1, 2]]
        self.assertEqual(fixed_blocks(k), [(0, 0)])
        cipher, _, plain = encrypt("Genshin Impact is the most fun game", k)
        self.assertEqual(cipher, "LQGZQZWFCSDGCLMGMRBQMGAVUBNACA")
        self.assertEqual(decrypt(cipher, k)[0], plain)
        self.assertEqual(attack_with_text("GENS", "LQGZ")[0], k)

    def test_invalid_keys_and_input(self):
        with self.assertRaises(InvalidKeyError):
            encrypt("AB", [[1, 0], [0, 2]])
        with self.assertRaises(ValueError):
            key_from_args([9, 4, 2, 7, 99])


    def test_letter_mapping(self):
        self.assertEqual([letter_to_number(c) for c in "AYZ"], [1, 25, 0])

    def test_text_preparation(self):
        self.assertEqual(clean_text("Genshin Impact, is!"), "GENSHINIMPACTIS")
        self.assertEqual(pad_text("ABC", 2), "ABCX")

    def test_report_cases(self):
        for name, text, K, expected, _ in CASES:
            cipher, _, padded = encrypt(text, K)
            self.assertEqual(cipher, expected, name)
            plain, _, _ = decrypt(cipher, K)
            self.assertEqual(plain, padded, name)


def run_selftest():
    print("\n" + "=" * 60)
    print("🧪 RUNNING UNIT TESTS")
    print("=" * 60)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HillTests)
    result = unittest.TextTestRunner(verbosity=1, stream=sys.stdout).run(suite)
    return result.wasSuccessful()


def interactive_menu():
    """Friendly menu when run without arguments."""
    while True:
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "             🔐 HILL CIPHER TOOLKIT - MAIN MENU             ".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        print("  [1] 🚀 Run all analyses & unit tests ('all')")
        print("  [2] ✅ Verify report cases ('verify')")
        print("  [3] 🔑 Count valid keys ('count')")
        print("  [4] 🧩 Kernel & fixed blocks analysis ('fixed')")
        print("  [5] 🔓 Known-plaintext attack demo ('attack')")
        print("  [6] 🔒 Encrypt custom text")
        print("  [7] 🔓 Decrypt custom text")
        print("  [8] 🔍 Check key inverse & validity ('inverse') ✨NEW")
        print("  [9] 🧪 Run unit tests ('selftest')")
        print("  [0] 🚪 Exit")
        print("-" * 60)
        
        choice = input("👉 Enter your choice [0-9]: ").strip()
        
        if choice == '1':
            verify_cases()
            report_counts()
            report_fixed()
            report_attack()
            run_selftest()
        elif choice == '2':
            verify_cases()
        elif choice == '3':
            report_counts()
        elif choice == '4':
            report_fixed()
        elif choice == '5':
            report_attack()
        elif choice == '6':
            try:
                key_input = input("Enter key matrix entries separated by space (e.g. 9 4 2 7): ").split()
                key = [int(x) for x in key_input]
                text = input("Enter plaintext to encrypt: ")
                K = key_from_args(key)
                out, steps, padded = encrypt(text, K)
                print(f"\n✨ Prepared plaintext: {padded}")
                print(f"✨ Ciphertext       : {out}")
                show_s = input("Show step-by-step details? (y/n): ").lower()
                if show_s == 'y':
                    print(format_steps(steps, "Kx"))
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == '7':
            try:
                key_input = input("Enter key matrix entries separated by space (e.g. 8 1 9 3): ").split()
                key = [int(x) for x in key_input]
                text = input("Enter ciphertext to decrypt: ")
                K = key_from_args(key)
                out, steps, Kinv = decrypt(text, K)
                print(f"\n✨ K⁻¹ = {fmt_matrix(Kinv)}")
                print(f"✨ Plaintext : {out}")
                show_s = input("Show step-by-step details? (y/n): ").lower()
                if show_s == 'y':
                    print(format_steps(steps, "K⁻¹y"))
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '8':
            try:
                key_input = input("Enter key matrix entries separated by space (e.g. 9 4 2 7): ").split()
                key = [int(x) for x in key_input]
                K = key_from_args(key)
                d, d_mod, g, d_inv, Kinv, ok = inverse_report(K, MOD)
                print(f"\n--- Key Analysis Report ---")
                print(f"Matrix K = {fmt_matrix(K)}")
                print(f"Determinant det(K) = {d} ≡ {d_mod} (mod {MOD})")
                print(f"gcd(det(K), {MOD}) = {g} -> {'✅ Valid (Invertible)' if g == 1 else '❌ Invalid (Not Invertible)'}")
                if g == 1:
                    print(f"Modular inverse of det: {d_inv}")
                    print(f"Inverse matrix K⁻¹ = {fmt_matrix(Kinv)}")
                    print(f"Verification (K · K⁻¹ ≡ I mod 26): {'✅ PASS' if ok else '❌ FAIL'}")
                else:
                    print(f"⚠️ Note: Since gcd({d_mod}, 26) = {g} != 1, this matrix cannot be used as a Hill cipher key.")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == '9':
            run_selftest()
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.")
        input("\nPress Enter to return to the menu...")


def key_from_args(entries):
    n = math.isqrt(len(entries))
    if n * n != len(entries) or n < 2:
        raise ValueError("--key needs n*n integers (4 for a 2x2 key, 9 for a 3x3 key).")
    return [list(entries[i * n:(i + 1) * n]) for i in range(n)]


def main(argv=None):
    if argv is None and len(sys.argv) == 1:
        interactive_menu()
        return 0

    parser = argparse.ArgumentParser(description="Hill cipher toolkit (A=1,...,Y=25,Z=0; modulus 26).")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("encrypt", "decrypt"):
        p = sub.add_parser(name, help=f"{name} a text")
        p.add_argument("--key", type=int, nargs="+", required=True, help="matrix entries row by row")
        p.add_argument("--text", required=True)
        p.add_argument("--steps", action="store_true", help="show the block calculations")
    
    # Add inverse command
    p_inv = sub.add_parser("inverse", help="check key inverse, determinant, and validity")
    p_inv.add_argument("--key", type=int, nargs="+", required=True, help="matrix entries row by row")

    for name, text in (("count", "count valid keys"), ("fixed", "kernel test and fixed blocks"),
                        ("attack", "known-plaintext attack demonstration"),
                        ("verify", "verify the cases used in the report"),
                        ("selftest", "run the unit tests"), ("all", "run everything")):
        sub.add_parser(name, help=text)
    
    args = parser.parse_args(argv)

    try:
        if args.command in ("encrypt", "decrypt"):
            K = key_from_args(args.key)
            if args.command == "encrypt":
                out, steps, padded = encrypt(args.text, K)
                print(f"Prepared plaintext: {padded}")
                print(f"Ciphertext        : {out}")
            else:
                out, steps, Kinv = decrypt(args.text, K)
                print(f"K⁻¹ = {fmt_matrix(Kinv)}")
                print(f"Plaintext         : {out}")
            if args.steps:
                print(format_steps(steps, "Kx" if args.command == "encrypt" else "K⁻¹y"))
        elif args.command == "inverse":
            K = key_from_args(args.key)
            d, d_mod, g, d_inv, Kinv, ok = inverse_report(K, MOD)
            print(f"Matrix K = {fmt_matrix(K)}")
            print(f"Determinant det(K) = {d} ≡ {d_mod} (mod {MOD})")
            print(f"gcd(det(K), {MOD}) = {g} -> {'Valid' if g == 1 else 'Invalid'}")
            if g == 1:
                print(f"det⁻¹ (mod 26) = {d_inv}")
                print(f"K⁻¹ = {fmt_matrix(Kinv)}")
                print(f"Verification (K·K⁻¹ == I): {ok}")
            else:
                print("Error: Matrix is not invertible modulo 26.")
        elif args.command == "fixed":
            report_fixed()
        elif args.command == "attack":
            report_attack()
        elif args.command == "count":
            report_counts()
        elif args.command == "verify":
            return 0 if verify_cases() else 1
        elif args.command == "selftest":
            return 0 if run_selftest() else 1
        elif args.command == "all":
            ok = verify_cases()
            report_counts()
            report_fixed()
            report_attack()
            ok = run_selftest() and ok
            return 0 if ok else 1
    except (ValueError, InvalidKeyError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())