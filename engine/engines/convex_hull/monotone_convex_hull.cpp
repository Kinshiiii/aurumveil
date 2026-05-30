#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

#include "convex_hull.hpp"
#include "geometry_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

vector<Vertex> computeConvexHullMonotoneChain(vector<Vertex> vertices) {
    ranges::sort(
        vertices,
        compareVertices
    );

    vector<Vertex> convexHull;
    convexHull.reserve(vertices.size() * 2);

    for (const auto& vertex : vertices) {
        while (
            convexHull.size() >= 2 &&
            crossProduct(
                convexHull[
                    convexHull.size() - 2
                ],
                convexHull.back(),
                vertex
            ) <= EPSILON
        ) {
            convexHull.pop_back();
        }

        convexHull.push_back(vertex);
    }

    const size_t lowerHullSize =
        convexHull.size();

    for (ssize_t i = static_cast<ssize_t>(vertices.size()) - 2; i >= 0; --i) {
        const auto& vertex =
            vertices[i];

        while (
            convexHull.size() > lowerHullSize &&
            crossProduct(
                convexHull[
                    convexHull.size() - 2
                ],
                convexHull.back(),
                vertex
            ) <= EPSILON
        ) {
            convexHull.pop_back();
        }

        convexHull.push_back(vertex);
    }

    convexHull.pop_back();

    return convexHull;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Expected input file: <input.json>" << endl;
        return EXIT_FAILURE;
    }

    try {
        const json inputData = readInput(argv[1]);

        const vector<Vertex> vertices =
            extractPoints(inputData);

        Stopwatch stopwatch;

        const vector<Vertex> convexHull =
            computeConvexHullMonotoneChain(vertices);

        const double executionTimeMs =
            stopwatch.elapsedMilliseconds();

        cout << buildConvexOutput(
            convexHull,
            executionTimeMs
        ).dump(4) << endl;
    }
    catch (const exception& exception) {
        cerr << exception.what() << endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}