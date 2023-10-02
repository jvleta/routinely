#include "routine_builder.hpp"

#include <emscripten/bind.h>

using namespace emscripten;

EMSCRIPTEN_BINDINGS(routine_builder) { function("build", builder::build); }
