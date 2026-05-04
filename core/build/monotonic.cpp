#include <iostream>
#include <vector>
#include <algorithm>
#include <tuple>
#include <fstream>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

struct Point {
    double x{0.0};
    double y{0.0};
};

bool comparePoints(const Point& a, const Point& b) {
    return tie(a.x, a.y) < tie(b.x, b.y);
}

double crossPoints(const Point& O, const Point& A, const Point& B) {
    return (A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x);
}

vector<Point> computeConvexHullMonotoneChain(vector<Point> points) {
    int n = points.size();
    if (n <= 1) {
        return points;
    }

    sort(points.begin(), points.end(), comparePoints);

    vector<Point> hull;

    for (const auto& p : points) {
        while (hull.size() >= 2 &&
               crossPoints(hull[hull.size() - 2], hull.back(), p) <= 0) {
            hull.pop_back();
        }
        hull.push_back(p);
    }

    size_t lowerSize = hull.size();

    for (int i = n - 2; i >= 0; --i) {
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

    ifstream file(argv[1]);
    if (!file) {
        cerr << "Error: Cannot open file." << endl;
        return 1;
    }

    json inputData;
    file >> inputData;

    vector<Point> minePoints;
    for (const auto& item : inputData["mines"]) {
        minePoints.push_back({item["x"], item["y"]});
    }

    auto convexHull = computeConvexHullMonotoneChain(minePoints);

    json outputData;
    for (const auto& p : convexHull) {
        outputData["convex_hull"].push_back({
            {"x", p.x},
            {"y", p.y}
        });
    }

    cout << outputData.dump(4) << endl;
}
