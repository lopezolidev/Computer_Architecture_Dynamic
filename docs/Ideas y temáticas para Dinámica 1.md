# Documento de Especificación Técnica: Dinámicas de Evaluación Corta (6 Horas)

 - **Asunto: Diseño Metodológico, Cobertura del Temario y Automatización de la Corrección contra el Uso de Modelos de Lenguaje**

## Introducción y Filosofía de Diseño

El presente documento expone la estructura de cinco dinámicas de corta duración (6 horas máximo) diseñadas para evaluar de forma crítica y rigurosa los conceptos basales de la asignatura. La premisa metodológica rompe con el esquema tradicional de evaluación basado en la escritura de código fuente en C (fácilmente delegable en herramientas de Inteligencia Artificial). En su lugar, se plantea un enfoque analítico basado en **cajas negras binarias precompiladas**.

El estudiante se enfrenta a problemas de optimización, ingeniería inversa y hacking binario operando directamente sobre flujos de control en lenguaje ensamblador y mutaciones de datos a nivel de bits. La resolución no exige redactar software extenso, sino descubrir constantes matemáticas exactas, alineaciones en la pila o banderas específicas del hardware. 

El diseño garantiza que las soluciones sean paramétricas y dependientes del identificador único del estudiante (C.I), lo que neutraliza la copia directa y permite una corrección e indexación de notas automatizada.

## Cobertura Curricular y Fundamentos Basales (Temas 1 y 2 de la Nota Informativa)

Las cinco dinámicas se sustentan estrictamente sobre los contenidos programáticos del temario provisto, concentrando su núcleo operativo en los elementos de los ítems 1 y 4, con soporte transversal del ítem 2 (Optimización de Rendimiento a Nivel de Programa):

- **Vínculo con el Ítem 1 (Representación y Manipulación de la Información):** Cada dinámica obliga al estudiante a procesar la información en su estado más primitivo. Se evalúa de manera práctica la notación hexadecimal, el ordenamiento a nivel de bytes (_Little Endian_), la aritmética en complemento a 2 (con sus anomalías de desbordamiento por signo y magnitud) y la descomposición bit a bit del estándar IEEE 754 de punto flotante.
    
- **Vínculo con el Ítem 4 (Arquitectura de Conjunto de Instrucciones - ISA):** Los retos exigen la lectura directa de acronimos x86-64, la comprensión analítica del contador de programa (`%rip`), el aislamiento de la tabla de símbolos y la manipulación forzada de los mecanismos de llamada a procedimientos mediante la administración del marco de pila (_Stack Frame_), punteros de pila (`%rsp`), referencias fuera de límite y desbordamientos de búfer (_Buffer Overflow_).
    

## Especificación Estructurada de las Temáticas

### Temática 1: Vector-Sign

- **Enfoque:** Desbordamiento de enteros para corromper la pila en x86-64.
    

#### Objetivo

Demostrar la vulnerabilidad lógica que surge cuando coexisten tipos de datos con signo y sin signo en la aritmética de la CPU, utilizándola para alterar el flujo de ejecución mediante la sobrescritura de la dirección de retorno en la pila.

#### Relación con la Nota Informativa

- **Ítem 1:** Sistemas numéricos posicionales, representación y aritmética de enteros en complemento a 2, y truncamiento por tamaño de datos (`int` vs. `size_t`).
    
- **Ítem 4:** Administración de la pila, referencias a memoria fuera de límite, desbordamiento de búfer y alteración de las instrucciones de flujo de control (llamada y retorno).
    

#### Estructura de la Temática

El estudiante recibe un binario que solicita un número entero $N$ que representa la cantidad de registros estructurados que desea almacenar en la pila. El binario ejecuta internamente una función de asignación de memoria local calculando el tamaño total requerido como:

$$\text{Tamaño} = N \times \text{sizeof(struct)}$$

El programa cuenta con un control de seguridad que verifica que $N$ no exceda un límite máximo estricto. Sin embargo, dicha validación condicional trata a $N$ como un entero con signo (`int`), mientras que la posterior instrucción de multiplicación en ensamblador (`imul`) e indexación de la pila trata el resultado como un valor sin signo (`size_t`/64 bits).

