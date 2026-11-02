#include <functional>
#include <iostream>
#include <queue>
#include <stack>
#include <string>
#include <vector>

struct Job {
    int priority; std::string name;
    bool operator<(const Job& o) const { return priority < o.priority; }
};

int main() {
    std::stack<std::string> undo;
    for (auto op : {"add track", "trim", "fade"}) undo.push(op);
    std::cout << "undo: " << undo.top() << '\n';
    undo.pop();
    std::cout << "then: " << undo.top() << '\n';

    std::queue<int> packets;
    for (int i = 1; i <= 3; ++i) packets.push(i);
    std::cout << "first packet: " << packets.front() << ", last: " << packets.back() << '\n';

    std::priority_queue<Job> jobs;
    jobs.push({1, "thumbnail"});
    jobs.push({5, "encode audio"});
    jobs.push({3, "upload"});
    while (!jobs.empty()) { std::cout << jobs.top().priority << ':' << jobs.top().name << ' '; jobs.pop(); }
    std::cout << '\n';

    std::priority_queue<int, std::vector<int>, std::greater<>> min_heap;   // smallest first
    for (int t : {30, 10, 20}) min_heap.push(t);
    std::cout << "next timer fires at " << min_heap.top() << "ms\n";
}
