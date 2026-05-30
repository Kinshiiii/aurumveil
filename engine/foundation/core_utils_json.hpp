/**
 * @file json.hpp
 * @brief JSON parsing and serialization utilities.
 *
 * Provides helper functions for reading input data,
 * extracting domain structures, and generating JSON
 * responses returned by native algorithm executables.
 */

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

/**
 * @brief Reads and parses a JSON input file.
 *
 * Loads a JSON document from disk and converts it
 * into a nlohmann::json object.
 *
 * @param filePath
 * Path to the input file.
 *
 * @return json
 * Parsed JSON document.
 *
 * @throws std::runtime_error
 * Raised when the file cannot be opened.
 */
inline json readInput(const string& filePath) {
    ifstream inputStream(filePath);

    if (!inputStream) {
        throw runtime_error("Failed to open file: " + filePath);
    }

    json inputData;
    inputStream >> inputData;

    return inputData;
}

/**
 * @brief Extracts mine locations as geometry vertices.
 *
 * Converts mining facility entries into vertex
 * structures used by convex hull algorithms.
 *
 * @param inputData
 * Parsed input dataset.
 *
 * @return vector<Vertex>
 * Collection of extracted vertices.
 */
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

/**
 * @brief Extracts mines for range query processing.
 *
 * Converts serialized boundary points into Mine
 * objects used by range query algorithms.
 *
 * @param inputData
 * Parsed input dataset.
 *
 * @return vector<Mine>
 * Collection of extracted mines.
 */
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

/**
 * @brief Extracts a circular range query interval.
 *
 * Reads the requested range boundaries and adjusts
 * wrap-around intervals when necessary.
 *
 * @param inputData
 * Parsed input dataset.
 *
 * @param totalVertices
 * Total number of boundary vertices.
 *
 * @return pair<size_t, size_t>
 * Range query interval.
 */
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

/**
 * @brief Extracts selected optimization algorithms.
 *
 * Reads the configured maximum-flow and minimum-cost
 * algorithms from the input configuration.
 *
 * @param inputData
 * Parsed input dataset.
 *
 * @return pair<string, string>
 * Selected flow and pathfinding algorithms.
 */
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

/**
 * @brief Creates a range query result payload.
 *
 * Builds a JSON response containing information
 * about a detected mine together with algorithm
 * execution timing statistics.
 *
 * @param mine
 * Mine included in the result.
 *
 * @param key
 * JSON field used to store the result entry.
 *
 * @param executionTimeMs
 * Algorithm execution time in milliseconds.
 *
 * @return json
 * Serialized range query result.
 */
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

/**
 * @brief Creates a convex hull result payload.
 *
 * Converts a convex hull into a JSON representation
 * together with geometry algorithm execution timing.
 *
 * @param convexHull
 * Convex hull vertices.
 *
 * @param executionTimeMs
 * Algorithm execution time in milliseconds.
 *
 * @return json
 * Serialized convex hull result.
 */
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

/**
 * @brief Builds miner-to-mine assignment records.
 *
 * Traverses the residual flow network and extracts
 * successful miner assignments represented by flow
 * edges connecting miners to mining facilities.
 *
 * @param inputData
 * Original input dataset.
 *
 * @param graph
 * Residual flow network.
 *
 * @param minersCount
 * Number of miners in the network.
 *
 * @param minesCount
 * Number of mines in the network.
 *
 * @return json
 * Collection of assignment records.
 */
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

/**
 * @brief Creates a flow optimization result payload.
 *
 * Builds a complete JSON response containing
 * optimization statistics, selected algorithms,
 * execution timings, and miner assignment data.
 *
 * @param flowResult
 * Flow optimization statistics.
 *
 * @param assignments
 * Generated miner assignments.
 *
 * @param maxflowAlgorithm
 * Selected maximum-flow algorithm.
 *
 * @param mincostAlgorithm
 * Selected minimum-cost pathfinding algorithm.
 *
 * @param executionTimeMs
 * Total executable runtime in milliseconds.
 *
 * @return json
 * Serialized flow optimization result.
 */
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