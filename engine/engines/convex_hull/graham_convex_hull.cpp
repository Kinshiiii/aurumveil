#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

#include "convex_hull.hpp"
#include "geometry_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

vector<Vertex> computeConvexHullGraham(vector<Vertex> vertices) {
    size_t pivotIndex = 0;

    for (size_t i = 1; i < vertices.size(); ++i) {
        if (
            vertices[i].y < vertices[pivotIndex].y ||
            (
                fabs(
                    vertices[i].y -
                    vertices[pivotIndex].y
                ) < EPSILON &&
                vertices[i].x < vertices[pivotIndex].x
            )
        ) {
            pivotIndex = i;
        }
    }

    swap(
        vertices[0],
        vertices[pivotIndex]
    );

    const Vertex& pivotVertex =
        vertices[0];

    ranges::stable_sort(
        vertices.begin() + 1,
        vertices.end(),
        [&](const Vertex& a, const Vertex& b) {
            return comparePolar(
                pivotVertex,
                a,
                b
            );
        }
    );

    vector<Vertex> filteredVertices;
    filteredVertices.reserve(vertices.size());

    filteredVertices.push_back(
        pivotVertex
    );

    for (size_t i = 1; i < vertices.size(); ++i) {
        while (
            i + 1 < vertices.size() &&
            fabs(
                crossProduct(
                    pivotVertex,
                    vertices[i],
                    vertices[i + 1]
                )
            ) < EPSILON
        ) {
            ++i;
        }

        filteredVertices.push_back(
            vertices[i]
        );
    }

    vector<Vertex> convexHull;
    convexHull.reserve(vertices.size());

    for (const auto& vertex : filteredVertices) {
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
            computeConvexHullGraham(vertices);

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