#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

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
  return {options.begin(), options.begin() + num_choices};
}

int main() {
  std::vector<int> all_choices{1, 2, 3, 4, 5, 6, 7, 8};
  std::vector<std::string> weekdays{"Monday",   "Tuesday", "Wednesday",
                                    "Thursday", "Friday",  "Saturday",
                                    "Sunday"};

  std::vector<int> not_chosen;
  std::vector<int> on_deck;

  for (const auto &day : weekdays) {
    std::vector<int> todays_choices;

    if (!on_deck.empty()) {
      if (on_deck.size() > 4) {
        std::cout << "\n\nAAAAAHHHHHHHHH\n\n";
      }
      auto choices = get_choices(on_deck, on_deck.size());
      std::copy(choices.begin(), choices.end(),
                std::back_inserter(todays_choices));
    }

    if (todays_choices.size() < 4) {

      std::vector<int> not_chosen_yet;
      std::sort(todays_choices.begin(), todays_choices.end());
      std::set_difference(all_choices.begin(), all_choices.end(),
                          todays_choices.begin(), todays_choices.end(),
                          std::back_inserter(not_chosen_yet));
      auto choices = get_choices(not_chosen_yet, 4 - todays_choices.size());
      std::copy(choices.begin(), choices.end(),
                std::back_inserter(todays_choices));
    }

    std::cout << day << "\n";

    std::sort(todays_choices.begin(), todays_choices.end());
    print_choices(todays_choices, "final list of today's choices");

    std::set_difference(all_choices.begin(), all_choices.end(),
                        todays_choices.begin(), todays_choices.end(),
                        std::back_inserter(not_chosen));

    print_choices(not_chosen, "not chosen");

    on_deck.clear();
    for (const auto choice : all_choices) {
      int n = std::count(not_chosen.begin(), not_chosen.end(), choice);
      if (n == 2) {
        on_deck.push_back(choice);
        auto start = std::remove(not_chosen.begin(), not_chosen.end(), choice);
        not_chosen.erase(start, not_chosen.end());
      }
    }
  }
}
