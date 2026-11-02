# Lesson 16.2: Embedded and real-time C++

<span class="stdtag">C++20</span> · about 13 minutes

## Why this matters

A microcontroller might have 64 KB of flash, 16 KB of RAM, no OS, and an interrupt that must be serviced in
2 µs. C++ is excellent here — templates and `constexpr` cost nothing at run time — but you have to choose the
right subset: no heap after startup, often no exceptions or RTTI, and very deliberate access to hardware.

## The embedded subset

- **No heap after init**: fragmentation and non-deterministic timing. Use static storage, fixed-capacity
  containers (`std::array`, the ring buffer capstone, C++26 `std::inplace_vector`), and pools.
- **Exceptions/RTTI** are often disabled (`-fno-exceptions -fno-rtti`) for code size and determinism; use
  error codes / `std::expected`.
- **Compute at compile time**: `constexpr` tables live in flash, not RAM.

## Hardware registers

```cpp
struct Uart { volatile std::uint32_t data, status, ctrl; };
inline Uart& uart0 = *reinterpret_cast<Uart*>(0x4000'1000);   // on real hardware
```

`volatile` tells the compiler every access matters (it can't cache or remove them). C++20 deprecated
compound operations like `reg |= bit` on volatile because they suggest atomicity that doesn't exist; write
`reg = reg | bit`. Below we simulate a register block in RAM so the example runs anywhere.

```cpp title="examples/week16/lesson02.cpp"
--8<-- "examples/week16/lesson02.cpp"
```

**Output**:

```text
--8<-- "examples/week16/lesson02.out"
```

## Fixed-point

Many MCUs lack an FPU. Q15 fixed-point stores values in [-1, 1) as `int16_t` scaled by 2^15; multiplication
is `(a * b) >> 15` in 32-bit. The example implements a Q15 gain with saturation.

## Sharing with interrupts

An ISR and the main loop share data like threads do. Use `std::atomic` (if lock-free on the target) or a
critical section (disable interrupts briefly). The SPSC ring buffer from Week 14 is the classic ISR→main
channel — see Capstone B.

## Key takeaways

!!! success "Key takeaways"
    - Embedded C++ avoids the heap after init and often disables exceptions/RTTI.
    - `volatile` is for hardware registers; avoid compound ops on volatile (deprecated in C++20).
    - `constexpr` tables, fixed-point math and static pools give deterministic, small code.
    - Share data with ISRs via lock-free atomics or brief critical sections (SPSC ring buffer).

## Quiz

**Q1.** Why avoid dynamic allocation after startup on an MCU?

??? question "Show answer"
    Fragmentation and non-deterministic timing can cause failures or missed deadlines.

**Q2.** Why did C++20 deprecate `reg |= bit` on a volatile?

??? question "Show answer"
    It looks atomic but is a separate read and write; writing it out makes the two accesses explicit.

**Q3.** What is 0.5 × 0.25 in Q15 as an integer?

??? question "Show answer"
    4096 (0.125 × 32768).

