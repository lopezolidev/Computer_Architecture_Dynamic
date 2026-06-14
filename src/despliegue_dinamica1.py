import os
import csv
import hashlib
import subprocess

# =====================================================================
# CONSTANTES ARQUITECTÓNICAS Y MATEMÁTICAS (CS:APP Cap. 2 y 3)
# =====================================================================
MASK_64 = 0xFFFFFFFFFFFFFFFF
INV_MOD_5 = 0xCCCCCCCCCCCCCCCD
INDICE_EXITO = 3

def generar_entropia(ci, nombre, apellido):
    """
    Sanitiza los datos de entrada y genera una semilla criptográfica determinista.
    """
    cadena_base = f"{ci}{nombre}{apellido}".lower().replace(" ", "")
    return hashlib.sha256(cadena_base.encode('utf-8')).digest()

def derivar_parametros_little_endian(hash_estudiante):
    """
    Extrae la Matriz Mutante y la Firma respetando el ordenamiento de bytes de x86-64.
    Alinea la Firma para garantizar el aterrizaje en la Jump Table.
    """
    m0 = int.from_bytes(hash_estudiante[0:8], byteorder='little')
    m1 = int.from_bytes(hash_estudiante[8:16], byteorder='little')
    m2 = int.from_bytes(hash_estudiante[16:24], byteorder='little')
    m3 = int.from_bytes(hash_estudiante[24:32], byteorder='little')
    
    hash_firma = hashlib.sha256(hash_estudiante).digest()
    firma_bruta = int.from_bytes(hash_firma[0:8], byteorder='little')
    
    # [!] PARCHE: Alineacion de la Jump Table
    # 1. (~0x07) apaga los ultimos 3 bits (Los vuelve 000).
    # 2. (| INDICE_EXITO) enciende los bits exactos para forzar el estado a terminar en 3.
    firma_alineada = (firma_bruta & ~0x07) | INDICE_EXITO
    
    return [m0, m1, m2, m3], firma_alineada

def calcular_llave_maestra(matriz, firma_objetivo):
    """
    Keygen Analítico: Revierte la cascada de estado módulo 2^64.
    """
    estado = firma_objetivo
    for i in range(3, -1, -1):
        estado = (estado - i) & MASK_64                     # Revierte ALU ADD
        estado = (estado * INV_MOD_5) & MASK_64             # Revierte AGU LEAQ
        estado = estado ^ matriz[i]                         # Revierte Máscara XOR
    return estado

def generar_codigo_c(matriz, firma):
    """
    Esqueleto en C con inyección de constantes y bloqueo de heurísticas de GCC.
    """
    return f"""#include <stdint.h>

#define M_0 0x{matriz[0]:016X}ULL
#define M_1 0x{matriz[1]:016X}ULL
#define M_2 0x{matriz[2]:016X}ULL
#define M_3 0x{matriz[3]:016X}ULL
#define FIRMA_OBJETIVO 0x{firma:016X}ULL
#define INDICE_EXITO {INDICE_EXITO}

__attribute__((optimize("no-unroll-loops")))
int validar_mutacion(uint64_t key) {{
    uint64_t estado = key;
    const uint64_t matriz[4] = {{M_0, M_1, M_2, M_3}};

    for (int i = 0; i < 4; i++) {{
        estado ^= matriz[i];
        estado = (estado * 5) + i; 
    }}

    uint8_t indice = estado & 0x07;

    switch(indice) {{
        case 0: return 0x10; case 1: return 0x11; case 2: return 0x12;
        case INDICE_EXITO: 
            if (estado == FIRMA_OBJETIVO) return 1; 
            return 0x13;
        case 4: return 0x14; case 5: return 0x15; case 6: return 0x16; case 7: return 0x17;
        default: return 0;
    }}
}}
"""

def desplegar_evaluaciones(archivo_csv):
    """
    Orquesta la lectura, inyección, ensamblado y registro de binarios.
    """
    dir_salida = "entregables_alumnos"
    os.makedirs(dir_salida, exist_ok=True)
    
    archivo_matriz = 'claves_maestras_profesor.csv'
    
    with open(archivo_csv, mode='r') as f_in, open(archivo_matriz, mode='w', newline='') as f_out:
        lector = csv.reader(f_in)
        escritor = csv.writer(f_out)
        escritor.writerow(['CI', 'Nombre', 'Apellido', 'Llave_Solucion_Hex', 'Firma_Objetivo_Hex'])
        
        # Omitir cabecera si existe
        cabecera = next(lector, None)
        if cabecera and cabecera[0].lower() != 'ci':
            f_in.seek(0)
            
        for fila in lector:
            if not fila or len(fila) < 3: continue
            
            ci, nombre, apellido = [campo.strip() for campo in fila[0:3]]
            print(f"[*] Procesando: {ci} - {nombre} {apellido}")
            
            
            # 1. Generación de entropía
            hash_estudiante = generar_entropia(ci, nombre, apellido)
            # 2. Derivación de datos en memoria
            matriz, firma = derivar_parametros_little_endian(hash_estudiante)
            # 3. Resolución analítica del inverso
            llave_maestra = calcular_llave_maestra(matriz, firma)
            
            # Generación y compilación
            src_file = f"temp_{ci}.c"
            obj_file = os.path.join(dir_salida, f"caja_negra_{ci}.o")
            
            with open(src_file, 'w') as f_c:
                f_c.write(generar_codigo_c(matriz, firma))
                
            subprocess.run(['gcc', '-O2', '-c', src_file, '-o', obj_file], check=True)
            os.remove(src_file)
            
            # Registro en hoja de corrección
            escritor.writerow([ci, nombre, apellido, f"0x{llave_maestra:016X}", f"0x{firma:016X}"])
            print(f"    [+] Ensamblado exitoso. Llave: 0x{llave_maestra:016X}")

if __name__ == "__main__":
    if not os.path.exists("estudiantes.csv"):
        with open("estudiantes.csv", "w") as f:
            f.write("CI,Nombre,Apellido\n")
            f.write("27555111,Sergio,Lopez\n")
            f.write("12345678,Ana,Perez\n")
            
    print("=== INICIANDO PIPELINE DE COMPILACION - DINAMICA 1 ===")
    desplegar_evaluaciones("estudiantes.csv")
    print(f"\n[+] Despliegue completado. Archivos .o listos en 'entregables_alumnos/'")
    print("[+] Hoja de corrección generada: 'claves_maestras_profesor.csv'")