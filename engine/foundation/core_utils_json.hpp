#ifndef CORE_UTILS_JSON_HPP
#define CORE_UTILS_JSON_HPP

#include <fstream>
#include <string>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>

#include "engines/convex_hull/geometry_utils.hpp"
#include "engines/range_queries/range_utils.hpp"
#include "engines/network_flow/flow_optimizer.hpp"

using namespace std;
using json = nlohmann::json;

inline json readInput(const string& filePath) {
    ifstream inputStream(filePath);

    if (!inputStream) {
        throw runtime_error("Failed to open file: " + filePath);
    }

    json inputData;
    inputStream >> inputData;

    return inputData;
}

inline vector<Vertex> extractPoints(const json& inputData) {
    vector<Vertex> vertices;

    for (const auto& node : inputData["mines"]) {
        vertices.push_back({
            node.value("id", ""),
            node.value("x", 0.0),
            node.value("y", 0.0)
        });
    }

    return vertices;
}

inline vector<Mine> extractMines(const json& inputData) {
    vector<Mine> mines;

    for (const auto& node : inputData["points"]) {
        mines.push_back({
            node.value("id", ""),
            node.value("loudness", 0),
            {
                "",
                node.value("x", 0.0),
                node.value("y", 0.0)
            }
        });
    }

    return mines;
}

inline pair<size_t, size_t> extractRange(const json& inputData, size_t totalVertices) {
    const size_t from =
        static_cast<size_t>(
            inputData["range"][0]
        ) - 1;

    size_t to =
        static_cast<size_t>(
            inputData["range"][1]
        ) - 1;

    if (to < from) {
        to += totalVertices;
    }

    return {
        from,
        to
    };
}

inline pair<string, string> extractAlgorithms(const json& inputData) {
    const string maxflowAlgorithm =
        inputData["config"]
                 ["flow_algorithm"];

    const string mincostAlgorithm =
        inputData["config"]
                 ["cost_algorithm"];

    return {
        maxflowAlgorithm,
        mincostAlgorithm
    };
}

inline json buildMineOutput(const Mine& mine, const string& key, double executionTimeMs) {
    json result;

    result["execution_time_ms"] = executionTimeMs;

    result[key].push_back({
        {"id", mine.id},
        {"x", mine.vertex.x},
        {"y", mine.vertex.y},
        {"loudness", mine.loudness}
    });

    return result;
}

inline json buildConvexOutput(const vector<Vertex>& convexHull, double executionTimeMs) {
    json result;

    result["execution_time_ms"] = executionTimeMs;

    for (const auto& vertex : convexHull) {
        result["convex_hull"].push_back({
            {"id", vertex.id},
            {"x", vertex.x},
            {"y", vertex.y}
        });
    }

    return result;
}

inline json buildAssignments(
    const json& inputData,
    const vector<vector<Edge>>& graph,
    size_t minersCount,
    size_t minesCount
) {
    json result;

    for (size_t i = 0; i < minersCount; ++i) {
        const auto& miner =
            inputData["miners"][i];

        for (const auto& edge : graph[i + 1]) {
            const bool isMineNode =
                edge.destination > minersCount &&
                edge.destination <=
                minersCount + minesCount;

            const bool hasFlow =
                edge.capacity == 0;

            if (!isMineNode || !hasFlow) {
                continue;
            }

            const int mineIndex =
                edge.destination -
                minersCount -
                1;

            const auto& mine =
                inputData["mines"]
                         [mineIndex];

            result.push_back({
                {"miner", miner["id"]},

                {"miner_x", miner["x"]},
                {"miner_y", miner["y"]},

                {"mine", mine["id"]},

                {"mine_x", mine["x"]},
                {"mine_y", mine["y"]}
            });
        }
    }

    return result;
}

inline json buildFlowOutput(
    const FlowStatistics& flowResult,
    const json& assignments,
    const string& maxflowAlgorithm,
    const string& mincostAlgorithm,
    double executionTimeMs
) {
    json result;

    result["pathfinding_time_ms"] =
        flowResult.pathfindingTimeMs;

    result["augmentation_time_ms"] =
        flowResult.augmentationTimeMs;

    result["total_algorithm_time_ms"] =
        flowResult.totalTimeMs;

    result["execution_time_ms"] =
        executionTimeMs;

    result["maxflow_algorithm"] =
        maxflowAlgorithm;

    result["mincost_algorithm"] =
        mincostAlgorithm;

    result["max_flow"] =
        flowResult.maximumFlow;

    result["min_cost"] =
        flowResult.minimumCost;

    result["assignments"] =
        assignments;

    return result;
}

#endif // CORE_UTILS_JSON_HPP