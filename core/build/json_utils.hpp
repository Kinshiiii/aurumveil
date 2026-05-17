#ifndef CORE_JSON_UTILS_HPP
#define CORE_JSON_UTILS_HPP

#include <fstream>
#include <string>
#include <vector>

#include "geometry.hpp"
#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

inline json loadJson(const string& path) {
    ifstream inputFile(path);

    if (!inputFile) {
        throw runtime_error("Cannot open file");
    }

    json data;
    inputFile >> data;

    return data;
}

inline vector<Point> parsePoints(const json& inputData) {
    vector<Point> points;

    for (const auto& item : inputData["mines"]) {
        points.push_back({
            item.value("id", ""),
            item["x"].get<double>(),
            item["y"].get<double>()
        });
    }

    return points;
}

inline json buildOutputJson(const vector<Point>& hull) {
    json output;

    for (const auto& point : hull) {
        output["convex_hull"].push_back({
            {"id", point.id},
            {"x", point.x},
            {"y", point.y}
        });
    }

    return output;
}

#endif // CORE_JSON_UTILS_HPP