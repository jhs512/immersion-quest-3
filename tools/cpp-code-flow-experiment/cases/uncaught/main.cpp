#include <cstdio>
#include <stdexcept>

int fail(int v) {
    int doubled = v * 2;
    throw std::runtime_error("boom");
    return doubled;
}

int main() {
    int x = 4;
    std::printf("before\n");
    int y = fail(x);
    std::printf("%d\n", y);
    return 0;
}
