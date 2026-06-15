import os
import subprocess
import sys

def compilar_binario(cedula, nombre, apellido):
    try:
        with open("plantilla_vectorsign.c", "r") as file:
            codigo_fuente = file.read()
    except FileNotFoundError:
        print("[-] Error: No se encontró 'plantilla_vectorsign.c'")
        sys.exit(1)

    # 1. Inyección de las tres dimensiones de entropía
    codigo_mutado = codigo_fuente.replace("{{{CEDULA_PLACEHOLDER}}}", str(cedula))
    codigo_mutado = codigo_mutado.replace("{{{NOMBRE_PLACEHOLDER}}}", nombre)
    codigo_mutado = codigo_mutado.replace("{{{APELLIDO_PLACEHOLDER}}}", apellido)
    
    # 2. Polimorfismo Espacial (Desplazamiento del .text)
    bytes_desplazamiento = (int(cedula) % 1024) + 16
    asm_padding = f'".space {bytes_desplazamiento}, 0x90"'
    codigo_mutado = codigo_mutado.replace("{{{PADDING_ASM}}}", asm_padding)
    
    temp_c_file = f"temp_{cedula}.c"
    with open(temp_c_file, "w") as file:
        file.write(codigo_mutado)

    bin_name = f"reto_vectorsign_{cedula}"
    comando_gcc = [
        "gcc", "-O0", "-no-pie", "-fno-stack-protector", 
        "-o", bin_name, temp_c_file
    ]

    try:
        subprocess.run(comando_gcc, check=True, stderr=subprocess.PIPE)
        print(f"[+] Generado: {bin_name} ({nombre} {apellido})")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error al compilar para CI {cedula}:\n{e.stderr.decode()}")
    finally:
        if os.path.exists(temp_c_file):
            os.remove(temp_c_file)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 generador_lotes.py <archivo_alumnos.csv>")
        print("Formato esperado en el CSV: Cedula,Nombre,Apellido")
        sys.exit(1)

    archivo_alumnos = sys.argv[1]
    
    if not os.path.exists(archivo_alumnos):
        print(f"[-] Error: No se encuentra el archivo {archivo_alumnos}")
        sys.exit(1)

    print("=== Iniciando Generador de Lotes (Vector-Sign) ===")
    with open(archivo_alumnos, "r", encoding="utf-8") as file:
        for linea in file:
            linea = linea.strip()
            if not linea:
                continue
            
            partes = linea.split(',')
            if len(partes) != 3:
                print(f"[!] Saltando línea con formato inválido: '{linea}'")
                continue
                
            cedula, nombre, apellido = partes
            if cedula.isdigit():
                compilar_binario(cedula, nombre, apellido)
            else:
                print(f"[!] Saltando cédula inválida en: '{linea}'")
    print("=== Generación Finalizada ===")

if __name__ == "__main__":
    main()