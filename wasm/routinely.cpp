#include "routinely.hpp"

#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <random>
#include <ranges>
#include <string>
#include <vector>

using json = nlohmann::json;

namespace {
constexpr int kNumChoicesPerDay = 4;
constexpr int kNumTotalChoices = 7;

std::random_device seed;
std::mt19937 rng(seed());

std::vector<int> get_random_subset(std::vector<int> values, int size) {
  std::ranges::shuffle(values, rng);
  std::vector<int> subset = {values.begin(), values.begin() + size};
  std::ranges::sort(subset);
  return subset;
}

std::vector<int> get_ordered_integer_sequence(int size) {
  std::vector<int> values(size);
  std::iota(values.begin(), values.end(), 0);
  return values;
}

std::vector<int> get_todays_choices(
    std::vector<int> not_chosen_two_consecutive_days,
    std::vector<int> all_choices) {
  std::vector<int> todays_choices;

  if (!not_chosen_two_consecutive_days.empty()) {
    todays_choices = get_random_subset(not_chosen_two_consecutive_days,
                               not_chosen_two_consecutive_days.size());
  }

  if (todays_choices.size() < kNumChoicesPerDay) {
    std::vector<int> not_chosen_yet;
    std::ranges::set_difference(all_choices, todays_choices,
                                std::back_inserter(not_chosen_yet));

    std::ranges::copy(
        get_random_subset(not_chosen_yet, kNumChoicesPerDay - todays_choices.size()),
        std::back_inserter(todays_choices));

    std::ranges::sort(todays_choices);
  }
  return todays_choices;
}
}  // namespace

namespace builder {

std::string build(const int num_days) {
  json output;
  const auto all_choices = get_ordered_integer_sequence(kNumTotalChoices);

  std::vector<int> days(num_days);
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
    for (const auto choice : all_choices) {
      int num_times_not_chosen =
          std::count(not_chosen.begin(), not_chosen.end(), choice);
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
