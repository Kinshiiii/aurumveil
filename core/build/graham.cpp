#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

#include "convex_hull.hpp"
#include "geometry.hpp"
#include "json_utils.hpp"

using namespace std;

vector<Point> computeConvexHullGraham(vector<Point> points) {
    const size_t n = points.size();

    size_t pivot_idx = 0;

    for (size_t i = 1; i < n; ++i) {
        if (
            points[i].y < points[pivot_idx].y ||
            (
                abs(points[i].y - points[pivot_idx].y) < EPS &&
                points[i].x < points[pivot_idx].x
            )
        ) {
            pivot_idx = i;
        }
    }

    swap(points[0], points[pivot_idx]);

    const Point& pivot = points[0];

    stable_sort(
        points.begin() + 1,
        points.end(),
        [&](const Point& a, const Point& b) {
            return polarComparator(pivot, a, b);
        }
    );

    vector<Point> filtered;
    filtered.push_back(pivot);

    const size_t pointCount = points.size();

    for (size_t i = 1; i < pointCount; ++i) {
        while (
            i + 1 < pointCount &&
            abs(
                crossPoints(
                    pivot,
                    points[i],
                    points[i + 1]
                )
            ) < EPS
        ) {
            ++i;
        }

        filtered.push_back(points[i]);
    }

    vector<Point> hull;

    for (const auto& p : filtered) {
        while (
            hull.size() >= 2 &&
            crossPoints(
                hull[hull.size() - 2],
                hull[hull.size() - 1],
                p
            ) <= EPS
        ) {
            hull.pop_back();
        }

        hull.push_back(p);
    }

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

        vector<Point> convexHull = computeConvexHullGraham(minePoints);

        cout << buildOutputJson(convexHull).dump(4) << endl;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}