cmake_minimum_required(VERSION 3.21)

# Only set the cxx_standard if it is not set by someone else
if (NOT DEFINED CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 20)
endif()

# strongly encouraged to enable this globally to avoid conflicts between
# -Wpedantic being enabled and -std=c++20 and -std=gnu++20 for example
# when compiling with PCH enabled
set(CMAKE_CXX_EXTENSIONS OFF)

# Set the project name and language
project(
  routinely
  VERSION 0.0.1
  DESCRIPTION ""
  HOMEPAGE_URL "https://github.com/jvleta/routinely"
  LANGUAGES CXX C)

include(ProjectOptions.cmake)


routinely_setup_options()

routinely_global_options()
include(Dependencies.cmake)
routinely_setup_dependencies()

routinely_local_options()

set(GIT_SHA
    "Unknown"
    CACHE STRING "SHA this build was generated from")
string(
  SUBSTRING "${GIT_SHA}"
            0
            8
            GIT_SHORT_SHA)

target_compile_features(routinely_options INTERFACE cxx_std_${CMAKE_CXX_STANDARD})

add_library(routinely::routinely_options ALIAS routinely_options)
add_library(routinely::routinely_warnings ALIAS routinely_warnings)

#add_library(routinely::routinely_options INTERFACE IMPORTED)
#add_library(routinely::routinely_warnings INTERFACE IMPORTED)

# Adding the src:
add_subdirectory(src)

# Adding the tests:
# include(CTest)

# if(BUILD_TESTING)
#   message(AUTHOR_WARNING "Building Tests. Be sure to check out test/constexpr_tests.cpp for constexpr testing")
#   add_subdirectory(test)
# endif()


# if(routinely_BUILD_FUZZ_TESTS)
#   message(AUTHOR_WARNING "Building Fuzz Tests, using fuzzing sanitizer https://www.llvm.org/docs/LibFuzzer.html")
#   if (NOT routinely_ENABLE_ADDRESS_SANITIZER AND NOT routinely_ENABLE_THREAD_SANITIZER)
#     message(WARNING "You need asan or tsan enabled for meaningful fuzz testing")
#   endif()
#   add_subdirectory(fuzz_test)

# endif()

# If MSVC is being used, and ASAN is enabled, we need to set the debugger environment
# so that it behaves well with MSVC's debugger, and we can run the target from visual studio
if(MSVC)
  get_all_installable_targets(all_targets)
  message("all_targets=${all_targets}")
  set_target_properties(${all_targets} PROPERTIES VS_DEBUGGER_ENVIRONMENT "PATH=$(VC_ExecutablePath_x64);%PATH%")
endif()

# set the startup project for the "play" button in MSVC
set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT intro)

if(CMAKE_SKIP_INSTALL_RULES)
  return()
endif()

# include(cmake/PackageProject.cmake)

# Add other targets that you want installed here, by default we just package the one executable
# we know we want to ship
# routinely_package_project(
#   TARGETS
#   intro
#   routinely_options
#   routinely_warnings
#   # FIXME: this does not work! CK
#   # PRIVATE_DEPENDENCIES_CONFIGURED project_options project_warnings
# )

# Experience shows that explicit package naming can help make it easier to sort
# out potential ABI related issues before they start, while helping you
# track a build to a specific GIT SHA
# set(CPACK_PACKAGE_FILE_NAME
#     "${CMAKE_PROJECT_NAME}-${CMAKE_PROJECT_VERSION}-${GIT_SHORT_SHA}-${CMAKE_SYSTEM_NAME}-${CMAKE_BUILD_TYPE}-${CMAKE_CXX_COMPILER_ID}-${CMAKE_CXX_COMPILER_VERSION}"
# )

# include(CPack)