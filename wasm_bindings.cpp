#include <emscripten/bind.h>

#include "routinely.hpp"

using namespace emscripten;

EMSCRIPTEN_BINDINGS(routine_builder) { function("build", builder::build); }
