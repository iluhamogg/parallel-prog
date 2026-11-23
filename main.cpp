#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;

class Matrix {
    int n;
    vector<vector<double>> data;
public:
    Matrix(int size) : n(size), data(size, vector<double>(size, 0)) {}
    static Matrix load(const string& filename) {
        ifstream in(filename);
        int size;
        if (!(in >> size) || size <= 0) throw runtime_error("Cannot read matrix: " + filename);
        Matrix m(size);
        for (auto& row : m.data)
            for (double& x : row)
                if (!(in >> x)) throw runtime_error("Invalid matrix data: " + filename);
        return m;
    }
    int size() const { return n; }
    Matrix multiply(const Matrix& b) const {
        if (n != b.n) throw runtime_error("Matrix sizes differ");
        Matrix c(n);
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j)
                for (int k = 0; k < n; ++k)
                    c.data[i][j] += data[i][k] * b.data[k][j];
        return c;
    }
    void save(const string& filename) const {
        ofstream out(filename);
        if (!out) throw runtime_error("Cannot create result file");
        out << n << '\n' << setprecision(17);
        for (const auto& row : data) {
            for (double x : row) out << x << ' ';
            out << '\n';
        }
    }
};

int main(int argc, char* argv[]) {
    try {
        string a = argc > 1 ? argv[1] : "A.txt";
        string b = argc > 2 ? argv[2] : "B.txt";
        string result = argc > 3 ? argv[3] : "result.txt";
        Matrix A = Matrix::load(a), B = Matrix::load(b);
        auto start = chrono::steady_clock::now();
        Matrix C = A.multiply(B);
        auto finish = chrono::steady_clock::now();
        C.save(result);
        double seconds = chrono::duration<double>(finish - start).count();
        long long n = A.size();
        cout << fixed << setprecision(6)
             << "N=" << n << " time_sec=" << seconds
             << " operations=" << 2LL*n*n*n
             << " memory_bytes=" << 3LL*n*n*sizeof(double) << '\n';
    } catch (const exception& e) {
        cerr << e.what() << '\n';
        return 1;
    }
}
