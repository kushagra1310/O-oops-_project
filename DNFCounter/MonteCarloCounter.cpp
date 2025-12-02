#include <bits/stdc++.h>
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iomanip>
#include <chrono>
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


// Monte Carlo DNF counting (Algorithm II)
double solve_dnf(const vector<vector<pair<int, int>>>& dnf, int num_vars, int& samples_used) {
    int t = dnf.size();
    int m = ceil((3 * t / (eps*eps)) * log(2/delta));
    samples_used = m;
    // m = 10000;
    cout << m << "\n";
    if (dnf.empty() || num_vars <= 0 || m <= 0) {
        return 0.0;
    }

    vector<double> weights;
    weights.reserve(dnf.size());
    for (const auto& clause : dnf) {
        int clause_size = static_cast<int>(clause.size());
        if (clause_size > num_vars) {
            weights.push_back(0.0);
            continue;
        }
        // |SC_i| = 2^(n - |clause|)
        weights.push_back(static_cast<double>(1ULL << (num_vars - clause_size)));
    }

    double total_weight = accumulate(weights.begin(), weights.end(), 0.0);
    if (total_weight == 0.0) {
        return 0.0;
    }

    std::mt19937 rng(std::random_device{}());
    std::discrete_distribution<int> clause_dist(weights.begin(), weights.end());
    std::uniform_int_distribution<int> bit_dist(0, 1);

    auto clause_satisfied = [&](const vector<pair<int, int>>& clause,
                                const vector<int>& assignment) -> bool {
        for (const auto& lit : clause) {
            int var_idx = lit.first;
            int is_negated = lit.second;
            if (var_idx <= 0 || var_idx > num_vars) return false;
            bool value = assignment[var_idx];
            if (is_negated) value = !value;
            if (!value) return false;
        }
        return true;
    };

    int X = 0;

    for (int k = 0; k < m; ++k) {
        int i = clause_dist(rng);  // chosen clause index
        const auto& clause = dnf[i];

        vector<int> assignment(num_vars + 1, 0);

        // Random assignment
        for (int v = 1; v <= num_vars; ++v) {
            assignment[v] = bit_dist(rng);
        }
        // Force literals in chosen clause to be satisfied
        for (const auto& lit : clause) {
            int var_idx = lit.first;
            int is_negated = lit.second;
            if (var_idx > 0 && var_idx <= num_vars) {
                assignment[var_idx] = is_negated ? 0 : 1;
            }
        }

        bool in_prior = false;
        for (int j = 0; j < i; ++j) {
            if (clause_satisfied(dnf[j], assignment)) {
                in_prior = true;
                break;
            }
        }

        if (!in_prior) {
            ++X;
        }
    }

    double Y = (static_cast<double>(X) / static_cast<double>(m)) * total_weight;
    return Y;
}


int main(int argc, char** argv) {

    if (argc >= 3) {
        try {
            eps = std::stod(argv[1]);
            delta = std::stod(argv[2]);
        } catch (const std::exception&) {
            std::cerr << "Failed to parse eps/delta, using defaults.\n";
        }
    }

    
    
    const char* in_path = (argc >= 4) ? argv[3] : "Data/samples20_literals60_clauses20_var_width1.bin";
    FILE* fp = std::fopen(in_path, "rb");
    if (!fp) {
        std::perror("fopen for read");
        return 1;
    }

    std::filesystem::create_directories("OutputMonte");
    std::ostringstream eps_delta_ss;
    eps_delta_ss << std::fixed << std::setprecision(2) << eps << "_" << std::fixed << std::setprecision(2) << delta;
    std::string ofile = (std::filesystem::path("OutputMonte") /
                        (std::filesystem::path(in_path).filename().string() +
                         "_kl" + eps_delta_ss.str() + ".txt")).string();

    std::ofstream out_txt(ofile);
    if (!out_txt) {
        std::perror("opening output txt");
        std::fclose(fp);
        return 1;
    }

    std::vector<std::vector<pair<int, int>>> mat;
    int idx = 0;

    // Derive num_vars from filename pattern "..._literals<NUM>_..."
    int num_vars = 20;
    {
        std::string path_str(in_path);
        auto pos = path_str.find("literals");
        if (pos != std::string::npos) {
            pos += std::string("literals").size();
            size_t end = pos;
            while (end < path_str.size() && std::isdigit(path_str[end])) {
                ++end;
            }
            if (end > pos) {
                try {
                    num_vars = std::stoi(path_str.substr(pos, end - pos));
                } catch (...) {
                    num_vars = 20;
                }
            }
        }
    }

    auto wall_start = std::chrono::steady_clock::now();
    int samples_used = 0;
    std::string status = "ok";

    try {
        while (true) {
            bool ok = read2DVector(fp, mat);
            if (!ok) {
                break; // no more matrices
            }

            long long count = round(solve_dnf(mat, num_vars, samples_used));
            std::cout << "Matrix #" << idx++
                      << " satisfying assignments (approx): " << count << '\n';
            out_txt << count << '\n';
        }
    } catch (const std::exception& e) {
        std::cerr << "Error reading: " << e.what() << '\n';
        status = "error";
    }

    auto wall_end = std::chrono::steady_clock::now();
    double seconds = std::chrono::duration<double>(wall_end - wall_start).count();

    std::fclose(fp);
    out_txt.close();

    // Append timing and sampling info to a run log CSV.
    std::filesystem::create_directories("OutputMonte");
    std::string log_path = "OutputMonte/monte_run_log.csv";
    std::ofstream log(log_path, std::ios::app);
    if (log) {
        log.seekp(0, std::ios::end);
        if (log.tellp() == 0) {
            log << "file,num_vars,samples_used,seconds,status,eps,delta\n";
        }
        log << in_path << ','
            << num_vars << ','
            << samples_used << ','
            << std::fixed << std::setprecision(6) << seconds << ','
            << status << ','
            << eps << ','
            << delta << '\n';
    }
    

    return 0;
}
