#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// =========================================================================
// SUBRUTINAS DE CONTROL DE FLUJO
// =========================================================================
void generar_token_exito() {
    printf("\n[!!!] CONTROL FLOW HIJACK EXITOSO [!!!]\n");
    printf("[*] El Run-Time Stack fue alterado. %rip redireccionado.\n\n");
    
    FILE *f = fopen("estudiante_id.txt", "r");
    if (!f) {
        printf("[-] Error: Archivo 'estudiante_id.txt' no encontrado.\n");
        exit(1);
    }
    
    uint64_t ci;
    fscanf(f, "%lu", &ci);
    fclose(f);

    // Algoritmo de Hashing a nivel de bits (CS:APP Cap 2)
    uint64_t salt = 0xDEADBEEFCAFEBABE;
    uint64_t token = ci ^ salt;
    // Rotación circular a la izquierda (Left Rotate por 13 bits)
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
// ESTRUCTURA DE DATOS (Alineación estricta - System V AMD64 ABI)
// =========================================================================
struct ContextoEjecucion {
    void (*funcion_salida)(); // Puntero a función (Offset 0, 8 bytes)
    long registros[8];        // Arreglo contiguo (Offset 8, 64 bytes)
};

// =========================================================================
// DATAPATH Y LÓGICA PRINCIPAL
// =========================================================================
void procesar_registros() {
    struct ContextoEjecucion ctx;
    ctx.funcion_salida = rutina_salida_estandar; 
    
    int indice;
    long valor;

    printf("Ingrese el índice del registro a actualizar (0-7): ");
    if (scanf("%d", &indice) != 1) exit(1);

    // BARRERA CONDICIONAL VULNERABLE (Comparación con signo)
    if (indice > 7) {
        printf("[-] Error: Índice fuera de los límites permitidos.\n");
        return;
    }

    printf("Ingrese el nuevo valor para el registro (Decimal): ");
    if (scanf("%ld", &valor) != 1) exit(1);

    // ESCRITURA EN MEMORIA
    // Si índice es -1: Offset base de 'registros' + (-1 * 8 bytes) 
    // = Offset del puntero 'funcion_salida'.
    ctx.registros[indice] = valor;

    printf("[*] Procesamiento finalizado. Invocando subrutina de cierre...\n");
    
    // EJECUCIÓN (Call indirecto)
    ctx.funcion_salida(); 
}

int main() {
    // Desactivamos el buffering para garantizar I/O sincrónico en la consola
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("--- Laboratorio: Vector-Sign (Control Flow Hijack) ---\n");
    procesar_registros();
    return 0;
}