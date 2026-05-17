#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

#include "convex_hull.hpp"
#include "geometry.hpp"
#include "json_utils.hpp"

using namespace std;

vector<Point> computeConvexHullMonotoneChain(vector<Point> points) {
    const size_t n = points.size();

    sort(points.begin(), points.end(), comparePoints);

    vector<Point> hull;

    for (const auto& p : points) {
        while (hull.size() >= 2 &&
               crossPoints(hull[hull.size() - 2], hull.back(), p) <= 0) {
            hull.pop_back();
        }

        hull.push_back(p);
    }

    const size_t lowerSize = hull.size();

    for (ssize_t i = static_cast<ssize_t>(n) - 2; i >= 0; --i) {
        const auto& p = points[i];

        while (hull.size() > lowerSize &&
               crossPoints(hull[hull.size() - 2], hull.back(), p) <= 0) {
            hull.pop_back();
        }

        hull.push_back(p);
    }

    hull.pop_back();

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

        vector<Point> convexHull = computeConvexHullMonotoneChain(minePoints);

        cout << buildOutputJson(convexHull).dump(4) << endl;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}