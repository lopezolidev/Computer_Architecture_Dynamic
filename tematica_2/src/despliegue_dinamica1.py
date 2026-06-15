import os
import csv
import hashlib
import subprocess

# =====================================================================
# MOTOR DE ENTROPÍA Y DERIVACIÓN (Basado en CS:APP Cap 2)
# =====================================================================

def generar_entropia(ci, nombre, apellido):
    """
    Sanitiza los datos de entrada y genera una semilla criptográfica determinista.
    """
    cadena = f"{ci}{nombre}{apellido}".lower().replace(" ", "")
    return hashlib.sha256(cadena.encode('utf-8')).digest()

def derivar_reto(hash_bytes):
    """
    Extrae los datos respetando el ordenamiento Little-Endian de x86-64.
    """
    # 1 byte para el char objetivo (enmascarado para ser ASCII imprimible)
    char_obj = (hash_bytes[0] & 0x7F) | 0x20 
    
    # Dos bloques de 4 bytes para el enigma aritmético del int
    mascara_xor = int.from_bytes(hash_bytes[1:5], 'little')
    resultado_esperado = int.from_bytes(hash_bytes[5:9], 'little')
    
    # El valor int que el estudiante debe deducir resolviendo el XOR analíticamente
    int_solucion = mascara_xor ^ resultado_esperado
    
    # 2 bytes para el short
    short_obj = int.from_bytes(hash_bytes[9:11], 'little')
    
    # Mutación Topológica: Selección de la estructura (0, 1 o 2)
    variante_topologica = hash_bytes[12] % 3
    
    return char_obj, mascara_xor, resultado_esperado, int_solucion, short_obj, variante_topologica

def calcular_serial_arquitectonico(v_id, int_solucion):
    """
    Calcula el tamaño total y el offset del double basado en las estrictas 
    reglas de alineación de la ABI x86-64 (CS:APP 3.9.3).
    """
    if v_id == 0:
        # Topología: char(0), int(4), double(8), short(16)
        # Padding interno: 3 bytes tras el char. 
        # Padding final: 6 bytes para alinear a múltiplo de 8.
        tamano = 24
        offset_double = 8
    elif v_id == 1:
        # Topología: double(0), int(8), short(12), char(14)
        # Padding interno: Ninguno. 
        # Padding final: 1 byte para alinear a múltiplo de 8 (tamaño total = 16).
        tamano = 16
        offset_double = 0
    else: # v_id == 2
        # Topología: int(0), char(4), double(8), short(16)
        # Padding interno: 3 bytes tras el char.
        # Padding final: 6 bytes para alinear a múltiplo de 8.
        tamano = 24
        offset_double = 8
        
    # Formato del Vector de Estado: [TAMAÑO_TOTAL]-[OFFSET_DOUBLE]-[VALOR_INT_HEX]
    serial = f"{tamano:02d}-{offset_double:02d}-{int_solucion:08X}"
    return serial

# =====================================================================
# GENERACIÓN DE CÓDIGO MÁQUINA
# =====================================================================

def generar_codigo_c_variante(v_id, char_obj, m_xor, res_esp, short_obj):
    """
    Inyecta las constantes en el molde estructural seleccionado.
    El estudiante jamás verá este código fuente.
    """
    comunes = f"""#include <stdint.h>
#define CHAR_OBJ '{chr(char_obj)}'
#define M_XOR 0x{m_xor:08X}
#define RES_ESP 0x{res_esp:08X}
#define SHORT_OBJ 0x{short_obj:04X}
#define IEEE_OBJ 2.0
"""
    # Definición de la topología en C
    if v_id == 0:
        struct_def = "struct Carga { char a; int b; double c; short d; };"
        checks = "if(c->a != CHAR_OBJ) return 0; if((c->b ^ M_XOR) != RES_ESP) return 0; if(c->c != IEEE_OBJ) return 0; if(c->d != SHORT_OBJ) return 0;"
    elif v_id == 1:
        struct_def = "struct Carga { double c; int b; short d; char a; };"
        checks = "if(c->c != IEEE_OBJ) return 0; if((c->b ^ M_XOR) != RES_ESP) return 0; if(c->d != SHORT_OBJ) return 0; if(c->a != CHAR_OBJ) return 0;"
    else:
        struct_def = "struct Carga { int b; char a; double c; short d; };"
        checks = "if((c->b ^ M_XOR) != RES_ESP) return 0; if(c->a != CHAR_OBJ) return 0; if(c->c != IEEE_OBJ) return 0; if(c->d != SHORT_OBJ) return 0;"

    return comunes + struct_def + f"\nint validar_acceso(void *ptr) {{\n    struct Carga *c = (struct Carga *)ptr;\n    {checks}\n    return 1;\n}}"

# =====================================================================
# ORQUESTADOR PRINCIPAL (Deployment Pipeline)
# =====================================================================

def desplegar_arqueologia(archivo_csv):
    dir_salida = "entregables_alumnos"
    os.makedirs(dir_salida, exist_ok=True)
    
    with open(archivo_csv, 'r') as f_in, open('matriz_correccion_profesor.csv', 'w', newline='') as f_out:
        lector = csv.reader(f_in)
        escritor = csv.writer(f_out)
        
        # El CSV de corrección ahora es puro O(1): Identidad y Serial
        escritor.writerow(['CI', 'Nombre', 'Apellido', 'Serial_Esperado'])
        
        # Saltar cabecera si existe
        cabecera = next(lector, None)
        if cabecera and cabecera[0].lower() != 'ci': f_in.seek(0)
            
        for fila in lector:
            if not fila or len(fila) < 3: continue
            ci, nombre, apellido = [c.strip() for c in fila[0:3]]
            print(f"[*] Ensamblando topología para: {ci} - {nombre} {apellido}")
            
            # 1. Generar entropía matemática
            hash_bytes = generar_entropia(ci, nombre, apellido)
            char_obj, m_xor, res_esp, int_sol, short_obj, v_id = derivar_reto(hash_bytes)
            
            # 2. Calcular el Serial Arquitectónico Definitivo
            serial_esperado = calcular_serial_arquitectonico(v_id, int_sol)
            
            # 3. Compilación a archivo objeto (.o) con nivel de optimización 1
            src_file = f"temp_{ci}.c"
            obj_file = os.path.join(dir_salida, f"caja_negra_{ci}.o")
            
            with open(src_file, 'w') as f_c:
                f_c.write(generar_codigo_c_variante(v_id, char_obj, m_xor, res_esp, short_obj))
                
            # Usamos -O1 para un desensamblado claro pero respetando las reglas ABI
            subprocess.run(['gcc', '-O1', '-c', src_file, '-o', obj_file], check=True)
            os.remove(src_file)
            
            # 4. Inyección en la matriz de corrección
            escritor.writerow([ci, nombre, apellido, serial_esperado])
            print(f"    [+] Éxito. Variante {v_id}. Serial asignado: {serial_esperado}")

if __name__ == "__main__":
    # Genera un archivo de prueba si no se proporciona uno
    if not os.path.exists("estudiantes.csv"):
        with open("estudiantes.csv", "w") as f:
            f.write("CI,Nombre,Apellido\n")
            f.write("27555111,Sergio,Lopez\n")
            f.write("11223344,Javier,Lopez\n")
            
    print("=== INICIANDO DESPLIEGUE: ARQUEOLOGIA DE ESTRUCTURAS ===")
    desplegar_arqueologia("estudiantes.csv")
    print("\n[+] Archivos de código objeto (.o) listos en 'entregables_alumnos/'")
    print("[+] Matriz de evaluación O(1) lista en 'matriz_correccion_profesor.csv'")