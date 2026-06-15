#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Prototipo de la rutina ofuscada (Reside en el archivo .o provisto por el profesor)
extern int validar_mutacion(uint64_t key);

int main(int argc, char *argv[]) {
    // 1. Validación de argumentos en el Run-Time
    if (argc != 2) {
        fprintf(stderr, "Uso de la herramienta de diagnostico:\n");
        fprintf(stderr, "$ %s <CLAVE_HEXADECIMAL_DE_64_BITS>\n", argv[0]);
        fprintf(stderr, "Ejemplo: %s 0x123456789ABCDEF0\n", argv[0]);
        return EXIT_FAILURE;
    }

    // 2. Parseo estricto del string a un entero no signado de 64 bits (CS:APP 2.1)
    uint64_t key = strtoull(argv[1], NULL, 16);

    printf("[*] Inyectando llave maestra: 0x%016lX\n", key);
    printf("[*] Transfiriendo control a la Matriz Mutante...\n");

    // 3. Salto hacia la rutina de la Caja Negra (Paso de parámetro por %rdi)
    int resultado = validar_mutacion(key);

    // 4. Evaluación del flujo de retorno (%eax)
    if (resultado == 1) {
        printf("\n[+] EXITO: Firma criptografica valida. Entropia alineada.\n");
        printf("[+] Has superado la barrera del silicio.\n\n");
        return EXIT_SUCCESS;
    } else {
        printf("\n[-] FALLO: Segmento logico colapsado. La matriz te ha rechazado.\n\n");
        return EXIT_FAILURE;
    }
}