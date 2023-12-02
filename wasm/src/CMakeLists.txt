add_executable(routinely routinely.hpp routinely.cpp main.cpp)

target_link_libraries(routinely PRIVATE routinely::routinely_options routinely::routinely_warnings)

target_link_system_libraries(routinely PRIVATE CLI11::CLI11 nlohmann_json::nlohmann_json)
#           fmt::fmt
#           spdlog::spdlog
#           lefticus::tools
#           ftxui::screen
#           ftxui::dom
#           ftxui::component)
