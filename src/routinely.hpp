#ifndef ROUTINE_BUILDER_HPP
#define ROUTINE_BUILDER_HPP

#include <string>

template <typename T>
T convert(auto n) {
  return static_cast<T>(n);
}

namespace builder {

std::vector<std::vector<int>> build(int num_days);

}  // namespace builder

#endif
