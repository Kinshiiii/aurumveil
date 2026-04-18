#include <iostream>
#include <vector>
#include <algorithm>
#include <utility>
#include <chrono>
#include <cmath>

constexpr double EPS = 1e-12;

using namespace std;
using namespace chrono;

struct Point {
    double x{};
    double y{};
};

ostream& operator<<(ostream& os, const Point& p) {
    return os << "(" << p.x << ", " << p.y << ")";
}

ostream& operator<<(ostream& os, const vector<Point>& points) {
    os << "  - Hull (" << points.size() << " points, CCW): [";

    for (size_t i = 0; i < points.size(); ++i) {
        os << points[i];
        if (i + 1 < points.size()) {
            os << ", ";
        }
    }

    os << "]";
    return os;
}

void read_points(size_t& point_count, vector<Point>& input_points) {
    cout << "Enter points (x y):" << endl;

    for (size_t i = 0; i < point_count; ++i) {
        cout << "  Point " << (i + 1) << ": ";
        cin >> input_points[i].x >> input_points[i].y;
    }

    sort(input_points.begin(), input_points.end(),
        [](const Point& a, const Point& b)
        {
            if (abs(a.x - b.x) > EPS) {
                return a.x < b.x;
            }

            return a.y < b.y;
        });

    input_points.erase(
        unique(input_points.begin(), input_points.end(),
            [](const Point& a, const Point& b)
            {
                return abs(a.x - b.x) < EPS &&
                       abs(a.y - b.y) < EPS;
            }),
        input_points.end()
    );

    point_count = input_points.size();
    cout << endl;
}

double squared_distance(const Point& a, const Point& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return dx * dx + dy * dy;
}

double orientation(const Point& p, const Point& q, const Point& r) {
    return (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x);
}

vector<Point> compute_convex_hull_graham_stable(size_t point_count, const vector<Point>& input_points) {
    vector<Point> points = input_points;

    auto start = steady_clock::now();

    size_t start_index = 0;

    for (size_t i = 1; i < point_count; ++i) {
        if (points[i].y < points[start_index].y ||
            (abs(points[i].y - points[start_index].y) < EPS &&
             points[i].x < points[start_index].x))
        {
            start_index = i;
        }
    }

    swap(points[0], points[start_index]);
    const Point& pivot = points[0];

    stable_sort(points.begin() + 1, points.end(),
        [&](const Point& a, const Point& b)
        {
            double orient = orientation(pivot, a, b);

            if (abs(orient) < EPS) {
                return squared_distance(pivot, a) < squared_distance(pivot, b);
            }

            return orient > 0;
        });

    vector<Point> filtered;
    filtered.push_back(points[0]);

    for (size_t i = 1; i < point_count; ++i) {
        while (i + 1 < point_count &&
               abs(orientation(pivot, points[i], points[i + 1])) < EPS)
        {
            ++i;
        }
        filtered.push_back(points[i]);
    }

    points = filtered;
    point_count = points.size();

    if (point_count < 3) {
        cout << "  - Graham (stable sort) time: "
             << duration_cast<nanoseconds>(steady_clock::now() - start).count()
             << " ns"
             << endl;

        return points;
    }

    vector<Point> convex_hull;
    convex_hull.reserve(point_count);

    convex_hull.push_back(points[0]);
    convex_hull.push_back(points[1]);
    convex_hull.push_back(points[2]);

    for (size_t i = 3; i < point_count; ++i) {
        const Point& p = points[i];

        while (convex_hull.size() >= 2 &&
               orientation(convex_hull[convex_hull.size() - 2],
                           convex_hull.back(),
                           p) <= 0)
        {
            convex_hull.pop_back();
        }

        convex_hull.push_back(p);
    }

    cout << "  - Graham (stable sort) time: "
         << duration_cast<nanoseconds>(steady_clock::now() - start).count()
         << " ns"
         << endl;

    return convex_hull;
}

vector<Point> compute_convex_hull_graham_polar(size_t point_count, const vector<Point>& input_points) {
    vector<Point> points = input_points;

    auto start = steady_clock::now();

    size_t start_index = 0;

    for (size_t i = 1; i < point_count; ++i) {
        if (points[i].y < points[start_index].y ||
            (abs(points[i].y - points[start_index].y) < EPS &&
             points[i].x < points[start_index].x))
        {
            start_index = i;
        }
    }

    swap(points[0], points[start_index]);
    const Point& pivot = points[0];

    sort(points.begin() + 1, points.end(),
        [&](const Point& a, const Point& b)
        {
            double orient = orientation(pivot, a, b);

            if (abs(orient) < EPS) {
                return squared_distance(pivot, a) < squared_distance(pivot, b);
            }

            return orient > 0;
        });

    vector<Point> filtered;
    filtered.push_back(points[0]);

    for (size_t i = 1; i < point_count; ++i) {
        while (i + 1 < point_count &&
               abs(orientation(pivot, points[i], points[i + 1])) < EPS)
        {
            ++i;
        }
        filtered.push_back(points[i]);
    }

    points = filtered;
    point_count = points.size();

    if (point_count < 3) {
        cout << "  - Graham (polar sort) time: "
             << duration_cast<nanoseconds>(steady_clock::now() - start).count()
             << " ns"
             << endl;

        return points;
    }

    vector<Point> convex_hull;
    convex_hull.reserve(point_count);

    convex_hull.push_back(points[0]);
    convex_hull.push_back(points[1]);
    convex_hull.push_back(points[2]);

    for (size_t i = 3; i < point_count; ++i) {
        const Point& p = points[i];

        while (convex_hull.size() >= 2 &&
               orientation(convex_hull[convex_hull.size() - 2],
                           convex_hull.back(),
                           p) <= 0)
        {
            convex_hull.pop_back();
        }

        convex_hull.push_back(p);
    }

    cout << "  - Graham (polar sort) time: "
         << duration_cast<nanoseconds>(steady_clock::now() - start).count()
         << " ns"
         << endl;

    return convex_hull;
}

