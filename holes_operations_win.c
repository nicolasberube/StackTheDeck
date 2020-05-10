__declspec(dllexport) void min_update(int* vector, int* sub_index, int val, int n)
{
    for (int i = 0; i < n; i++) {
        if (vector[sub_index[i]] > val) {
            vector[sub_index[i]] = val;
        }
    }
    return;
}


__declspec(dllexport) int is_under(int* vector, int val, int n)
{
    int res = 0;
    for (int i = 0; i < n; i++) {
        if (vector[i] < val) {
            res++;
        }
    }
    return res;
}

__declspec(dllexport) int is_equal(int* vector, int val, int n)
{
    int res = 0;
    for (int i = 0; i < n; i++) {
        if (vector[i] == val) {
            res++;
        }
    }
    return res;
}
