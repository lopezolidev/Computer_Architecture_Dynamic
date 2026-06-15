import sys

def hash_cadena(cadena):
    hash_val = 0x1234567890ABCDEF
    for char in cadena:
        # Simulamos un logical shift de 64 bits y aplicamos XOR con el byte ASCII
        hash_val = ((hash_val << 7) & 0xFFFFFFFFFFFFFFFF) | (hash_val >> (64 - 7))
        hash_val ^= ord(char) # ord() extrae el valor numérico ASCII del caracter
    return hash_val

def derivar_hash_matematico(cedula, nombre, apellido):
    salt = 0xDEADBEEFCAFEBABE
    token = cedula ^ salt
    
    # Integramos la entropía de los strings
    token ^= hash_cadena(nombre)
    token ^= hash_cadena(apellido)
    
    # Simulación de la rotación final de 64 bits
    token = ((token << 13) & 0xFFFFFFFFFFFFFFFF) | (token >> (64 - 13))
    token ^= 0x0123456789ABCDEF
    
    return f"{token:X}"

def evaluar_entrega(cedula, nombre, apellido, flag_entregado):
    flag_limpio = str(flag_entregado).strip().upper()
    if flag_limpio.startswith("FLAG_VECTORSIGN_"):
        flag_limpio = flag_limpio.replace("FLAG_VECTORSIGN_", "")

    hash_esperado = derivar_hash_matematico(cedula, nombre, apellido)

    if flag_limpio == hash_esperado:
        return True, hash_esperado
    else:
        return False, hash_esperado

def main():
    if len(sys.argv) != 5:
        print("Uso: python3 evaluador.py <Cedula> <Nombre> <Apellido> <Flag_Obtenido>")
        print("Ejemplo: python3 evaluador.py 28111222 Carlos Perez FLAG_VECTORSIGN_A1B2...")
        sys.exit(1)

    try:
        cedula = int(sys.argv[1])
    except ValueError:
        print("[-] Error crítico: La Cédula debe ser un número entero válido.")
        sys.exit(1)

    nombre = sys.argv[2]
    apellido = sys.argv[3]
    flag_entregado = sys.argv[4]

    aprobado, hash_esperado = evaluar_entrega(cedula, nombre, apellido, flag_entregado)

    if aprobado:
        print(f"[====================================================]")
        print(f"[++] ALUMNO: {nombre} {apellido} (CI: {cedula})")
        print(f"[++] ESTADO: APROBADO")
        print(f"[++] Control Flow Hijack matemático exitoso.")
        print(f"[====================================================]")
        sys.exit(0)
    else:
        print(f"[----------------------------------------------------]")
        print(f"[--] ALUMNO: {nombre} {apellido} (CI: {cedula})")
        print(f"[--] ESTADO: REPROBADO / FRAUDE")
        print(f"[--] Expected: FLAG_VECTORSIGN_{hash_esperado}")
        print(f"[--] Received: {flag_entregado}")
        print(f"[----------------------------------------------------]")
        sys.exit(1)

if __name__ == "__main__":
    main()