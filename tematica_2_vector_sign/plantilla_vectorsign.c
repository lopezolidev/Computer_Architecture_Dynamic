#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// =========================================================================
// MACROS INYECTADAS EN TIEMPO DE COMPILACIÓN (Entropía Máxima)
// =========================================================================
#define STUDENT_CI {{{CEDULA_PLACEHOLDER}}}
#define STUDENT_NOMBRE "{{{NOMBRE_PLACEHOLDER}}}"
#define STUDENT_APELLIDO "{{{APELLIDO_PLACEHOLDER}}}"

void __attribute__((noinline)) desplazamiento_memoria() {
    __asm__ __volatile__({{{PADDING_ASM}}});
}

// =========================================================================
// PROCESAMIENTO DE CARACTERES ASCII A NIVEL DE BITS 
// =========================================================================
uint64_t hash_cadena(const char* str) {
    uint64_t hash = 0x1234567890ABCDEF; // Semilla base para strings
    for (int i = 0; str[i] != '\0'; i++) {
        // Rotación circular izquierda (7 bits) y XOR con el valor ASCII del byte
        // Nota: Como 'hash' es unsigned, >> realiza un "Logical Shift" (rellena con 0s)
        hash = ((hash << 7) | (hash >> (64 - 7))) ^ (uint64_t)str[i];
    }
    return hash;
}

// =========================================================================
// SUBRUTINAS DE CONTROL DE FLUJO
// =========================================================================
void generar_token_exito() {
    printf("\n[!!!] CONTROL FLOW HIJACK EXITOSO [!!!]\n");
    printf("[*] El Run-Time Stack fue alterado. %%rip redireccionado.\n\n");
    
    uint64_t ci = STUDENT_CI; 
    uint64_t salt = 0xDEADBEEFCAFEBABE;
    
    // Fusión de entropía: CI + Representación ASCII del Nombre y Apellido
    uint64_t token = ci ^ salt;
    token ^= hash_cadena(STUDENT_NOMBRE);
    token ^= hash_cadena(STUDENT_APELLIDO);
    
    // Rotación final y máscara
    token = (token << 13) | (token >> (64 - 13)); 
    token = token ^ 0x0123456789ABCDEF;

    printf("FLAG_VECTORSIGN_%lX\n", token);
    exit(0);
}

void rutina_salida_estandar() {
    printf("[*] Ejecutando rutina de limpieza y salida estándar...\n");
    exit(0);
}

// =========================================================================
// ESTRUCTURA DE DATOS VULNERABLE
// =========================================================================
struct ContextoEjecucion {
    void (*funcion_salida)(); 
    long registros[8];        
};

void procesar_registros() {
    struct ContextoEjecucion ctx;
    ctx.funcion_salida = rutina_salida_estandar; 
    
    int indice;
    long valor;

    printf("Ingrese el índice del registro a actualizar (0-7): ");
    if (scanf("%d", &indice) != 1) exit(1);

    if (indice > 7) {
        printf("[-] Error: Índice fuera de los límites permitidos.\n");
        return;
    }

    printf("Ingrese el nuevo valor para el registro (Decimal): ");
    if (scanf("%ld", &valor) != 1) exit(1);

    ctx.registros[indice] = valor;

    printf("[*] Procesamiento finalizado. Invocando subrutina de cierre...\n");
    ctx.funcion_salida(); 
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("--- Laboratorio: Vector-Sign (Control Flow Hijack) ---\n");
    printf("--- Binario asiganado a: %s %s (CI: %lu) ---\n", STUDENT_NOMBRE, STUDENT_APELLIDO, (uint64_t)STUDENT_CI);
    procesar_registros();
    return 0;
}