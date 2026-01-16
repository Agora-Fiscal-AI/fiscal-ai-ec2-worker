# Pipeline de Estructuración de Documentos Normativos (Resumen Técnico)

## Objetivo
Transformar un documento PDF jurídico (o normativo) en una **estructura jerárquica trazable**, donde cada unidad normativa (título, capítulo, artículo, fracción, inciso, etc.) queda:
- correctamente identificada,
- posicionada en el texto original,
- y asociada a su contenido completo.

El pipeline está diseñado para **documentos estructurados jerárquicamente**, siendo las leyes el caso más exigente.

---

## Visión General del Flujo

PDF  
→ Texto plano preservando líneas  
→ Documento lógico indexado  
→ Detección de niveles estructurales  
→ Construcción de árbol normativo  
→ Asignación de contenido por rango  
→ Estructura final navegable y auditable

---

## 1. Extracción del Texto (PDF → Líneas)

**Propósito:**  
Obtener texto legible manteniendo el orden y la separación por líneas, sin interpretar semántica.

**Resultado clave:**
- Texto plano dividido en líneas coherentes
- Orden estable (la posición de cada línea es significativa)
- Eliminación básica de ruido (headers)

**Salida:**  
Un bloque de texto multilínea.

---

## 2. Normalización en Documento Lógico

**Propósito:**  
Convertir el texto crudo en un objeto documental indexado.

**Concepto central:**
- La **línea** es la unidad absoluta de referencia.

**Resultado clave:**
- Cada línea tiene un índice único
- Se preserva el orden original
- Este índice será usado en todo el pipeline

**Salida:**  
Documento lógico con acceso directo por número de línea.

---

## 3. Configuración Estructural (YAML)

**Propósito:**  
Definir la semántica del documento **fuera del código**.

**Qué se define aquí:**
- Tipos de niveles (título, artículo, fracción, etc.)
- Formas de numeración válidas
- Jerarquía permitida entre niveles
- Niveles opcionales o implícitos

**Resultado clave:**
- El sistema se adapta a distintos tipos de documentos
- Cambios estructurales no requieren modificar el motor

---

## 4. Detección de Niveles Estructurales

**Propósito:**  
Identificar dónde inicia cada unidad normativa en el texto.

**Cómo funciona (conceptual):**
- Se analiza cada línea del documento
- Se prueba contra reglas declaradas en la configuración
- Cuando una línea coincide, se marca como inicio de un nivel

**Resultado clave:**
- Lista ordenada de candidatos estructurales
- Cada candidato conoce su tipo y su línea de inicio

**Salida:**  
Eventos de detección estructural con referencia exacta al texto.

---

## 5. Construcción del Árbol Normativo

**Propósito:**  
Organizar los niveles detectados en una jerarquía coherente.

**Concepto central:**
- La jerarquía no se infiere: se **valida** según reglas formales.

**Resultado clave:**
- Árbol con nodos padre–hijo
- Cada nodo representa una unidad normativa
- Se conserva el orden relativo y la posición en el documento

**Salida:**  
Estructura jerárquica navegable del documento.

---

## 6. Indexación por Línea

**Propósito:**  
Conectar la estructura con el texto real.

**Cómo se logra:**
- Cada nodo guarda la línea donde inicia
- Se construye un índice línea → nodo

**Resultado clave:**
- Trazabilidad total entre texto y estructura

---

## 7. Asignación de Contenido (Binding)

**Propósito:**  
Asignar el contenido textual a cada unidad normativa.

**Lógica conceptual:**
- Desde la línea de inicio de un nodo
- Hasta antes del inicio del siguiente nodo
- El texto intermedio se considera su contenido

**Resultado clave:**
- Cada nodo contiene su texto completo
- El encabezado y el cuerpo quedan separados

---

## 8. Resultado Final

**Salida del pipeline:**
- Árbol normativo completo
- Cada nodo tiene:
  - tipo estructural
  - numeración
  - posición exacta en el documento
  - contenido normativo asociado

**Propiedades del resultado:**
- Trazable
- Auditable
- Explicable
- Apto para análisis, indexación, IA o compliance

---

## Enfoque del Sistema

- No interpreta significado jurídico
- No usa NLP
- No “adivina” estructura

Se limita a **hacer visible la estructura formal del documento**, que luego puede ser explotada por capas analíticas superiores.

---
