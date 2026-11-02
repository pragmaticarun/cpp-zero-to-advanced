# Week 4 programming assignment: A Rational number type

Implement `class Rational` (numerator/denominator, `long long`):

1. Invariant: denominator > 0 and the fraction is always reduced (use `std::gcd` from `<numeric>`).
   The constructor throws `std::invalid_argument` on a zero denominator.
2. `+ - * /` via the compound-assignment pattern; `explicit operator double()`.
3. Comparisons with `<=>` — careful: a defaulted `<=>` would compare numerators first, which is wrong for
   fractions! Write a custom `operator<=>` that cross-multiplies, plus a defaulted `operator==` (correct
   because fractions are always reduced).
4. `operator<<` printing `3/4`.

??? tip "Reference solution"
    ```cpp title="examples/week04/assignment_solution.cpp"
    --8<-- "examples/week04/assignment_solution.cpp"
    ```

    **Output:**

    ```text
    --8<-- "examples/week04/assignment_solution.out"
    ```

