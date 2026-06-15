import os
import csv
import hashlib
import subprocess

def generar_entropia(ci, nombre, apellido):
    """Genera una semilla determinista basada en la identidad del estudiante."""
    cadena = f"{ci}{nombre}{apellido}".lower().replace(" ", "")
    return hashlib.sha256(cadena.encode('utf-8')).digest()

def derivar_reto(hash_bytes):
    """
    Extrae los parámetros del reto garantizando Little-Endianness.
    - MASCARA_XOR: 32 bits (Ofuscación)
    - THRESHOLD_UPPER: short negativo (entre -10 y -1000)
    - THRESHOLD_LOWER: unsigned short alto (entre 40000 y 60000)
    """
    m_xor = int.from_bytes(hash_bytes[0:4], 'little')
    
    # Límite con signo (Negativo para activar el Sign Flag)
    upper_abs = (int.from_bytes(hash_bytes[4:6], 'little') % 990) + 10
    t_upper = -upper_abs
    
    # Límite sin signo (Alto para forzar evaluación por Carry Flag)
    t_lower = 40000 + (int.from_bytes(hash_bytes[6:8], 'little') % 20000)
    
    return m_xor, t_upper, t_lower

def calcular_payload_esperado(m_xor, t_upper):
    """
    Calcula una solución válida. 
    Al truncar a 16 bits, cualquier valor en los bits superiores es ignorado.
    Usaremos ceros para los 16 bits superiores de la base para estandarizar el serial.
    """
    # El valor del kernel en 16 bits (complemento a dos)
    kernel_16bit = t_upper & 0xFFFF
    
    # Aplicamos la lógica inversa (XOR es su propia inversa)
    payload_solucion = kernel_16bit ^ m_xor
    
    return f"{payload_solucion:08X}"

def generar_codigo_c(m_xor, t_lower, t_upper):
    """Molde C con Side-Effects para forzar la generación de saltos condicionales."""
    return f"""#include <stdint.h>

#define MASCARA_XOR 0x{m_xor:08X}
#define THRESHOLD_LOWER {t_lower}U
#define THRESHOLD_UPPER {t_upper}

// Declaración de función opaca. 
// Alimenta el "Branch Predictor" y bloquea la optimización 'branchless'.
extern void penalizacion_hardware(void);

int validar_mutacion(uint32_t payload) {{
    uint32_t valor_descifrado = payload ^ MASCARA_XOR;
    short kernel = (short)valor_descifrado;
    
    // Compuerta 1: Evaluación sin signo
    if ((unsigned short)kernel < THRESHOLD_LOWER) {{
        penalizacion_hardware(); // Efecto secundario forzado
        return 0; 
    }}
    
    // Compuerta 2: Evaluación con signo
    if (kernel > THRESHOLD_UPPER) {{
        penalizacion_hardware(); // Efecto secundario forzado
        return 0; 
    }}
    
    return 1;
}}
"""

def desplegar_dinamica(archivo_csv):
    dir_salida = "entregables_alumnos"
    os.makedirs(dir_salida, exist_ok=True)
    
    with open(archivo_csv, 'r') as f_in, open('matriz_asimetria.csv', 'w', newline='') as f_out:
        lector = csv.reader(f_in)
        escritor = csv.writer(f_out)
        escritor.writerow(['CI', 'Nombre', 'Apellido', 'Payload_Esperado', 'T_LOWER', 'T_UPPER', 'MASCARA'])
        
        cabecera = next(lector, None)
        if cabecera and cabecera[0].lower() != 'ci': f_in.seek(0)
            
        for fila in lector:
            if not fila or len(fila) < 3: continue
            ci, nombre, apellido = [c.strip() for c in fila[0:3]]
            print(f"[*] Compilando topología de silicio para: {ci}")
            
            hash_bytes = generar_entropia(ci, nombre, apellido)
            m_xor, t_upper, t_lower = derivar_reto(hash_bytes)
            
            payload_esperado = calcular_payload_esperado(m_xor, t_upper)
            
            src_file = f"temp_{ci}.c"
            obj_file = os.path.join(dir_salida, f"caja_negra_{ci}.o")
            
            with open(src_file, 'w') as f_c:
                f_c.write(generar_codigo_c(m_xor, t_lower, t_upper))
                
            # Compilación con -O1 para respetar el desensamblado pedagógico
            subprocess.run(['gcc', '-O1', '-c', src_file, '-o', obj_file], check=True)
            os.remove(src_file)
            
            escritor.writerow([ci, nombre, apellido, payload_esperado, t_lower, t_upper, f"{m_xor:08X}"])
            print(f"    [+] .o Generado. Solución esperada: {payload_esperado}")

if __name__ == "__main__":
    if not os.path.exists("estudiantes.csv"):
        with open("estudiantes.csv", "w") as f:
            f.write("CI,Nombre,Apellido\n27555111,Sergio,Lopez\n11223344,Javier,Lopez\n")
    print("=== MOTOR DE DESPLIEGUE: ASIMETRÍA DE SIGNO ===")
    desplegar_dinamica("estudiantes.csv")