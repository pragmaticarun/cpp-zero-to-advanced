# Capstone B: An embedded fixed-capacity ring buffer

## The problem

A microcontroller samples a sensor in an interrupt at 8 kHz; the main loop filters and transmits the data.
You need a buffer that: never allocates, has bounded and predictable timing, can be used in `constexpr`
code and tests, supports an overwrite-oldest policy for "latest N readings" use cases, and has a lock-free
variant for the ISR→main-loop hand-off.

## Requirements

1. `RingBuffer<T, N>`: `push` / `pop` / `peek` / indexing (0 = oldest) / iteration, `full`, `empty`,
   `clear`; overflow policy **reject** or **overwrite oldest** (with a counter).
2. All operations `noexcept` for trivially copyable `T`, and usable in constant expressions.
3. `SpscRing<T, N>`: lock-free single-producer/single-consumer, power-of-two capacity, drop counter.
4. No heap allocation anywhere; `static_assert`s for misuse (zero capacity, non-power-of-two, non-trivial
   ISR payloads, non-lock-free atomics).
5. Tests run under ASan/UBSan; the SPSC test runs under TSan.

## The library

```cpp title="examples/capstone/ring_buffer.hpp"
--8<-- "examples/capstone/ring_buffer.hpp"
```

Design notes:

- The single-threaded buffer stores `head` and `size` (not head/tail), so it uses all N slots. The SPSC
  version must keep one slot empty, because head and tail are written by different threads.
- `constexpr` everything: the tests below include `static_assert`-based tests that run inside the compiler.
- On a real MCU you'd check `is_always_lock_free` for `std::size_t` atomics (some 8-bit targets fail), or
  use a critical section instead.

## Tests

```cpp title="examples/capstone/ringbuffer_tests.cpp"
--8<-- "examples/capstone/ringbuffer_tests.cpp"
```

**Output**:

```text
--8<-- "examples/capstone/ringbuffer_tests.out"
```

## Demo: a simulated sensor ISR

A thread stands in for the interrupt; the main loop drains the SPSC ring and keeps a moving average of the
last 8 readings in an overwrite-oldest `RingBuffer`.

```cpp title="examples/capstone/ringbuffer_demo.cpp"
--8<-- "examples/capstone/ringbuffer_demo.cpp"
```

**Output**:

```text
--8<-- "examples/capstone/ringbuffer_demo.out"
```

## Extensions

- Bulk `push_n`/`pop_n` with `std::span` for DMA transfers.
- A `std::ranges`-compatible random-access iterator.
- Port to a real board (e.g. an STM32 with `arm-none-eabi-g++ -fno-exceptions -fno-rtti`) and measure
  cycles per push.
- Replace your own buffer with C++26 `std::inplace_vector` where a FIFO isn't needed.
