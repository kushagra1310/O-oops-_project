#include <bits/stdc++.h>
#include <fstream>
using namespace std;

template<typename T>
bool read2DVector(FILE* fp, std::vector<std::vector<T>>& mat) {
    if (!fp) {
        throw std::runtime_error("Null FILE* passed to read2DVector");
    }

    mat.clear();

    std::uint64_t rows;
    size_t n = std::fread(&rows, sizeof(rows), 1, fp);

    if (n != 1) {
        if (std::feof(fp)) {
            // No more matrices to read
            return false;
        } else {
            throw std::runtime_error("Failed to read row count");
        }
    }

    mat.resize(rows);

    for (std::uint64_t i = 0; i < rows; ++i) {
        std::uint64_t cols;
        if (std::fread(&cols, sizeof(cols), 1, fp) != 1) {
            throw std::runtime_error("Failed to read column count");
        }

        mat[i].resize(cols);

        if (cols > 0) {
            if (std::fread(mat[i].data(), sizeof(T), cols, fp) != cols) {
                throw std::runtime_error("Failed to read row data");
            }
        }
    }

    return true;
}

double eps = 1e-1;
double delta = 1e-1;


double solve_dnf(const vector<vector<pair<int, int>>>& dnf, int num_vars_hint) {
    if (eps <= 0.0 || delta <= 0.0 || delta >= 1.0) {
        throw std::runtime_error("eps must be > 0 and delta in (0,1)");
    }

    // Determine the actual number of variables to size assignments safely.
    int actual_n = num_vars_hint;
    for (const auto& clause : dnf) {
        for (const auto& lit : clause) {
            actual_n = max(actual_n, lit.first);
        }
    }

    // 1. Calculate number of samples
    int t = static_cast<int>(dnf.size());
    int m = static_cast<int>(std::ceil((3.0 * t / (eps * eps)) * std::log(2.0 / delta)));

    cout << m << "\n";
    if (dnf.empty() || actual_n <= 0 || m <= 0) {
        return 0.0;
    }

    struct ClauseMeta {
        std::vector<int> vars;      // distinct vars
        std::vector<int> signs;     // aligned signs
        std::vector<int> free_vars; // variables not in clause
        bool contradictory = false;
    };

    std::vector<ClauseMeta> meta(dnf.size());
    std::vector<int> free_counts(dnf.size(), 0);
    int max_free = 0;

    for (size_t idx = 0; idx < dnf.size(); ++idx) {
        ClauseMeta cm;
        std::unordered_map<int, int> seen;
        for (const auto& lit : dnf[idx]) {
            int var_idx = lit.first;
            int sign = lit.second;
            if (var_idx <= 0) continue;
            auto it = seen.find(var_idx);
            if (it != seen.end() && it->second != sign) {
                cm.contradictory = true;
                break;
            }
            seen[var_idx] = sign;
        }

        if (!cm.contradictory) {
            std::vector<std::pair<int, int>> vs(seen.begin(), seen.end());
            std::sort(vs.begin(), vs.end(), [](auto a, auto b) { return a.first < b.first; });
            cm.vars.reserve(vs.size());
            cm.signs.reserve(vs.size());
            for (const auto& kv : vs) {
                cm.vars.push_back(kv.first);
                cm.signs.push_back(kv.second);
            }
        }

        if (cm.contradictory || static_cast<int>(cm.vars.size()) > actual_n) {
            meta[idx] = std::move(cm);
            continue;
        }

        std::vector<char> in_clause(actual_n + 1, 0);
        for (int v : cm.vars) {
            if (v >= 1 && v <= actual_n) in_clause[v] = 1;
        }
        for (int v = 1; v <= actual_n; ++v) {
            if (!in_clause[v]) cm.free_vars.push_back(v);
        }

        free_counts[idx] = static_cast<int>(cm.free_vars.size());
        max_free = std::max(max_free, free_counts[idx]);
        meta[idx] = std::move(cm);
    }

    // Scale weights for discrete_distribution to avoid overflow/underflow.
    std::vector<double> weights_scaled(dnf.size(), 0.0);
    long double total_scaled = 0.0L;
    for (size_t i = 0; i < dnf.size(); ++i) {
        if (meta[i].contradictory) {
            weights_scaled[i] = 0.0;
            continue;
        }
        int shift = free_counts[i] - max_free; // <= 0
        long double scaled = std::ldexp(1.0L, shift); // 2^(free_i - max_free)
        weights_scaled[i] = static_cast<double>(scaled);
        total_scaled += scaled;
    }

    long double scale_factor = std::ldexp(1.0L, max_free); // 2^max_free
    long double total_weight = scale_factor * total_scaled;

    if (total_scaled == 0.0L || !std::isfinite(total_weight)) {
        return 0.0;
    }

    std::mt19937 rng(std::random_device{}());
    std::discrete_distribution<int> clause_dist(weights_scaled.begin(), weights_scaled.end());
    std::uniform_int_distribution<int> bit_dist(0, 1);

    // Optimized satisfaction check
    auto clause_satisfied = [&](const vector<pair<int, int>>& clause,
                                const vector<int>& assignment) -> bool {
        for (const auto& lit : clause) {
            int var_idx = lit.first;
            int is_negated = lit.second;
            if (var_idx <= 0 || var_idx >= static_cast<int>(assignment.size())) {
                return false;
            }
            bool value = assignment[var_idx];
            if (is_negated) value = !value;
            if (!value) return false;
        }
        return true;
    };

    double weighted_sum = 0.0;

    for (int k = 0; k < m; ++k) {
        // 2. Pick a clause C_i with probability w_i / W
        int i = clause_dist(rng);
        if (meta[i].contradictory || weights_scaled[i] == 0.0) {
            continue;
        }
        const auto& chosen_clause = meta[i];

        // 3. Generate random assignment 'a' such that a satisfies C_i
        // Initialize with random bits (O(n))
        vector<int> assignment(actual_n + 1);
        for (int v : chosen_clause.free_vars) {
            assignment[v] = bit_dist(rng);
        }
        for (size_t j = 0; j < chosen_clause.vars.size(); ++j) {
            int var_idx = chosen_clause.vars[j];
            int sign = chosen_clause.signs[j];
            if (var_idx > 0 && var_idx < static_cast<int>(assignment.size())) {
                assignment[var_idx] = sign ? 0 : 1;
            }
        }

        // 4. KLM Optimization (Inverse Coverage)
        // Instead of checking order (0 to i), we count TOTAL satisfying clauses.
        // This is the "Coverage Estimator": Y = TotalWeight / |Cov(a)|
        
        int coverage_count = 0;
        
        // To strictly approach O(n) per sample in dense cases, we can't avoid checking 
        // the list without preprocessing, but this is the KLM estimator logic.
        for (size_t c = 0; c < dnf.size(); ++c) {
            if (!meta[c].contradictory && clause_satisfied(dnf[c], assignment)) {
                coverage_count++;
            }
        }

        // Add contribution: 1 / |{j : a satisfies C_j}|
        if (coverage_count > 0) {
            weighted_sum += (1.0 / static_cast<double>(coverage_count));
        }
    }

    // Result = (Average of contributions) * TotalWeight
    // Each contribution is (1/coverage), so we average them and multiply by W.
    double result = (weighted_sum / static_cast<double>(m)) * total_weight;
    return result;
}



int main() {

    
    
    FILE* fp = std::fopen("Data/samples20_literals25_clauses1000_var_width1.bin_sol.txt", "rb");
    if (!fp) {
        std::perror("fopen for read");
        return 1;
    }

    string ofile = "Data/samples20_literals60_clauses20_var_width1_klm" + to_string(eps) + to_string(delta) + ".txt";

    std::ofstream out_txt(ofile);
    if (!out_txt) {
        std::perror("opening output txt");
        std::fclose(fp);
        return 1;
    }

    std::vector<std::vector<pair<int, int>>> mat;
    int idx = 0;
    const int num_vars = 25;
    const int samples = 10000; // number of Monte Carlo trials per formula

    try {
        while (true) {
            bool ok = read2DVector(fp, mat);
            if (!ok) {
                break; // no more matrices
            }

            double count = solve_dnf(mat, num_vars);
            std::cout << "Matrix #" << idx++
                      << " satisfying assignments (approx): " << count << '\n';
            out_txt << count << '\n';
        }
    } catch (const std::exception& e) {
        std::cerr << "Error reading: " << e.what() << '\n';
        std::fclose(fp);
        out_txt.close();
        return 1;
    }

    std::fclose(fp);
    out_txt.close();
    

    return 0;
}
