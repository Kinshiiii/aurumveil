#include <cmath>
#include <iostream>
#include <vector>

#include "convex_hull.hpp"
#include "geometry.hpp"
#include "json_utils.hpp"

using namespace std;

vector<Point> computeConvexHullJarvis(const vector<Point>& points) {
    const size_t n = points.size();

    size_t start = 0;

    for (size_t i = 1; i < n; ++i) {
        if (
            points[i].y < points[start].y ||
            (
                fabs(points[i].y - points[start].y) < EPS &&
                points[i].x < points[start].x
            )
        ) {
            start = i;
        }
    }

    vector<Point> hull;
    size_t current = start;

    do {
        hull.push_back(points[current]);

        size_t next = (current + 1) % n;

        for (size_t i = 0; i < n; ++i) {
            if (i == current) {
                continue;
            }

            double cross = crossPoints(
                points[current],
                points[next],
                points[i]
            );

            if (
                cross < -EPS ||
                (
                    fabs(cross) < EPS &&
                    squaredDistance(
                        points[current],
                        points[i]
                    ) >
                    squaredDistance(
                        points[current],
                        points[next]
                    )
                )
            ) {
                next = i;
            }
        }

        current = next;

    } while (current != start);

    return hull;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: program <input_file.json>" << endl;
        return 1;
    }

    try {
        json inputData = loadJson(argv[1]);

        vector<Point> minePoints = parsePoints(inputData);

        vector<Point> convexHull = computeConvexHullJarvis(minePoints);

        cout << buildOutputJson(convexHull).dump(4) << endl;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}