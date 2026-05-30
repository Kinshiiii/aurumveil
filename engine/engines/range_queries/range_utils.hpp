/**
 * @file mine_utils.hpp
 * @brief Mine data structures and helper utilities.
 *
 * Defines mining facility representations and helper
 * operations used by range query algorithms.
 */

#ifndef MINE_UTILS_HPP
#define MINE_UTILS_HPP

#include <string>
#include <limits>

#include <nlohmann/json.hpp>

#include "../convex_hull/geometry_utils.hpp"

using namespace std;
using json = nlohmann::json;

/**
 * @file mine_utils.hpp
 * @brief Mine data structures and helper utilities.
 *
 * Defines mining facility representations and helper
 * operations used by range query algorithms.
 */
struct Mine {
    string id;

    int loudness{0};

    Vertex vertex;
};

/**
 * @brief Neutral mine value.
 *
 * Sentinel object used as an identity element
 * during maximum loudness queries.
 */
inline const Mine neutralMine = {
    "",
    numeric_limits<int>::min(),
    {
        "",
        0.0,
        0.0
    }
};

/**
 * @brief Returns the louder mine.
 *
 * Compares two mines and returns the one with
 * the greater loudness value.
 *
 * @param a
 * First mine.
 *
 * @param b
 * Second mine.
 *
 * @return Mine
 * Mine with the highest loudness.
 */
inline Mine loudnessMax(const Mine& a, const Mine& b) {
    if (a.loudness >= b.loudness) {
        return a;
    }

    return b;
}

#endif // MINE_UTILS_HPP