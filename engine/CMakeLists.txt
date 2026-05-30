cmake_minimum_required(
    VERSION 3.16
)

project(
    AurumveilAlgorithms
)

set(
    CMAKE_CXX_STANDARD
    20
)

set(
    CMAKE_CXX_STANDARD_REQUIRED
    ON
)

set(
    CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror -pedantic"
)

set(
    CMAKE_RUNTIME_OUTPUT_DIRECTORY
    ${CMAKE_BINARY_DIR}/bin
)

include(FetchContent)

FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)

FetchContent_MakeAvailable(
    json
)

include_directories(
        ${CMAKE_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/algorithms
        ${CMAKE_SOURCE_DIR}/utils
)

function(add_algorithm TARGET)
    add_executable(
        ${TARGET}
        ${ARGN}
    )

    target_link_libraries(
        ${TARGET}
        PRIVATE
        nlohmann_json::nlohmann_json
    )
endfunction()

add_algorithm(
    mcmf
    engines/network_flow/flow_optimizer.cpp
)

add_algorithm(
    graham
    engines/convex_hull/graham_convex_hull.cpp
    engines/convex_hull/geometry_utils.cpp
)

add_algorithm(
    jarvis
    engines/convex_hull/jarvis_convex_hull.cpp
    engines/convex_hull/geometry_utils.cpp
)

add_algorithm(
    monotonic
    engines/convex_hull/monotone_convex_hull.cpp
    engines/convex_hull/geometry_utils.cpp
)

add_algorithm(
    brute
    engines/range_queries/brute_force.cpp
)

add_algorithm(
    segment
    engines/range_queries/segment_tree.cpp
)