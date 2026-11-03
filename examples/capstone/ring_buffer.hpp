// ring_buffer.hpp — Capstone B: fixed-capacity ring buffers for embedded / real-time code.
// No heap, no exceptions required, constexpr-friendly single-threaded variant,
// and a lock-free SPSC variant safe between an ISR (producer) and the main loop (consumer).
#pragma once
#include <array>
#include <atomic>
#include <cstddef>
#include <new>
#include <optional>
#include <type_traits>
#include <utility>

namespace embedded {

// Single-threaded ring buffer. Usable in constant expressions.
template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "capacity must be positive");
    static_assert(std::is_trivially_copyable_v<T> || std::is_nothrow_move_assignable_v<T>,
                  "T must be cheap and safe to move in real-time code");
public:
    using value_type = T;
    enum class Overflow { reject, overwrite_oldest };

    constexpr explicit RingBuffer(Overflow policy = Overflow::reject) noexcept : policy_{policy} {}

    [[nodiscard]] constexpr bool push(const T& v) noexcept(std::is_nothrow_copy_assignable_v<T>) {
        if (full()) {
            if (policy_ == Overflow::reject) return false;
            head_ = next(head_); --size_; ++overwritten_;
        }
        data_[(head_ + size_) % N] = v;
        ++size_;
        return true;
    }
    [[nodiscard]] constexpr std::optional<T> pop() noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (empty()) return std::nullopt;
        T v = std::move(data_[head_]);
        head_ = next(head_); --size_;
        return v;
    }
    [[nodiscard]] constexpr const T* peek() const noexcept { return empty() ? nullptr : &data_[head_]; }
    [[nodiscard]] constexpr const T& operator[](std::size_t i) const noexcept { return data_[(head_ + i) % N]; }  // 0 = oldest
    constexpr void clear() noexcept { head_ = size_ = 0; }

    [[nodiscard]] constexpr std::size_t size() const noexcept { return size_; }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return N; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return size_ == N; }
    [[nodiscard]] constexpr std::size_t overwritten() const noexcept { return overwritten_; }

    // Minimal forward iteration, oldest to newest
    class const_iterator {
    public:
        using value_type = T; using difference_type = std::ptrdiff_t;
        constexpr const_iterator() = default;
        constexpr const_iterator(const RingBuffer* rb, std::size_t i) : rb_{rb}, i_{i} {}
        constexpr const T& operator*() const { return (*rb_)[i_]; }
        constexpr const_iterator& operator++() { ++i_; return *this; }
        constexpr const_iterator operator++(int) { auto t = *this; ++i_; return t; }
        constexpr bool operator==(const const_iterator&) const = default;
    private:
        const RingBuffer* rb_ = nullptr;
        std::size_t i_ = 0;
    };
    [[nodiscard]] constexpr const_iterator begin() const noexcept { return {this, 0}; }
    [[nodiscard]] constexpr const_iterator end() const noexcept { return {this, size_}; }

private:
    static constexpr std::size_t next(std::size_t i) noexcept { return (i + 1) % N; }
    std::array<T, N> data_{};
    std::size_t head_ = 0, size_ = 0, overwritten_ = 0;
    Overflow policy_;
};

// Lock-free single-producer / single-consumer ring (e.g. ISR -> main loop).
// Capacity N must be a power of two; usable capacity is N - 1.
template <typename T, std::size_t N>
class SpscRing {
    static_assert(N >= 2 && (N & (N - 1)) == 0, "N must be a power of two");
    static_assert(std::is_trivially_copyable_v<T>, "keep ISR payloads trivially copyable");
    static_assert(std::atomic<std::size_t>::is_always_lock_free, "needs lock-free atomics on this target");
public:
    [[nodiscard]] bool push(const T& v) noexcept {            // producer only
        const auto t = tail_.load(std::memory_order_relaxed);
        const auto n = (t + 1) & (N - 1);
        if (n == head_.load(std::memory_order_acquire)) { dropped_.fetch_add(1, std::memory_order_relaxed); return false; }
        buf_[t] = v;
        tail_.store(n, std::memory_order_release);
        return true;
    }
    [[nodiscard]] std::optional<T> pop() noexcept {           // consumer only
        const auto h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) return std::nullopt;
        T v = buf_[h];
        head_.store((h + 1) & (N - 1), std::memory_order_release);
        return v;
    }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return N - 1; }
    [[nodiscard]] std::size_t dropped() const noexcept { return dropped_.load(std::memory_order_relaxed); }
private:
    std::array<T, N> buf_{};
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
    alignas(64) std::atomic<std::size_t> dropped_{0};
};

}  // namespace embedded
