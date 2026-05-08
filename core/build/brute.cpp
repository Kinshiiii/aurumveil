#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <limits>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

struct Mine {
    string id;
    int loudness;
};

vector<Mine> parsePoints(const json& inputData) {
    vector<Mine> minePoints;

    for (const auto& item : inputData["points"]) {
        minePoints.push_back({
            item["id"].get<string>(),
            item["loudness"].get<int>()
        });
    }

    return minePoints;
}

Mine findLoudest(const vector<Mine>& minePoints, size_t from, size_t to) {
    const size_t total = minePoints.size();
    size_t steps;

    if (from <= to) {
        steps = to - from + 1;
    } else {
        steps = total - from + to + 1;
    }

    Mine loudest = {"", numeric_limits<int>::min()};

    for (size_t i = 0; i < steps; ++i) {
        const size_t current = (from + i) % total;

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

    ifstream file(argv[1]);

    json inputData;
    file >> inputData;

    const vector<Mine> minePoints = parsePoints(inputData);

    const size_t total = minePoints.size();
    const size_t from = (size_t)inputData["range"][0] - 1;
    const size_t to = (size_t)inputData["range"][1];

    if (from >= total || to > total) {
        cerr << "Error: Range out of bounds." << endl;
        return 1;
    }

    const Mine loudest = findLoudest(
        minePoints,
        from,
        to
    );

    json outputData = {
        {"id", loudest.id},
        {"guard_loudness", loudest.loudness}
    };

    cout << outputData.dump(4) << endl;

    return 0;
}
