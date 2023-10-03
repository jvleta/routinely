#include "routinely.hpp"

int main() {
  constexpr int num_days = 1;
  const auto output = builder::build(num_days);
  std::cout << output;
}
