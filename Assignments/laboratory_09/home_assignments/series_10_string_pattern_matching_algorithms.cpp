#include <iostream>
#include <vector>

constexpr long long PRIME_MODULO = 1'000'000'007;

using namespace std;
using hash_t = long long;

void print_no_pattern_occurrences_message() {
    cout << "  - No pattern occurrences were found" << endl;
}

unsigned char get_character_code(char symbol) {
    return static_cast<unsigned char>(symbol);
}

vector<size_t> build_prefix_table(const string& search_pattern, size_t pattern_length) {
    vector<size_t> prefix_table(pattern_length, 0);

    size_t matched_prefix_length = 0;

    for (size_t i = 1; i < pattern_length; ++i) {
        while (matched_prefix_length > 0 && search_pattern[matched_prefix_length] != search_pattern[i]) {
            matched_prefix_length = prefix_table[matched_prefix_length - 1];
        }

        if (search_pattern[matched_prefix_length] == search_pattern[i]) {
            ++matched_prefix_length;
        }

        prefix_table[i] = matched_prefix_length;
    }

    return prefix_table;
}

void compute_pattern_matching_knuth_morris_pratt(const string& input_text, const string& search_pattern, size_t text_length, size_t pattern_length) {
    const vector<size_t> prefix_table = build_prefix_table(search_pattern, pattern_length);

    bool is_pattern_found = false;
    size_t matched_characters_count = 0;

    for (size_t i = 0; i < text_length; ++i) {
        while (matched_characters_count > 0 && search_pattern[matched_characters_count] != input_text[i]) {
            matched_characters_count = prefix_table[matched_characters_count - 1];
        }

        if (search_pattern[matched_characters_count] == input_text[i]) {
            ++matched_characters_count;
        }

        if (matched_characters_count == pattern_length) {
            is_pattern_found = true;
            const size_t pattern_index = i - pattern_length + 1;

            cout << "  - Pattern found at index: "
                 << pattern_index + 1
                 << endl;

            matched_characters_count = prefix_table[matched_characters_count - 1];
        }
    }

    if (!is_pattern_found) {
        print_no_pattern_occurrences_message();
    }
}

void compute_pattern_matching_rabin_karp(const string& input_text, const string& search_pattern, size_t text_length, size_t pattern_length) {
    constexpr long long ALPHABET_SIZE = 256;

    hash_t highest_power = 1;
    hash_t pattern_hash = 0;
    hash_t current_text_hash = 0;
    bool is_pattern_found = false;

    for (size_t i = 0; i < pattern_length - 1; ++i) {
        highest_power = (highest_power * ALPHABET_SIZE) % PRIME_MODULO;
    }

    for (size_t i = 0; i < pattern_length; ++i) {
        pattern_hash = ((ALPHABET_SIZE * pattern_hash) + get_character_code(search_pattern[i])) % PRIME_MODULO;
        current_text_hash = ((ALPHABET_SIZE * current_text_hash) + get_character_code(input_text[i])) % PRIME_MODULO;
    }

    for (size_t pattern_shift = 0; pattern_shift <= text_length - pattern_length; ++pattern_shift) {
        if (pattern_hash == current_text_hash) {
            bool is_match_found = true;

            for (size_t i = 0; i < pattern_length; ++i) {
                if (input_text[pattern_shift + i] != search_pattern[i]) {
                    is_match_found = false;
                    break;
                }
            }

            if (is_match_found) {
                is_pattern_found = true;
                cout << "  - Pattern found at shift: "
                     << pattern_shift + 1
                     << endl;
            }
        }

        if (pattern_shift < text_length - pattern_length) {
            const hash_t removed_character_hash =
                (
                    get_character_code(input_text[pattern_shift])
                    * highest_power
                ) % PRIME_MODULO;

            const hash_t normalized_hash =
                (
                    current_text_hash
                    - removed_character_hash
                    + PRIME_MODULO
                ) % PRIME_MODULO;

            current_text_hash =
                (
                    (ALPHABET_SIZE * normalized_hash)
                    + get_character_code(input_text[pattern_shift + pattern_length])
                ) % PRIME_MODULO;
        }
    }

    if (!is_pattern_found) {
        print_no_pattern_occurrences_message();
    }
}

void run_pattern_matching_algorithms(const string& input_text, const string& search_pattern) {
    cout << endl;

    const size_t text_length = input_text.size();
    const size_t pattern_length = search_pattern.size();

    if (text_length < pattern_length) {
        cout << "Pattern Matching Algorithms:" << endl
             << "  - The pattern length is GREATER than the text length" << endl
             << "  - It is impossible to find any occurrence of the pattern in the text" << endl
             << "  - Both Rabin-Karp and KMP algorithms require the pattern to be shorter than or equal to the text" << endl
             << "  - No valid pattern occurrences were found" << endl
             << endl;

        return;
    }

    cout << "Pattern matching (Knuth-Morris-Pratt / KMP algorithm, indexing starts from 1):" << endl;
    compute_pattern_matching_knuth_morris_pratt(
        input_text,
        search_pattern,
        text_length,
        pattern_length
    );
    cout << endl << endl;

    cout << "Pattern matching (Rabin-Karp algorithm with hashing, indexing starts from 1):" << endl;
    compute_pattern_matching_rabin_karp(
        input_text,
        search_pattern,
        text_length,
        pattern_length
    );
    cout << endl;
}

void initialize_pattern_matching_workflow() {
    string input_text;
    string search_pattern;

    cout << "Enter the input text:" << endl;
    getline(cin, input_text);

    if (input_text.empty()) {
        cout << "Pattern Matching Algorithms:" << endl
             << "  - The input text is EMPTY" << endl
             << "  - Pattern matching cannot be performed on an empty text" << endl
             << endl;

        return;
    }

    cout << endl;

    cout << "Enter the search pattern:" << endl;
    getline(cin, search_pattern);

    if (search_pattern.empty()) {
        cout << "Pattern Matching Algorithms:" << endl
             << "  - The search pattern is EMPTY" << endl
             << "  - Pattern matching requires a non-empty pattern" << endl
             << endl;

        return;
    }

    run_pattern_matching_algorithms(
        input_text,
        search_pattern
    );
}

int main() {
    initialize_pattern_matching_workflow();
    return 0;
}
