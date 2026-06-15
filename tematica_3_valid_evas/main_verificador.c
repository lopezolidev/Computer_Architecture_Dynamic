#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

extern int validar_mutacion(uint32_t payload);

// Implementación de la función opaca. 
// El compilador no podía ver esto cuando generó el .o del estudiante.
void penalizacion_hardware(void) {
    // Simulamos un flush del pipeline imprimiendo a stderr
    fprintf(stderr, "    [!] Branch Misprediction simulado. Vaciando pipeline...\n");
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <PAYLOAD_HEXADECIMAL_DE_32_BITS>\n", argv[0]);
        return EXIT_FAILURE;
    }

    uint32_t payload = (uint32_t)strtoul(argv[1], NULL, 16);

    printf("[*] Inyectando Payload en %%edi: 0x%08X\n", payload);
    printf("[*] Evaluando el arbol de saltos (Branch Tree)...\n");

    int eax_estado = validar_mutacion(payload);

    if (eax_estado == 1) {
        printf("\n[+] BARRERA SUPERADA (EAX = 1).\n");
        printf("[+] Asimetria de signo explotada con exito.\n");
        return EXIT_SUCCESS;
    } else {
        printf("\n[-] FALLO (EAX = 0). Las compuertas rechazaron el payload.\n");
        return EXIT_FAILURE;
    }
}