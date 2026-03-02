#include "my_extern_clib.h"

long external_c_function(long* data_view, int size){
    long result = 0;
    for (int i = 0; i < size; i++){
        result += data_view[i];
    }
    return result;
}
