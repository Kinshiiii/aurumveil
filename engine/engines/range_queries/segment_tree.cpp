#include <iostream>
#include <algorithm>
#include <vector>

#include "range_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

void buildTree(
    vector<Mine>& segmentTree,
    const vector<Mine>& mines,
    size_t nodeIndex,
    size_t nodeLeft,
    size_t nodeRight
) {
    if (nodeLeft == nodeRight) {
        segmentTree[nodeIndex] =
            mines[nodeLeft];

        return;
    }

    const size_t mid =
        (nodeLeft + nodeRight) / 2;

    buildTree(
        segmentTree,
        mines,
        2 * nodeIndex,
        nodeLeft,
        mid
    );

    buildTree(
        segmentTree,
        mines,
        2 * nodeIndex + 1,
        mid + 1,
        nodeRight
    );

    segmentTree[nodeIndex] =
        loudnessMax(
            segmentTree[
                2 * nodeIndex
            ],
            segmentTree[
                2 * nodeIndex + 1
            ]
        );
}

Mine queryRange(
    const vector<Mine>& segmentTree,
    size_t nodeIndex,
    size_t nodeLeft,
    size_t nodeRight,
    size_t queryLeft,
    size_t queryRight
) {
    if (nodeRight < queryLeft || queryRight < nodeLeft) {
        return neutralMine;
    }

    if (queryLeft <= nodeLeft && nodeRight <= queryRight) {
        return segmentTree[nodeIndex];
    }

    const size_t mid = (nodeLeft + nodeRight) / 2;

    const Mine leftResult = queryRange(
        segmentTree,
        2 * nodeIndex,
        nodeLeft,
        mid,
        queryLeft,
        queryRight
    );

    const Mine rightResult = queryRange(
        segmentTree,
        2 * nodeIndex + 1,
        mid + 1,
        nodeRight,
        queryLeft,
        queryRight
    );

    const Mine result = loudnessMax(
        leftResult,
        rightResult
    );

    return result;
}

Mine queryModuloRange(
    const vector<Mine>& segmentTree,
    size_t totalMines,
    size_t from,
    size_t to
) {
    if (to < totalMines) {
        return queryRange(
            segmentTree,
            1,
            0,
            totalMines - 1,
            from,
            to
        );
    }

    const Mine leftRange =
        queryRange(
            segmentTree,
            1,
            0,
            totalMines - 1,
            from,
            totalMines - 1
        );

    const Mine rightRange =
        queryRange(
            segmentTree,
            1,
            0,
            totalMines - 1,
            0,
            to % totalMines
        );

    return loudnessMax(
        leftRange,
        rightRange
    );
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

        vector<Mine> segmentTree(
            minePoints.size() * 4,
            neutralMine
        );

        buildTree(
            segmentTree,
            minePoints,
            1,
            0,
            minePoints.size() - 1
        );

        Stopwatch stopwatch;

        const Mine loudestMine =
            queryModuloRange(
                segmentTree,
                minePoints.size(),
                from,
                to + 1
            );

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