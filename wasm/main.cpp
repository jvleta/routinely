#include <CLI/CLI.hpp>
#include <iostream>

#include "routinely.hpp"

constexpr int default_num_days = 30;

int main(int argc, char* argv[]) {
  CLI::App app{"Routinely"};

  int num_days = 1;

  app.add_option("-n,--number", num_days,
                 "number of days to include in practice plan");

  CLI11_PARSE(app, argc, argv)

  const auto output = builder::build(num_days);
  std::cout << output;
}
