// Wrong way: a deleted constructor can't be called.
#include <string>
class Stream {
public:
    explicit Stream(int) {}
    Stream(bool) = delete;
};
int main() {
    Stream s{true};   // error: use of deleted function
}
