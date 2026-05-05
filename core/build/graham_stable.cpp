#include <iostream>
#include <vector>
#include <algorithm>
#include <tuple>
#include <fstream>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

constexpr double EPS = 1e-9;

struct Point {
    string id;
    double x{0.0};
    double y{0.0};
};

double crossPoints(const Point& O, const Point& A, const Point& B) {
    return (A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x);
}

double squaredDistance(const Point& a, const Point& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return dx * dx + dy * dy;
}

vector<Point> ComputeConvexHullGrahamStable(vector<Point> points) {
    size_t n = points.size();
    if (n <= 2) {
        return points;
    }

    size_t pivot_idx = 0;
    for (size_t i = 1; i < n; ++i) {
        if (points[i].y < points[pivot_idx].y ||
           (abs(points[i].y - points[pivot_idx].y) < EPS &&
            points[i].x < points[pivot_idx].x)) {
            pivot_idx = i;
        }
    }

    swap(points[0], points[pivot_idx]);
    Point pivot = points[0];

    stable_sort(points.begin() + 1, points.end(),
        [&](const Point& a, const Point& b) {
            double c = crossPoints(pivot, a, b);
            if (abs(c) < EPS)
                return squaredDistance(pivot, a) < squaredDistance(pivot, b);
            return c > 0;
        });

    vector<Point> filtered;
    filtered.push_back(pivot);

    size_t point_count = points.size();
    for (size_t i = 1; i < point_count; ++i) {
        while (i + 1 < point_count &&
               abs(crossPoints(pivot, points[i], points[i + 1])) < EPS) {
            ++i;
        }
        filtered.push_back(points[i]);
    }

    vector<Point> hull;
    for (const auto& p : filtered) {
        while (hull.size() >= 2 &&
               crossPoints(hull[hull.size() - 2],
                     hull[hull.size() - 1],
                     p) <= EPS) {
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

    ifstream file(argv[1]);
    if (!file) {
        cerr << "Error: Cannot open file." << endl;
        return 1;
    }

    json inputData;
    file >> inputData;

    vector<Point> minePoints;
    for (const auto& item : inputData["mines"]) {
        minePoints.push_back({item["id"], item["x"], item["y"]});
    }

    auto convexHull = ComputeConvexHullGrahamStable(minePoints);

    json outputData;
    for (const auto& p : convexHull) {
        outputData["convex_hull"].push_back({
            {"id", p.id},
            {"x", p.x},
            {"y", p.y}
        });
    }

    cout << outputData.dump(4) << endl;
}
