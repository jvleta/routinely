#!/bin/bash

clang-tidy routine_builder.cpp routine_builder.hpp -checks=readability-* -- -I /opt/homebrew/Cellar/nlohmann-json/3.11.2/include/
clang++ -isystem /opt/homebrew/Cellar/nlohmann-json/3.11.2/include/ -std=c++20 \
    -Weverything \
    -Werror \
    -Wno-switch-enum \
    -Wno-signed-enum-bitfield \
    -Wno-deprecated-register \
    -Wno-c++98-compat \
    -Wno-c++98-compat-pedantic \
    -Wno-c++98-c++11-compat-pedantic \
    -Wno-nested-anon-types \
    -Wno-gnu-anonymous-struct \
    -Wno-missing-prototypes \
    -Wno-documentation \
    -Wno-documentation-unknown-command \
    -Wno-weak-vtables \
    -Wno-unused-const-variable \
    -Wno-format-nonliteral \
    -Wno-global-constructors \
    -Wno-exit-time-destructors \
    -Wno-error=padded \
    -Wno-sign-conversion \
    -Wno-shorten-64-to-32 \
    routine_builder.cpp 
