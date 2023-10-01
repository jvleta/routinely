#ifndef ROUTINE_BUILDER_HPP
#define ROUTINE_BUILDER_HPP

#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

namespace {
constexpr int kNumChoicesPerDay = 4;
constexpr int kNumTotalChoices = 7;

std::map<int, std::string> options{
    {1, "scsles"},
    {2, "chords"},
    {3, "arpeggios"},
    {4, "finger picking"},
    {5, "alternate picking"},
    {6, "ear training"},
    {7, "song practice"},
};

std::random_device rd;
std::mt19937 g(rd());
void print_choices(std::vector<int> choices, std::string message) {
  std::cout << message << " ";
  std::cout << "[ ";
  for (const auto &choice : choices) {
    std::cout << choice << " ";
  }
  std::cout << "]\n";
}

void print_counts(std::map<int, int> data) {
  for (const auto pair : data) {
    auto [index, count] = pair;
    std::cout << index << " " << count << "\n";
  }
}

std::vector<int> get_choices(std::vector<int> options, int num_choices) {
  std::shuffle(options.begin(), options.end(), g);
  std::vector<int> subset = {options.begin(), options.begin() + num_choices};
  std::sort(subset.begin(), subset.end());
  return subset;
}

std::vector<int> generate_all_choices(int num_choices) {
  std::vector<int> choices(num_choices);
  std::iota(choices.begin(), choices.end(), 1);
  return choices;
}

std::vector<int>
get_todays_choices(std::vector<int> not_chosen_two_consecutive_days,
                   std::vector<int> all_choices) {
  std::vector<int> todays_choices;

  if (!not_chosen_two_consecutive_days.empty()) {
    auto choices = get_choices(not_chosen_two_consecutive_days,
                               not_chosen_two_consecutive_days.size());
    std::copy(choices.begin(), choices.end(),
              std::back_inserter(todays_choices));
  }

  if (todays_choices.size() < kNumChoicesPerDay) {
    std::vector<int> not_chosen_yet;
    std::set_difference(all_choices.begin(), all_choices.end(),
                        todays_choices.begin(), todays_choices.end(),
                        std::back_inserter(not_chosen_yet));
    auto choices =
        get_choices(not_chosen_yet, kNumChoicesPerDay - todays_choices.size());
    std::copy(choices.begin(), choices.end(),
              std::back_inserter(todays_choices));
    std::sort(todays_choices.begin(), todays_choices.end());
  }

  return todays_choices;
}
} // namespace

namespace builder {
void build() {
  const auto all_choices = generate_all_choices(kNumTotalChoices);

  std::vector<std::string> weekdays{"Sunday",    "Monday",   "Tuesday",
                                    "Wednesday", "Thursday", "Friday",
                                    "Saturday"};

  std::vector<int> not_chosen;
  std::vector<int> not_chosen_two_consecutive_days;
  for (const auto &day : weekdays) {
    const auto todays_choices =
        get_todays_choices(not_chosen_two_consecutive_days, all_choices);

    std::cout << day << "\n";
    for (auto choice : todays_choices) {
      std::cout << options[choice] << "\n";
    }
    std::cout << "\n";

    std::set_difference(all_choices.begin(), all_choices.end(),
                        todays_choices.begin(), todays_choices.end(),
                        std::back_inserter(not_chosen));

    not_chosen_two_consecutive_days.clear();
    for (const auto choice : all_choices) {
      int n = std::count(not_chosen.begin(), not_chosen.end(), choice);
      if (n == 2) {
        not_chosen_two_consecutive_days.push_back(choice);
        auto start = std::remove(not_chosen.begin(), not_chosen.end(), choice);
        not_chosen.erase(start, not_chosen.end());
      }
    }
  }
}
} // namespace builder

#endif