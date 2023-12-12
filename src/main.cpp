#include <CLI/CLI.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "routinely.hpp"

std::vector<std::string> read_lines(const std::filesystem::path& path) {
  std::vector<std::string> lines;
  std::string line;
  std::ifstream file(path);
  if (file.is_open()) {
    while (getline(file, line)) {
      lines.push_back(line);
    }
    file.close();
  }
  return lines;
}

int main(int argc, char* argv[]) {
  CLI::App app{"Routinely"};

  int num_days = 1;
  std::string filename = "";
  app.add_option("-n,--number", num_days,
                 "number of days to include in practice plan");
  app.add_option("-f,--filename", filename, "schema file");

  CLI11_PARSE(app, argc, argv)

  std::filesystem::path path = filename;

  builder::build(num_days);
}