#### Aplicación Práctica (Ventana de 6 Horas)

El estudiante debe calcular un valor negativo exacto que evite la barrera condicional (`jge`), pero que al expandirse a 64 bits provoque un desbordamiento por envoltura (_integer wrap-around_). Esto resulta en una asignación real de memoria de apenas unos bytes, permitiendo que la posterior entrada de datos sobreescriba el puntero de instrucción `%rip`.

#### Mecanismo de Automatización de la Corrección

El binario está compilado con una clave criptográfica vinculada a la cédula del estudiante. Si la dirección de retorno es reescrita correctamente hacia la subrutina oculta, esta procesa el ID del alumno y escribe en la salida estándar un token único e irreversible de éxito (v.g., `FLAG_VECTORSIGN_XXXX`). La corrección se realiza mediante un script en el servidor de evaluación que compara el hash del token subido por el alumno con el valor esperado para su carnet.

### Temática 2: Ingeniería Inversa

#### Enfoque: 
Ingeniería inversa sobre código ensamblador compilado mediante el análisis de dependencias de datos, álgebra de Boole y flujos de control indirecto (_Jump Tables_).

#### Objetivo: 
Analizar y revertir la mutación de estado a nivel de registros inducida por transformaciones aritmético-lógicas iterativas (XOR, desplazamientos, aritmética de punteros con `leaq`), reconstruyendo la clave de entrada original requerida para satisfacer una condición de éxito oculta en el flujo del programa, sin el código fuente y apoyándose en depuradores dinámicos (GDB).

#### Relación con la Nota Informativa:

- **Ítem 1:** Almacenamiento de información, notación hexadecimal, ordenamiento de bytes (_Little-Endian_), aritmética en complemento a dos (inversos modulares), máscaras lógicas y operaciones a nivel de bits (XOR, desplazamientos lógicos/aritméticos).
    
- **Ítem 3 y 4:** Procesamiento a nivel de máquina, traducción de bucles en ensamblador (ej. _jump-to-middle_, _guarded-do_), cálculo de direcciones efectivas (`leaq`), y mecanismos de ramificación múltiple mediante tablas de salto (flujo de control indirecto).
    

#### Estructura de la Temática: 
Se le entrega al estudiante un esqueleto en C (`main.c`) y una "Caja Negra" en formato objeto reubicable precompilada (`caja_negra.o`). Al ejecutarse, la rutina de la caja negra recibe una clave simétrica de 8 bytes y entra en un ciclo donde el estado muta iterativamente alimentándose del resultado anterior, aplicando operaciones matemáticas y lógicas (`XOR`) contra un arreglo de datos de ofuscación ("La matriz"). El estado final de la mutación se enmascara para indexar un salto indirecto mediante una tabla de saltos. Si la clave es errónea, el índice conduce a una rutina de fallo; si es correcta, el código aterriza en el bloque de validación contra la firma matemática esperada.

#### Aplicación Práctica (Ventana de 6 Horas): 
El estudiante desensambla el archivo objeto y ejecuta `gdb` para inspeccionar el flujo de instrucciones y el segmento de memoria estática (`.rodata`). Tras identificar la estructura de la tabla de saltos y la dirección de la "Firma" objetivo en la memoria, el estudiante debe trazar la ejecución del bucle hacia atrás manualmente. Aplicando álgebra booleana (reversibilidad del XOR), reordenamiento por estructura _Little-Endian_, y calculando el inverso modular de la aritmética oculta en las instrucciones `leaq`, debe deducir de forma analítica la clave exacta de 64 bits que genera el estado final de éxito. La complejidad y la dependencia del estado hacen inviable la resolución por fuerza bruta o el uso simple de IA.

#### Mecanismo de Automatización de la Corrección:
Las matrices de ofuscación y las firmas objetivo inyectadas en la compilación de `caja_negra.o` son generadas dinámicamente mediante un script del cuerpo docente, siendo paramétricas y únicas en función de la C.I. del alumno. Cuando el estudiante deduce  su clave y ejecuta el binario final, el bloque de éxito en la caja negra se activa y retorna un token criptográfico (el hash del estudiante) al registro `%rax`. El programa `main.c` imprime esta cadena, la cual el programa de corrección evaluará para registrar una nota válida, inequívoca y libre de plagio.


