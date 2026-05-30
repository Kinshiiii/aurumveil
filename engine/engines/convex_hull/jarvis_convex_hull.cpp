/**
 * @file jarvis_convex_hull.cpp
 * @brief Jarvis March convex hull algorithm.
 *
 * Implements the Jarvis March (Gift Wrapping)
 * algorithm for constructing the convex hull
 * of a set of two-dimensional vertices.
 */

#include <iostream>
#include <vector>
#include <cmath>

#include "convex_hull.hpp"
#include "geometry_utils.hpp"

#include "foundation/core_utils_json.hpp"
#include "foundation/core_utils_stopwatch.hpp"

using namespace std;

/**
 * @brief Computes a convex hull using Jarvis March.
 *
 * Starts from the lowest vertex and repeatedly
 * selects the next boundary vertex by searching
 * for the most counterclockwise point relative
 * to the current hull edge.
 *
 * Complexity: O(nh)
 * where n is the number of vertices and h is
 * the number of hull vertices.
 *
 * @param vertices
 * Input vertex set.
 *
 * @return vector<Vertex>
 * Convex hull vertices in counterclockwise order.
 */
vector<Vertex> computeConvexHullJarvis(const vector<Vertex>& vertices) {
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

    vector<Vertex> convexHull;
    convexHull.reserve(vertices.size());

    size_t currentIndex = pivotIndex;

    do {
        convexHull.push_back(vertices[currentIndex]);

        size_t nextIndex =
            (currentIndex + 1) % vertices.size();

        for (size_t i = 0; i < vertices.size(); ++i) {
            if (i == currentIndex) {
                continue;
            }

            const double crossValue =
                crossProduct(
                    vertices[currentIndex],
                    vertices[nextIndex],
                    vertices[i]
                );

            if (
                crossValue < -EPSILON ||
                (
                    fabs(crossValue) < EPSILON &&
                    distanceSquared(
                        vertices[currentIndex],
                        vertices[i]
                    ) >
                    distanceSquared(
                        vertices[currentIndex],
                        vertices[nextIndex]
                    )
                )
            ) {
                nextIndex = i;
            }
        }

        currentIndex = nextIndex;

    } while (currentIndex != pivotIndex);

    return convexHull;
}

/**
 * @brief Application entry point.
 *
 * Loads input vertices, executes the Jarvis
 * convex hull algorithm, and exports the resulting
 * boundary as a JSON response.
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

        const vector<Vertex> vertices =
            extractPoints(inputData);

        Stopwatch stopwatch;

        const vector<Vertex> convexHull =
            computeConvexHullJarvis(vertices);

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