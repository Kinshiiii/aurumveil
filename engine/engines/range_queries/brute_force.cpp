#include <iostream>
#include <vector>

#include "range_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

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