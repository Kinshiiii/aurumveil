#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>

#include "../include/nlohmann/json.hpp"

using namespace std;
using json = nlohmann::json;

constexpr double EPS = 1e-9;

struct Point {
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

vector<Point> computeConvexHullJarvis(const vector<Point>& points) {
    size_t n = points.size();
    if (n <= 2) {
        return points;
    }

    size_t start = 0;
    for (size_t i = 1; i < n; ++i) {
        if (points[i].y < points[start].y ||
           (fabs(points[i].y - points[start].y) < EPS &&
            points[i].x < points[start].x)) {
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

            double cross = crossPoints(points[current], points[next], points[i]);

            if (cross < -EPS ||
               (fabs(cross) < EPS &&
                squaredDistance(points[current], points[i]) >
                squaredDistance(points[current], points[next]))) {
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

    auto convexHull = computeConvexHullJarvis(minePoints);

    json outputData;
    for (const auto& p : convexHull) {
        outputData["convex_hull"].push_back({
            {"x", p.x},
            {"y", p.y}
        });
     }

    cout << outputData.dump(4) << endl;
}
