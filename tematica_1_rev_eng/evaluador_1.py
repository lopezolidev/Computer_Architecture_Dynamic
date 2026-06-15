import os
import csv
import re

def sanitizar_ci(ci_bruta):
    """
    Limpia la Cédula de Identidad eliminando puntos, espacios o prefijos (V-, E-).
    Garantiza un cruce relacional perfecto.
    """
    return re.sub(r'\D', '', str(ci_bruta))

def sanitizar_serial(serial_bruto):
    """
    Limpia el serial del estudiante: elimina espacios ocultos y fuerza mayúsculas.
    """
    return str(serial_bruto).strip().upper()

def ejecutar_auditoria(archivo_maestro, archivo_respuestas):
    """
    Compara las entregas de los estudiantes contra la matriz criptográfica del docente.
    """
    if not os.path.exists(archivo_maestro):
        print(f"[!] ERROR: No se encuentra la matriz del profesor '{archivo_maestro}'.")
        return

    if not os.path.exists(archivo_respuestas):
        print(f"[!] ERROR: No se encuentra el archivo de respuestas '{archivo_respuestas}'.")
        return

    # 1. Cargar la "Verdad Absoluta" en memoria (Diccionario Hash O(1))
    matriz_profesor = {}
    with open(archivo_maestro, 'r', encoding='utf-8') as f_maestro:
        lector_maestro = csv.DictReader(f_maestro)
        for fila in lector_maestro:
            ci_limpia = sanitizar_ci(fila['CI'])
            matriz_profesor[ci_limpia] = {
                'Nombre': fila['Nombre'],
                'Apellido': fila['Apellido'],
                'Serial_Esperado': fila['Serial_Esperado']
            }

    archivo_reporte = 'reporte_calificaciones_final.csv'
    
    # 2. Procesar entregas y generar el dictamen
    with open(archivo_respuestas, 'r', encoding='utf-8') as f_respuestas, \
         open(archivo_reporte, 'w', newline='', encoding='utf-8') as f_reporte:
        
        lector_respuestas = csv.DictReader(f_respuestas)
        escritor = csv.writer(f_reporte)
        
        # Cabecera del reporte de evaluación (Escala 0 a 20 pts - UCV)
        escritor.writerow(['CI', 'Estudiante', 'Serial_Entregado', 'Serial_Esperado', 'Veredicto', 'Calificacion_Pts'])
        
        print("=== INICIANDO AUDITORÍA DETERMINISTA DE SILICIO ===")
        
        for fila in lector_respuestas:
            # Asumimos que el formulario de Google tiene columnas 'CI' y 'Serial'
            ci_alumno = sanitizar_ci(fila.get('CI', ''))
            serial_alumno = sanitizar_serial(fila.get('Serial', ''))
            
            if ci_alumno not in matriz_profesor:
                print(f"[?] ALERTA: C.I. {ci_alumno} entregó, pero no está en la matriz original.")
                continue
                
            datos_maestro = matriz_profesor[ci_alumno]
            nombre_completo = f"{datos_maestro['Nombre']} {datos_maestro['Apellido']}"
            serial_esperado = datos_maestro['Serial_Esperado']
            
            # 3. La Comparación Arquitectónica
            if serial_alumno == serial_esperado:
                veredicto = "APROBADO - Alineación Perfecta"
                nota = 20
                print(f"[+] {ci_alumno} | {nombre_completo[:15]:<15} | ÉXITO (20 pts)")
            else:
                veredicto = "REPROBADO - Falla de Segmento Lógico"
                nota = 0
                print(f"[-] {ci_alumno} | {nombre_completo[:15]:<15} | FALLO (0 pts)")
                
            escritor.writerow([ci_alumno, nombre_completo, serial_alumno, serial_esperado, veredicto, nota])

    print(f"\n[+] Auditoría finalizada. Reporte generado: '{archivo_reporte}'")

if __name__ == "__main__":
    # Simulación rápida si no existe el archivo de respuestas (Ej: Descarga de Google Forms)
    if not os.path.exists("respuestas_alumnos.csv"):
        with open("respuestas_alumnos.csv", "w", encoding='utf-8') as f:
            f.write("Timestamp,CI,Serial\n")
            f.write("2026-06-14 18:00:00, 27.555.111, 16-00-CAFEBABE\n") # Ejemplo de Sergio con CI con puntos
            
    ejecutar_auditoria('matriz_correccion_profesor.csv', 'respuestas_alumnos.csv')