vector<Point> compute_convex_hull_jarvis(size_t point_count, const vector<Point>& input_points) {
    auto start = steady_clock::now();

    size_t start_index = 0;
    for (size_t i = 1; i < point_count; ++i) {
        if (input_points[i].y < input_points[start_index].y ||
            (abs(input_points[i].y - input_points[start_index].y) < EPS &&
             input_points[i].x < input_points[start_index].x))
        {
            start_index = i;
        }
    }

    vector<Point> convex_hull;
    convex_hull.reserve(point_count);

    size_t current_index = start_index;

    do {
        const Point& p = input_points[current_index];
        convex_hull.push_back(p);

        size_t next_index = (current_index == 0 ? 1 : 0);

        for (size_t j = 0; j < point_count; ++j) {
            if (j == current_index) {
                continue;
            }

            const Point& candidate = input_points[j];
            const Point& best = input_points[next_index];

            double orient = orientation(p, best, candidate);

            if (orient < 0 ||
                (abs(orient) < EPS &&
                 squared_distance(p, candidate) > squared_distance(p, best)))
            {
                next_index = j;
            }
        }

        current_index = next_index;

    } while (current_index != start_index);

    cout << "  - Jarvis march time: "
         << duration_cast<nanoseconds>(steady_clock::now() - start).count()
         << " ns"
         << endl;

    return convex_hull;
}

vector<Point> compute_convex_hull_monotonic_chain(size_t point_count, const vector<Point>& input_points) {
    auto start = steady_clock::now();

    vector<Point> convex_hull;
    convex_hull.reserve(point_count * 2);

    for (size_t i = 0; i < point_count; ++i) {
        const Point& p = input_points[i];

        while (convex_hull.size() >= 2 &&
               orientation(convex_hull[convex_hull.size() - 2],
                           convex_hull.back(),
                           p) <= 0)
        {
            convex_hull.pop_back();
        }

        convex_hull.push_back(p);
    }

    size_t lower_size = convex_hull.size();

    for (ssize_t i = (ssize_t)point_count - 2; i >= 0; --i) {
        const Point& p = input_points[i];

        while (convex_hull.size() > lower_size &&
               orientation(convex_hull[convex_hull.size() - 2],
                           convex_hull.back(),
                           p) <= 0)
        {
            convex_hull.pop_back();
        }

        convex_hull.push_back(p);
    }

    convex_hull.pop_back();

    cout << "  - Monotonic chain time: "
         << duration_cast<nanoseconds>(steady_clock::now() - start).count()
         << " ns"
         << endl;

    return convex_hull;
}

void run_convex_hull_algorithms(size_t point_count, const vector<Point>& input_points) {
    cout << endl;

    if (point_count < 3) {
        cout << "Convex hull:" << endl
             << "  - Not enough UNIQUE points to compute convex hull (n < 3)" << endl
             << input_points << endl
             << "  - Convex hull is the same as the set of unique points" << endl;
        return;
    }

    cout << "Convex hull (Graham scan - stable sort): " << endl
         << compute_convex_hull_graham_stable(point_count, input_points)
         << endl << endl;

    cout << "Convex hull (Graham scan - polar sort): " << endl
         << compute_convex_hull_graham_polar(point_count, input_points)
         << endl << endl;

    cout << "Convex hull (Jarvis march): " << endl
         << compute_convex_hull_jarvis(point_count, input_points)
         << endl << endl;

    cout << "Convex hull (Monotonic chain / Andrew's algorithm): " << endl
         << compute_convex_hull_monotonic_chain(point_count, input_points)
         << endl;
}

void initialize_convex_hull_workflow() {
    size_t point_count;

    cout << "Enter number of points (n): ";
    cin >> point_count;

    vector<Point> input_points(point_count);

    read_points(point_count, input_points);

    run_convex_hull_algorithms(
        point_count,
        input_points
    );
}

int main() {
    initialize_convex_hull_workflow();
    return 0;
}
