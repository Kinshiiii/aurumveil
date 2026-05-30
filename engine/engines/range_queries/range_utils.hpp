#ifndef MINE_UTILS_HPP
#define MINE_UTILS_HPP

#include <string>
#include <limits>

#include <nlohmann/json.hpp>

#include "../convex_hull/geometry_utils.hpp"

using namespace std;
using json = nlohmann::json;

struct Mine {
    string id;

    int loudness{0};

    Vertex vertex;
};

inline const Mine neutralMine = {
    "",
    numeric_limits<int>::min(),
    {
        "",
        0.0,
        0.0
    }
};

inline Mine loudnessMax(const Mine& a, const Mine& b) {
    if (a.loudness >= b.loudness) {
        return a;
    }

    return b;
}

#endif // MINE_UTILS_HPP