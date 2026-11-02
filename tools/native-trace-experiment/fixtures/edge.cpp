#include <cmath>
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

struct Node {
    int value;
    Node *next;
};

struct Pair {
    Node first;
    int tail;
};

int depth(int n) {
    if (n == 0) return 0;
    return depth(n - 1) + 1;
}

int add(int a, int b) {
    return a + b;
}

int main() {
    int unset;
    Node a{1, nullptr};
    Node b{2, &a};
    a.next = &b;
    Pair pair{{3, nullptr}, 4};
    Node *inner = &pair.first;
    int level = add(add(1, 2), add(3, 4));
    int deep = depth(2);
    double nan = std::nan("");
    auto first = std::make_unique<int>(5);
    auto second = std::move(first);
    std::vector<int> source = {1, 2};
    std::vector<int> target = std::move(source);
    int *dangling = new int(8);
    delete dangling;
    std::cout << level << " " << deep << " " << std::isnan(nan) << " " << *second << " " << target.size() << " " << inner->value << "\n";
    unset = 0;
    return unset;
}
