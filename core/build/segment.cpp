#include <algorithm>
#include <iostream>
#include <vector>

#include "json_utils.hpp"
#include "range_utils.hpp"

using namespace std;

void buildTree(vector<Mine>& segmentTree, const vector<Mine>& mines, size_t nodeIndex, size_t nodeLeft, size_t nodeRight) {
    if (nodeLeft == nodeRight) {
        segmentTree[nodeIndex] = mines[nodeLeft];
        return;
    }

    const size_t mid = (nodeLeft + nodeRight) / 2;

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

    segmentTree[nodeIndex] = loudnessMax(
        segmentTree[2 * nodeIndex],
        segmentTree[2 * nodeIndex + 1]
    );
}

Mine queryRange(const vector<Mine>& segmentTree, size_t nodeIndex, size_t nodeLeft, size_t nodeRight, size_t queryLeft, size_t queryRight) {
    if (nodeRight < queryLeft || queryRight < nodeLeft) {
        return neutralElement;
    }

    if (queryLeft <= nodeLeft && nodeRight <= queryRight) {
        return segmentTree[nodeIndex];
    }

    const size_t mid = (nodeLeft + nodeRight) / 2;

    Mine leftResult = queryRange(
        segmentTree,
        2 * nodeIndex,
        nodeLeft,
        mid,
        queryLeft,
        queryRight
    );

    Mine rightResult = queryRange(
        segmentTree,
        2 * nodeIndex + 1,
        mid + 1,
        nodeRight,
        queryLeft,
        queryRight
    );

    Mine result = loudnessMax(
        leftResult,
        rightResult
    );

    return result;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: program <input_file.json>" << endl;
        return 1;
    }

    try {
        json inputData = loadJson(argv[1]);

        vector<Mine> mines = parseMines(inputData);

        const size_t nodeRight = mines.size() - 1;

        vector<Mine> segmentTree(
            4 * nodeRight + 1,
            neutralElement
        );

        buildTree(
            segmentTree,
            mines,
            1,
            1,
            nodeRight
        );

        size_t queryLeft = 1;
        size_t queryRight = nodeRight;

        if (inputData.contains("range") && inputData["range"].size() == 2) {
            size_t left = static_cast<size_t>(inputData["range"][0]);
            size_t right = static_cast<size_t>(inputData["range"][1]);

            left = max(left, static_cast<size_t>(1));
            right = min(right, nodeRight);

            if (left <= right) {
                queryLeft = left;
                queryRight = right;
            }
        }

        Mine result = queryRange(
            segmentTree,
            1,
            1,
            nodeRight,
            queryLeft,
            queryRight
        );

        cout << buildMineOutput(result).dump(4) << endl;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}