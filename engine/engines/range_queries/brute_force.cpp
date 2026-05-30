/**
 * @file brute_force.cpp
 * @brief Brute-force range query algorithm.
 *
 * Implements a linear scan approach for locating
 * the loudest mine within a specified boundary range.
 */

#include <iostream>
#include <vector>

#include "range_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

/**
 * @brief Finds the loudest mine within a range.
 *
 * Performs a linear scan over the specified interval
 * and returns the mine with the highest loudness.
 *
 * Circular indexing is applied to support ranges
 * that wrap around the convex hull boundary.
 *
 * @param minePoints
 * Ordered boundary mines.
 *
 * @param from
 * Start index of the query range.
 *
 * @param to
 * End index of the query range.
 *
 * @return Mine
 * Loudest mine within the specified interval.
 */
Mine findLoudest(const vector<Mine>& minePoints, size_t from, size_t to) {
    Mine loudestMine = neutralMine;

    for (size_t i = from; i <= to; ++i) {
        if (minePoints[i % minePoints.size()].loudness > loudestMine.loudness) {
            loudestMine =
                minePoints[
                    i % minePoints.size()
                ];
        }
    }

    return loudestMine;
}

/**
 * @brief Application entry point.
 *
 * Loads input data, executes the brute-force
 * range query algorithm, and exports the result
 * as a JSON response.
 *
 * @param argc
 * Number of command-line arguments.
 *
 * @param argv
 * Command-line arguments.
 *
 * @return int
 * EXIT_SUCCESS on success, otherwise EXIT_FAILURE.
 */
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Expected input file: <input.json>" << endl;
        return EXIT_FAILURE;
    }

    try {
        const json inputData = readInput(argv[1]);

        const vector<Mine> minePoints =
            extractMines(inputData);

        const auto [from, to] =
            extractRange(inputData, minePoints.size());

        Stopwatch stopwatch;

        const Mine loudestMine =
            findLoudest(minePoints, from, to + 1);

        const double executionTimeMs =
            stopwatch.elapsedMilliseconds();

        cout << buildMineOutput(
            loudestMine,
            "loudest_mine",
            executionTimeMs
        ).dump(4) << endl;
    }
    catch (const exception& exception) {
        cerr << exception.what() << endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}