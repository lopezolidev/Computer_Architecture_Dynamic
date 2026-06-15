// solucion.h
#include <stdint.h>

// 1. La topología de memoria deducida del objdump
struct EstructuraDeducida {
    double c;
    int b;
    short d;
    char a;
};

// 2. La inyección del estado matemático calculado
void cargar_valores(struct EstructuraDeducida *ptr) {
    ptr->c = 2.0;
    ptr->b = 0xDEADBEEF ^ 0xCAFEBABE; // O el valor ya resuelto
    ptr->d = 0x1337;
    ptr->a = 0x7F;
}