### Temática 4: Asimetría de Signo

- **Enfoque:** Evasión de validaciones explotando saltos condicionales con/sin signo en la CPU.
    

#### Objetivo

Explotar la discrepancia estructural en la interpretación de los bits de resultado del registro de banderas de la CPU cuando un mismo patrón de bits es evaluado mediante instrucciones de salto condicional con signo frente a instrucciones sin signo.

#### Relación con la Nota Informativa

- **Ítem 1:** Representación de enteros (signo y magnitud vs. complemento a 2), bits de datos, y el bit de mayor peso (MSB) como indicador de signo.
    
- **Ítem 4:** Tipos de instrucciones de flujo de control (saltos condicionales basados en banderas: `ja` / `jg`, `jb` / `jl`), sintaxis en ensamblador y bits de resultado.
    

#### Estructura de la Temática

El sistema valida un identificador numérico a través de dos compuertas de seguridad consecutivas. El error radica en que el binario utiliza una instrucción de comparación sin signo (`cmpl` seguida de `ja`) para verificar el límite inferior, pero para el límite superior emplea una instrucción con signo (`jl`), manteniendo el mismo registro de origen.

#### Aplicación Práctica (Ventana de 6 Horas)

El alumno debe hallar un número hexadecimal cuyo bit más significativo sea 1 (número negativo en lógica con signo), pero cuyo valor absoluto interpretado sin signo sea numéricamente elevado. Al ingresar, por ejemplo, `0xFFFFFFFF`, la primera compuerta sin signo lo procesa como 4.294.967.295 (aprobando por ser mayor al límite inferior), mientras que la segunda compuerta con signo lo procesa como −1 (aprobando por ser menor al límite superior).

#### Mecanismo de Automatización de la Corrección

El entorno automatizado ejecuta el binario aislado pasándole el argumento del estudiante. Si la entrada logra que las dos instrucciones de salto mutuamente excluyentes den una respuesta positiva secuencial, el programa de corrección captura el estado de éxito y otorga la calificación.


## Matriz de Coherencia de Evaluaciones (Para el Cuerpo Docente)

| **Nombre de la Dinámica** | **Ítem Clave de la Nota Informativa**                | **Componente de Hardware Evaluado**                         | **Evidencia de Logro (Token de Entrega)**                          | **Estrategia Anti-IA**                                                                                           |
| ------------------------- | ---------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Vector-Sign**           | Ítem 1 (Aritmética Entera) / Ítem 4 (Pila)           | Marco de Pila de la CPU (`%rsp`, `%rbp`, `%rip`)            | Token dinámico generado por salto a función protegida.             | Requiere alineación exacta según el tamaño variable de una estructura aleatoria por alumno.                      |
| **Matriz Mutante**        | Ítem 1 (Máscaras de Bits) / Ítem 3 (Von Neumann)     | Registro de Instrucciones / Unidad de Decodificación        | Cadena descifrada ejecutable solo con la clave simétrica correcta. | Los LLM no procesan estados de memoria automodificables sin ejecución en tiempo de ejecución (_runtime_).        |
| **Anomalía-IEEE**         | Ítem 1 (Punto Flotante) / Ítem 4 (Flujo Excepcional) | Registros Vectoriales `XMM` y bandera de paridad `PF`       | Hash validado de entrada no numérica aceptada por la CPU.          | Las IA fallan crónicamente al predecir el impacto de un NaN sobre el registro estructural de banderas `%rflags`. |
| **Asimetría de Signo**    | Ítem 1 (Tipos de datos) / Ítem 4 (Saltos lógicos)    | Unidad de Control / Registro de Banderas (`SF`, `OF`, `CF`) | Entrada dual que satisface condicionales excluyentes.              | Requiza análisis empírico del código binario compilado; la IA asume lógica de alto nivel en C.                   |
| **Reloj-RDTSC**           | Ítem 2 (Rendimiento) / Ítem 4 (Interrupciones)       | Contador de Ciclos de Reloj de la Microarquitectura         | Clave dinámica extraída tras el bypass físico del binario.         | Requiere interacción viva en tiempo real con GDB y parcheo directo de bytes a nivel de OpCodes.                  |
