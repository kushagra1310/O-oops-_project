#include <bits/stdc++.h>
#include <fstream>
#include <filesystem>
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


int solve_dnf(const vector<vector<pair<int, int>>>& dnf, int num_vars) {
    const int total_masks = 1 << num_vars; // assumes num_vars small enough to brute force

    int satisfied = 0;

    for (int mask = 0; mask < total_masks; ++mask) {
        bool formula_true = false;

        for (const auto& clause : dnf) {
            bool clause_true = true;

            for (const auto& lit : clause) {
                int var_idx = lit.first;
                int is_negated = lit.second;

                if (var_idx <= 0 || var_idx > num_vars) {
                    clause_true = false;
                    break;
                }

                bool value = (mask >> (var_idx - 1)) & 1;
                if (is_negated) {
                    value = !value;
                }

                if (!value) {
                    clause_true = false;
                    break;
                }
            }

            if (clause_true) {
                formula_true = true; // DNF satisfied by this assignment
                break;
            }
        }

        if (formula_true) {
            ++satisfied;
        }
    }

    return satisfied;
}


int main(int argc, char** argv) {
    
    const char* in_path = (argc >= 2) ? argv[1] : "Data/samples20_literals5_clauses20_var_width1.bin";
    FILE* fp = std::fopen(in_path, "rb");
    if (!fp) {
        std::perror("fopen for read");
        return 1;
    }

    std::filesystem::create_directories("Output");
    std::filesystem::path out_path = std::filesystem::path("Output") /
                                     (std::filesystem::path(in_path).filename().string() + "_sol.txt");
    std::ofstream out_txt(out_path);
    if (!out_txt) {
        std::perror("opening output txt");
        std::fclose(fp);
        return 1;
    }

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

    std::vector<std::vector<pair<int, int>>> mat;
    int idx = 0;

    try {
        while (true) {
            bool ok = read2DVector(fp, mat);
            if (!ok) {
                break; // no more matrices
            }

            int count = solve_dnf(mat, num_vars);
            std::cout << "Matrix #" << idx++
                      << " satisfying assignments: " << count << '\n';
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
