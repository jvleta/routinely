include(cmake/SystemLink.cmake)
include(CMakeDependentOption)
include(CheckCXXCompilerFlag)


macro(routinely_supports_sanitizers)
  if((CMAKE_CXX_COMPILER_ID MATCHES ".*Clang.*" OR CMAKE_CXX_COMPILER_ID MATCHES ".*GNU.*") AND NOT WIN32)
    set(SUPPORTS_UBSAN ON)
  else()
    set(SUPPORTS_UBSAN OFF)
  endif()

  if((CMAKE_CXX_COMPILER_ID MATCHES ".*Clang.*" OR CMAKE_CXX_COMPILER_ID MATCHES ".*GNU.*") AND WIN32)
    set(SUPPORTS_ASAN OFF)
  else()
    set(SUPPORTS_ASAN ON)
  endif()
endmacro()

macro(routinely_setup_options)
  option(routinely_ENABLE_HARDENING "Enable hardening" ON)
  option(routinely_ENABLE_COVERAGE "Enable coverage reporting" OFF)
  cmake_dependent_option(
    routinely_ENABLE_GLOBAL_HARDENING
    "Attempt to push hardening options to built dependencies"
    ON
    routinely_ENABLE_HARDENING
    OFF)

  routinely_supports_sanitizers()

  if(NOT PROJECT_IS_TOP_LEVEL OR routinely_PACKAGING_MAINTAINER_MODE)
    option(routinely_ENABLE_IPO "Enable IPO/LTO" OFF)
    option(routinely_WARNINGS_AS_ERRORS "Treat Warnings As Errors" OFF)
    option(routinely_ENABLE_USER_LINKER "Enable user-selected linker" OFF)
    option(routinely_ENABLE_SANITIZER_ADDRESS "Enable address sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_LEAK "Enable leak sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_UNDEFINED "Enable undefined sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_THREAD "Enable thread sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_MEMORY "Enable memory sanitizer" OFF)
    option(routinely_ENABLE_UNITY_BUILD "Enable unity builds" OFF)
    option(routinely_ENABLE_CLANG_TIDY "Enable clang-tidy" OFF)
    option(routinely_ENABLE_CPPCHECK "Enable cpp-check analysis" OFF)
    option(routinely_ENABLE_PCH "Enable precompiled headers" OFF)
    option(routinely_ENABLE_CACHE "Enable ccache" OFF)
  else()
    option(routinely_ENABLE_IPO "Enable IPO/LTO" ON)
    option(routinely_WARNINGS_AS_ERRORS "Treat Warnings As Errors" ON)
    option(routinely_ENABLE_USER_LINKER "Enable user-selected linker" OFF)
    option(routinely_ENABLE_SANITIZER_ADDRESS "Enable address sanitizer" ${SUPPORTS_ASAN})
    option(routinely_ENABLE_SANITIZER_LEAK "Enable leak sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_UNDEFINED "Enable undefined sanitizer" ${SUPPORTS_UBSAN})
    option(routinely_ENABLE_SANITIZER_THREAD "Enable thread sanitizer" OFF)
    option(routinely_ENABLE_SANITIZER_MEMORY "Enable memory sanitizer" OFF)
    option(routinely_ENABLE_UNITY_BUILD "Enable unity builds" OFF)
    option(routinely_ENABLE_CLANG_TIDY "Enable clang-tidy" ON)
    option(routinely_ENABLE_CPPCHECK "Enable cpp-check analysis" ON)
    option(routinely_ENABLE_PCH "Enable precompiled headers" OFF)
    option(routinely_ENABLE_CACHE "Enable ccache" ON)
  endif()

  if(NOT PROJECT_IS_TOP_LEVEL)
    mark_as_advanced(
      routinely_ENABLE_IPO
      routinely_WARNINGS_AS_ERRORS
      routinely_ENABLE_USER_LINKER
      routinely_ENABLE_SANITIZER_ADDRESS
      routinely_ENABLE_SANITIZER_LEAK
      routinely_ENABLE_SANITIZER_UNDEFINED
      routinely_ENABLE_SANITIZER_THREAD
      routinely_ENABLE_SANITIZER_MEMORY
      routinely_ENABLE_UNITY_BUILD
      routinely_ENABLE_CLANG_TIDY
      routinely_ENABLE_CPPCHECK
      routinely_ENABLE_COVERAGE
      routinely_ENABLE_PCH
      routinely_ENABLE_CACHE)
  endif()

endmacro()

macro(routinely_global_options)
  if(routinely_ENABLE_IPO)
    include(cmake/InterproceduralOptimization.cmake)
    routinely_enable_ipo()
  endif()

  routinely_supports_sanitizers()

  if(routinely_ENABLE_HARDENING AND routinely_ENABLE_GLOBAL_HARDENING)
    include(cmake/Hardening.cmake)
    if(NOT SUPPORTS_UBSAN 
       OR routinely_ENABLE_SANITIZER_UNDEFINED
       OR routinely_ENABLE_SANITIZER_ADDRESS
       OR routinely_ENABLE_SANITIZER_THREAD
       OR routinely_ENABLE_SANITIZER_LEAK)
      set(ENABLE_UBSAN_MINIMAL_RUNTIME FALSE)
    else()
      set(ENABLE_UBSAN_MINIMAL_RUNTIME TRUE)
    endif()
    message("${routinely_ENABLE_HARDENING} ${ENABLE_UBSAN_MINIMAL_RUNTIME} ${routinely_ENABLE_SANITIZER_UNDEFINED}")
    routinely_enable_hardening(routinely_options ON ${ENABLE_UBSAN_MINIMAL_RUNTIME})
  endif()
endmacro()

macro(routinely_local_options)
  if(PROJECT_IS_TOP_LEVEL)
    include(cmake/StandardProjectSettings.cmake)
  endif()

  add_library(routinely_warnings INTERFACE)
  add_library(routinely_options INTERFACE)

  # include(cmake/CompilerWarnings.cmake)
  # routinely_set_project_warnings(
  #   routinely_warnings
  #   ${routinely_WARNINGS_AS_ERRORS}
  #   ""
  #   ""
  #   ""
  #   "")

  if(routinely_ENABLE_USER_LINKER)
    include(cmake/Linker.cmake)
    configure_linker(routinely_options)
  endif()

  include(cmake/Sanitizers.cmake)
  routinely_enable_sanitizers(
    routinely_options
    ${routinely_ENABLE_SANITIZER_ADDRESS}
    ${routinely_ENABLE_SANITIZER_LEAK}
    ${routinely_ENABLE_SANITIZER_UNDEFINED}
    ${routinely_ENABLE_SANITIZER_THREAD}
    ${routinely_ENABLE_SANITIZER_MEMORY})

  set_target_properties(routinely_options PROPERTIES UNITY_BUILD ${routinely_ENABLE_UNITY_BUILD})

  if(routinely_ENABLE_PCH)
    target_precompile_headers(
      routinely_options
      INTERFACE
      <vector>
      <string>
      <utility>)
  endif()

  if(routinely_ENABLE_CACHE)
    include(cmake/Cache.cmake)
    routinely_enable_cache()
  endif()

  # include(cmake/StaticAnalyzers.cmake)
  # if(routinely_ENABLE_CLANG_TIDY)
  #   routinely_enable_clang_tidy(routinely_options ${routinely_WARNINGS_AS_ERRORS})
  # endif()

  # if(routinely_ENABLE_CPPCHECK)
  #   routinely_enable_cppcheck(${routinely_WARNINGS_AS_ERRORS} "" # override cppcheck options
  #   )
  # endif()

  if(routinely_ENABLE_COVERAGE)
    include(cmake/Tests.cmake)
    routinely_enable_coverage(routinely_options)
  endif()

  if(routinely_ENABLE_HARDENING AND NOT routinely_ENABLE_GLOBAL_HARDENING)
    include(cmake/Hardening.cmake)
    if(NOT SUPPORTS_UBSAN 
       OR routinely_ENABLE_SANITIZER_UNDEFINED
       OR routinely_ENABLE_SANITIZER_ADDRESS
       OR routinely_ENABLE_SANITIZER_THREAD
       OR routinely_ENABLE_SANITIZER_LEAK)
      set(ENABLE_UBSAN_MINIMAL_RUNTIME FALSE)
    else()
      set(ENABLE_UBSAN_MINIMAL_RUNTIME TRUE)
    endif()
    routinely_enable_hardening(routinely_options OFF ${ENABLE_UBSAN_MINIMAL_RUNTIME})
  endif()

endmacro()