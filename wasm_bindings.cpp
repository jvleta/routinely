#include <emscripten/bind.h>

#include "routine_builder.hpp"

using namespace emscripten;

EMSCRIPTEN_BINDINGS(routine_builder) { function("build", builder::build); }
