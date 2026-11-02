# Lesson 3.5: Bits and bytes: bitwise operators, std::byte, and <bit>

<span class="stdtag">C++23</span> · about 11 minutes

## Why this matters

An H.264 NAL unit header packs three fields into a single byte: 1 bit, 2 bits and 5 bits. Hardware
registers, flags, compression, hashing — all of it is bit twiddling. C++ gives you direct access to bits,
and C++20 finally added a proper `<bit>` header so you no longer need compiler-specific builtins. Let's
decode that header.

## The operators

| Op | Meaning | Typical use |
|---|---|---|
| `a & b` | AND | test/clear bits with a mask |
| `a \| b` | OR | set bits |
| `a ^ b` | XOR | toggle bits |
| `~a` | NOT | invert (build "clear" masks) |
| `a << n`, `a >> n` | shift | move fields into place |

Extracting a field = **shift it down, then mask it**: `(byte >> 5) & 0b11` gives bits 5–6.

## Pitfalls

- Shifting by a count `>=` the width of the (promoted) type is **UB**: `1u << 32` on a 32-bit `unsigned`.
- `1 << 31` on `int`: before C++20 this was UB; since C++20 signed integers are defined to be two's
  complement and left shift is well-defined — but stick to **unsigned types** for bit manipulation anyway.
- Remember integer promotion: `~std::uint8_t{0x0F}` is an `int` `0xFFFFFFF0`, not `0xF0`.

## `std::byte` (C++17)

`std::byte` is "a byte of raw memory", not a character and not a number. It only supports bitwise ops,
so you can't accidentally do arithmetic on it. Use `std::to_integer<int>(b)` to read it.

## `<bit>` (C++20)

Portable versions of things you used to need intrinsics for: `std::popcount`, `std::countl_zero`,
`std::countr_zero`, `std::rotl`/`rotr`, `std::has_single_bit` (power of two?), `std::bit_ceil`,
`std::bit_width`, and `std::bit_cast` — the *safe* way to reinterpret an object's bits as another type of
the same size. C++23 added `std::byteswap`, and `std::endian` (C++20) tells you the platform byte order.

```cpp title="examples/week03/lesson05.cpp"
--8<-- "examples/week03/lesson05.cpp"
```

**Output**:

```text
--8<-- "examples/week03/lesson05.out"
```

## The wrong way to reinterpret bits

```cpp
float f = 1.0f;
std::uint32_t u = *reinterpret_cast<std::uint32_t*>(&f);   // WRONG: violates strict aliasing (UB)
std::uint32_t ok = std::bit_cast<std::uint32_t>(f);          // right (C++20); or std::memcpy
```

!!! tip "Pro tip: ring buffers love powers of two"
    If a buffer's capacity is a power of two, `index & (capacity - 1)` replaces the slower
    `index % capacity`. You'll use exactly this in the embedded capstone.

## Key takeaways

!!! success "Key takeaways"
    - Extract a bit field with shift-then-mask; use unsigned types for bit manipulation.
    - Shifting by >= the type width is UB; watch integer promotion with `~` on small types.
    - `std::byte` is raw memory, not a number; `<bit>` gives portable popcount, rotations, `bit_cast` etc.
    - Use `std::bit_cast` or `memcpy`, never `reinterpret_cast`, to reinterpret an object's bits.

## Quiz

**Q1.** How do you extract bits 2..4 (3 bits) of `x`?

??? question "Show answer"
    `(x >> 2) & 0b111`.

**Q2.** What is the type and value of `~std::uint8_t{0}`?

??? question "Show answer"
    `int`, value `-1` (all bits set), due to integer promotion before `~`.

**Q3.** Why is `*reinterpret_cast<int*>(&some_float)` wrong?

??? question "Show answer"
    It violates the strict aliasing rule (accessing a float object through an int glvalue), which is UB. Use `std::bit_cast<int>(f)` or `std::memcpy`.

**Q4.** What does `std::has_single_bit(x)` tell you?

??? question "Show answer"
    Whether `x` is a power of two.

