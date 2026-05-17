#ifndef CORE_RANGE_UTILS_HPP
#define CORE_RANGE_UTILS_HPP

#include <fstream>
#include <string>
#include <vector>

#include "geometry.hpp"
#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

struct Mine {
    string id;
    int loudness;
    Point point;
};

inline const Mine neutralElement = {
    "",
    numeric_limits<int>::min(),
    {
        "",
        0.0,
        0.0
    }
};

inline vector<Mine> parseMines(const json& inputData) {
    vector<Mine> minePoints;

    for (const auto& item : inputData["points"]) {
        minePoints.push_back({
            item.value("id", ""),
            item.value("loudness", 0),
            {
                "",
                item.value("x", 0.0),
                item.value("y", 0.0)
            }
        });
    }

    return minePoints;
}

inline json buildMineOutput(const Mine& mine) {
    return {
            {"id", mine.id},
            {"x", mine.point.x},
            {"y", mine.point.y},
            {"loudness", mine.loudness}
    };
}

inline Mine loudnessMax(const Mine& a, const Mine& b) {
    if (a.loudness >= b.loudness) {
        return a;
    }

    return b;
}

#endif // CORE_RANGE_UTILS_HPP