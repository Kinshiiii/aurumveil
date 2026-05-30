#ifndef CORE_UTILS_STOPWATCH_HPP
#define CORE_UTILS_STOPWATCH_HPP

#include <chrono>

using namespace std;
using namespace chrono;

class Stopwatch {
public:
    Stopwatch()
        : startTime(high_resolution_clock::now()) {}

    void restart() {
        startTime = high_resolution_clock::now();
    }

    double elapsedMilliseconds() const {
        const auto currentTime =
            high_resolution_clock::now();

        return duration<double, milli>(
            currentTime - startTime
        ).count();
    }

private:
    high_resolution_clock::time_point startTime;
};

#endif // CORE_UTILS_STOPWATCH_HPP