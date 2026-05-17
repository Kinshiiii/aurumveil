#include <fstream>
#include <iostream>
#include <vector>

#include "json_utils.hpp"
#include "range_utils.hpp"

using namespace std;

Mine findLoudest(const vector<Mine>& minePoints, size_t from, size_t to) {
    const size_t total = minePoints.size();
    const size_t steps = (to + total - from) % total + 1;

    Mine loudest = neutralElement;

    for (size_t i = 0; i < steps; ++i) {
        size_t current = (from + i) % total;

        if (minePoints[current].loudness > loudest.loudness) {
            loudest = minePoints[current];
        }
    }

    return loudest;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: program <input_file.json>" << endl;
        return 1;
    }

    try {
        json inputData = loadJson(argv[1]);

        vector<Mine> minePoints = parseMines(inputData);

        const size_t total = minePoints.size();

        const size_t from = static_cast<size_t>(inputData["range"][0]) - 1;
        const size_t to = static_cast<size_t>(inputData["range"][1]) - 1;

        if (from >= total || to >= total) {
            cerr << "Error: Range out of bounds." << endl;
            return 1;
        }

        Mine loudest = findLoudest(
            minePoints,
            from,
            to
        );

        cout << buildMineOutput(loudest).dump(4) << endl;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}