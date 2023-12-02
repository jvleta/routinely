#include "routinely.hpp"

#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <random>
#include <ranges>
#include <string>
#include <vector>

using json = nlohmann::json;

using diff_type = std::vector<int>::difference_type;
using size_type = std::vector<int>::size_type;

namespace {
constexpr int kNumChoicesPerDay = 4;
constexpr int kNumTotalChoices = 7;

std::random_device seed;
std::mt19937 rng(seed());

std::vector<int> get_random_subset(std::vector<int>& values, diff_type size) {
  std::vector<int> subset;
  std::for_each(values.begin(), values.begin() + size,
                [&](auto val) { subset.push_back(val); });
  std::ranges::sort(subset);
  return subset;
}

std::vector<int> get_ordered_integer_sequence(auto size) {
  std::vector<int> values(static_cast<std::vector<int>::size_type>(size));
  std::iota(values.begin(), values.end(), 0);
  return values;
}

}  // namespace

namespace builder {

std::vector<int> get_todays_choices(
    std::vector<int>& not_chosen_two_consecutive_days,
    std::vector<int>& all_choices) {
  std::vector<int> todays_choices;

  if (!not_chosen_two_consecutive_days.empty()) {
    todays_choices = get_random_subset(
        not_chosen_two_consecutive_days,
        convert<diff_type>(not_chosen_two_consecutive_days.size()));
  }

  if (todays_choices.size() < kNumChoicesPerDay) {
    std::vector<int> not_chosen_yet;
    std::ranges::set_difference(all_choices, todays_choices,
                                std::back_inserter(not_chosen_yet));
    auto n = convert<diff_type>(kNumChoicesPerDay - todays_choices.size());

    std::ranges::copy(get_random_subset(not_chosen_yet, n),
                      std::back_inserter(todays_choices));

    std::ranges::sort(todays_choices);
  }
  return todays_choices;
}

std::string build(int num_days) {
  const auto to_size_type = [](auto n) {
    return static_cast<std::vector<int>::size_type>(n);
  };
  json output;
  auto all_choices = get_ordered_integer_sequence(kNumTotalChoices);

  std::vector<int> days(to_size_type(num_days));
  std::iota(days.begin(), days.end(), 0);

  std::vector<int> not_chosen;
  std::vector<int> not_chosen_two_consecutive_days;

  std::for_each(days.begin(), days.end(), [&](int) {
    const auto todays_choices =
        get_todays_choices(not_chosen_two_consecutive_days, all_choices);

    output.push_back(todays_choices);

    std::set_difference(all_choices.begin(), all_choices.end(),
                        todays_choices.begin(), todays_choices.end(),
                        std::back_inserter(not_chosen));

    not_chosen_two_consecutive_days.clear();
    for (const int choice : all_choices) {
      auto num_times_not_chosen = std::count(
          not_chosen.begin(), not_chosen.end(), static_cast<long>(choice));
      if (num_times_not_chosen == 2) {
        not_chosen_two_consecutive_days.push_back(choice);
        auto start = std::remove(not_chosen.begin(), not_chosen.end(), choice);
        not_chosen.erase(start, not_chosen.end());
      }
    }
  });

  return output.dump(4);
}

}  // namespace builder
