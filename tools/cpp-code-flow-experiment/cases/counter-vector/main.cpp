#include <cstdio>
#include <string>
#include <vector>

class Counter {
public:
    int total;
    explicit Counter(int start) : total(start) {}
    int add(int amount) {
        total += amount;
        return total;
    }
};

int twice(const Counter &c) {
    int doubled = c.total * 2;
    return doubled;
}

int main() {
    Counter c(3);
    Counter *p = &c;
    p->add(4);
    int t = twice(c);
    int arr[3] = {t, 1, 2};
    std::vector<int> v = {1, 2};
    v.push_back(arr[0]);
    std::string name = "mq";
    std::printf("%d %d %zu %s\n", c.total, t, v.size(), name.c_str());
    return 0;
}
