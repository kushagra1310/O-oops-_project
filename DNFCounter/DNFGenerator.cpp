#include <bits/stdc++.h>

using namespace std;

int rand(int l, int r) {
    return l + rand() % (r - l + 1);
}

template<typename T>
void write2DVector(FILE* fp, const vector<vector<T>>& mat) {
    if (!fp) {
        throw runtime_error("Null FILE* passed to write2DVector");
    }

    // 1) Write number of rows
    uint64_t rows = mat.size();
    if (fwrite(&rows, sizeof(rows), 1, fp) != 1) {
        throw runtime_error("Failed to write row count");
    }

    // 2) For each row, write its size and then its contents
    for (const auto& row : mat) {
        uint64_t cols = row.size();
        if (fwrite(&cols, sizeof(cols), 1, fp) != 1) {
            throw runtime_error("Failed to write column count");
        }

        if (!row.empty()) {
            // T must be trivially copyable for this to be safe
            if (fwrite(row.data(), sizeof(T), cols, fp) != cols) {
                throw runtime_error("Failed to write row data");
            }
        }
    }
}

vector<vector<pair<int, int>>> generator(int num_literals, int num_clauses, int clause_width=-1, bool var_width=false) {

    random_device rd;
    mt19937 g(rd());

    if(clause_width == -1) 
        clause_width = num_literals;

    vector<vector<pair<int, int>>> output(num_clauses);

    vector<int> literals(num_literals);
    for(int i=0; i<num_literals; i++) {
        literals[i] = i+1;
    }

    for(int i=0; i<num_clauses; i++) {

        vector<int> clause;

        int width = clause_width;

        if(var_width) {
            width = rand(2, clause_width);
        }

        sample(literals.begin(), literals.end(), back_inserter(clause), width, g);
        for(auto e : clause) {
            output[i].push_back({e, rand(0, 1)});
        }
    }

    return output;
}

int main(int argc, char** argv) {
    int samples = 20;
    int n = 5;
    int m = 20;
    int clause_width = -1; // default: full width
    bool var_width = true;

    if (argc >= 5) {
        try {
            samples = std::stoi(argv[1]);
            n = std::stoi(argv[2]);
            m = std::stoi(argv[3]);
            clause_width = std::stoi(argv[4]);
        } catch (const std::exception&) {
            std::cerr << "Failed to parse args, falling back to defaults.\n";
        }
    }

    string filename = "Data/samples" + to_string(samples) + "_literals" + to_string(n) 
    + "_clauses" + to_string(m) + "_var_width" + to_string(var_width) + ".bin";

    FILE* fp = fopen(filename.c_str(), "wb");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    for(int i=0; i<samples; i++) {
        auto out = generator(n, m, clause_width, var_width);
        size_t vecSize = out.size();
        write2DVector(fp, out);
    }

    fclose(fp);
}
