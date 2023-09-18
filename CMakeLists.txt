cmake_minimum_required(VERSION 3.20)

# Define the project name and where to report bugs.
set(PACKAGE_BUGREPORT
    "https://github.com/GoogleCloudPlatform/cpp-samples/issues")
project(practice CXX)

find_package(functions_framework_cpp REQUIRED)
find_package(Threads)

add_executable(practice main.cpp)
target_compile_features(practice PRIVATE cxx_std_17)
target_link_libraries(practice functions-framework-cpp::framework)

include(GNUInstallDirs)
install(TARGETS practice RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})