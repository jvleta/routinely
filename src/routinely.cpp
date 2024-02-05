#include "routinely.hpp"

#include <iostream>
#include <map>
#include <nlohmann/json.hpp>
#include <random>
#include <ranges>
#include <string>
#include <vector>

using json = nlohmann::json;

using size_type = std::vector<int>::size_type;

namespace {
constexpr int kMaxAllowedSkips = 2;
constexpr int kNumChoicesPerDay = 4;
constexpr int kNumTotalChoices = 8;

std::random_device seed;
std::mt19937 rng(seed());

std::vector<int> get_random_subset(const std::vector<int>& values,
                                   size_type size) {
  std::vector<int> subset = values;
  std::ranges::shuffle(subset, rng);
  subset.resize(size);
  std::ranges::sort(subset);
  return subset;
}

std::vector<int> get_ordered_integer_sequence(size_type size) {
  std::vector<int> values(size);
  std::iota(values.begin(), values.end(), 0);
  return values;
}

}  // namespace

std::vector<int> get_todays_choices(const std::vector<int>& prioritized_choices,
                                    const std::vector<int>& all_choices) {
  std::vector<int> todays_choices;

  if (!prioritized_choices.empty()) {
    todays_choices =
        get_random_subset(prioritized_choices, prioritized_choices.size());
  }

  if (todays_choices.size() < kNumChoicesPerDay) {
    std::vector<int> not_chosen_yet;
    std::ranges::set_difference(all_choices, todays_choices,
                                std::back_inserter(not_chosen_yet));
    std::ranges::copy(
        get_random_subset(not_chosen_yet,
                          kNumChoicesPerDay - todays_choices.size()),
        std::back_inserter(todays_choices));

    std::ranges::sort(todays_choices);
  }

  return todays_choices;
}

bool choice_should_be_prioritized(const int choice,
                                  const std::vector<int>& not_chosen) {
  const auto count = std::ranges::count(not_chosen, static_cast<long>(choice));
  return convert<int>(count) == kMaxAllowedSkips;
}

void remove_from_not_chosen(const int choice, std::vector<int>& not_chosen) {
  auto start = std::remove(not_chosen.begin(), not_chosen.end(), choice);
  not_chosen.erase(start, not_chosen.end());
}

void prepare_for_next_iteration(const std::vector<int>& all_choices,
                                const std::vector<int>& todays_choices,
                                std::vector<int>& not_chosen,
                                std::vector<int>& prioritized_choices) {
  std::ranges::set_difference(all_choices, todays_choices,
                              std::back_inserter(not_chosen));
  prioritized_choices.clear();
  for (const int choice : all_choices) {
    if (choice_should_be_prioritized(choice, not_chosen)) {
      prioritized_choices.push_back(choice);
      remove_from_not_chosen(choice, not_chosen);
    }
  }
}

namespace builder {

std::vector<std::vector<int>> build(int num_days) {
  std::vector<std::string> current_focus_areas{"Speed Training",
                           "Cream and Sugar exercises",
                           "Giuliani Arpeggios 6-20",
                           "Chord Chemistry",
                           "What a Wonderful World",
                           "Day Tripper",
                           "Interval Training",
                           "Improvising"};

  std::vector<std::vector<int>> rows;
  const auto all_choices =
      get_ordered_integer_sequence(convert<size_type>(kNumTotalChoices));

  const auto day_indices =
      get_ordered_integer_sequence(convert<size_type>(num_days));

  std::vector<int> not_chosen;
  std::vector<int> prioritized_choices;

  std::ranges::for_each(day_indices, [&](int index) {
    const auto todays_choices =
        get_todays_choices(prioritized_choices, all_choices);

    prepare_for_next_iteration(all_choices, todays_choices, not_chosen,
                               prioritized_choices);
    std::cout << index + 1 << "\n";
    std::ranges::for_each(todays_choices,
                          [&current_focus_areas](int i) { std::cout << current_focus_areas[i]<< "\n"; });
    std::cout << "\n\n";
    rows.push_back(todays_choices);
  });

  return rows;
}

}  // namespace builder
