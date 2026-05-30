/**
 * @file stopwatch.hpp
 * @brief High-resolution execution time measurement utility.
 *
 * Provides a lightweight stopwatch used for measuring
 * algorithm execution times and benchmarking native
 * components of the Aurumveil platform.
 */

#ifndef CORE_UTILS_STOPWATCH_HPP
#define CORE_UTILS_STOPWATCH_HPP

#include <chrono>

using namespace std;
using namespace chrono;

/**
 * @brief High-resolution stopwatch.
 *
 * Measures elapsed execution time using the C++
 * standard high-resolution clock.
 */
class Stopwatch {
public:

    /**
     * @brief Creates and starts the stopwatch.
     *
     * Initializes the starting timestamp to the
     * current system time.
     */
    Stopwatch()
        : startTime(high_resolution_clock::now()) {}

    /**
     * @brief Restarts the stopwatch.
     *
     * Resets the starting timestamp to the current
     * time, discarding any previously measured interval.
     */
    void restart() {
        startTime = high_resolution_clock::now();
    }

    /**
     * @brief Returns elapsed time in milliseconds.
     *
     * Calculates the duration between the current
     * time and the most recent start or restart.
     *
     * @return double
     * Elapsed time in milliseconds.
     */
    double elapsedMilliseconds() const {
        const auto currentTime =
            high_resolution_clock::now();

        return duration<double, milli>(
            currentTime - startTime
        ).count();
    }

private:

    /// Timestamp marking the beginning of the measurement.
    high_resolution_clock::time_point startTime;
};

#endif // CORE_UTILS_STOPWATCH_HPP