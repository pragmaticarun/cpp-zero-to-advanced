# Lesson 12.6: std::chrono: durations, clocks, calendars, and time zones

<span class="stdtag">C++20</span> · about 12 minutes

## Why this matters

"Wait 50 ms." "How long did encoding take?" "What's the date three months from now?" "What time is this
UTC timestamp in India?" Getting time wrong produces subtle bugs: mixing up seconds and milliseconds, using a
wall clock that jumps for measuring intervals, or doing time-zone math by hand. `<chrono>` makes units part
of the type, so many of those bugs become compile errors.

## Durations carry units

```cpp
using namespace std::chrono_literals;
auto timeout = 250ms;
std::chrono::seconds s = 3min;          // OK: lossless conversion is implicit
std::chrono::seconds t = 1500ms;        // compile error: lossy! use duration_cast/floor/round
```

## Pick the right clock

| Clock | Use for |
|---|---|
| `steady_clock` | measuring intervals and timeouts (never goes backwards) |
| `system_clock` | wall-clock time, timestamps, dates |
| `high_resolution_clock` | usually an alias of one of the above — don't rely on it |

## Calendars and time zones (C++20)

`2026y/std::chrono::March/31` is a `year_month_day`. Adding months to the 31st gives an *invalid* date that
you must handle explicitly (clamp to last day, or overflow into the next month) — chrono makes you choose.
`zoned_time` converts between UTC and IANA time zones using the time-zone database.

```cpp title="examples/week12/lesson06.cpp"
--8<-- "examples/week12/lesson06.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson06.out"
```

Time-zone support needs the tz database at run time and library support (GCC 14 and MSVC have it;
libc++ support is recent/partial), so that part is a separate example marked "may be unsupported":

```cpp title="examples/week12/lesson06_tz.cpp"
--8<-- "examples/week12/lesson06_tz.cpp"
```

**Output**:

```text
--8<-- "examples/week12/lesson06_tz.out"
```

!!! tip "Pro tip"
    Store and transmit timestamps in UTC (`system_clock` / `sys_seconds`); convert to local time zones only
    for display.

## Key takeaways

!!! success "Key takeaways"
    - Durations encode units; lossy conversions require `duration_cast`, `floor`, `ceil` or `round`.
    - Use `steady_clock` for intervals, `system_clock` for timestamps.
    - C++20 calendar types make invalid dates explicit; you choose how to normalize.
    - Store UTC; convert with `zoned_time` only for display (needs tzdb support).

## Quiz

**Q1.** Why does `std::chrono::seconds s = 1500ms;` not compile?

??? question "Show answer"
    The conversion would lose information (truncate), so it must be explicit.

**Q2.** Which clock should measure how long a function takes?

??? question "Show answer"
    `std::chrono::steady_clock` — it's monotonic and unaffected by wall-clock adjustments.

**Q3.** What is `2026y/January/31 + months{1}`?

??? question "Show answer"
    `2026-02-31`, an invalid `year_month_day` (`ok()` is false) that you must clamp or normalize.

