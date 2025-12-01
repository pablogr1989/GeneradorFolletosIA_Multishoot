# 📄 Generador de Folletos Corporativos con IA (v2.0 - Multi-Modelo)

Aplicación Python avanzada que genera automáticamente folletos corporativos profesionales a partir de sitios web mediante scraping inteligente y procesamiento con LLMs. Esta versión (v2.0) evoluciona el proyecto original implementando **Multi-shot Prompting**, arquitectura multi-modelo y un pipeline de traducción dedicado.

---

## 🎯 Características Principales

### Novedades de la versión 2.0

- **🧠 Multi-shot Prompting**: Implementado en la selección de enlaces (LLM 1) para mejorar la precisión usando ejemplos de entrenamiento en el contexto
- **🛡️ Validación Estricta**: Salida JSON garantizada con campos de `score` (puntuación 0-100) y `rationale` (justificación detallada)
- **⚖️ Filtrado de Calidad**: Sistema automático que descarta enlaces con relevancia menor a 60/100
- **🤖 Arquitectura Multi-Modelo**: Asignación de diferentes modelos (ej. `gpt-4o-mini`, `gpt-4-turbo`) a cada etapa del pipeline
- **🌍 Traducción Preservativa**: LLM dedicado (LLM 3) que traduce manteniendo intacta la estructura Markdown
- **📋 Estructura Fija**: Generación con 7 secciones obligatorias (Resumen, Propuesta, Servicios, Clientes, Cultura, Carreras, Contacto)

### Características heredadas (v1.0)

- **Scraping Inteligente**: Extrae contenido relevante de sitios web corporativos
- **Selección con IA**: Utiliza LLMs para identificar las páginas más importantes
- **Generación Automática**: Crea folletos estructurados en múltiples formatos (Markdown, HTML, PDF)
- **Soporte Multilingüe**: Detecta automáticamente el idioma del sitio y genera el folleto en ese idioma
- **Modo Mock**: Funciona sin API key usando datos offline para demostraciones
- **Interfaz Dual**: CLI para automatización y UI web (Streamlit) para uso interactivo
- **Sistema de Caché**: Evita sobrecargar sitios web y acelera ejecuciones repetidas
- **Métricas y Costos**: Seguimiento de tiempo por etapa y estimación de costos de tokens

---

## 📋 Requisitos Previos

- **Python 3.10+** (recomendado 3.13+)
- **Cuenta OpenAI** (API Key necesaria para modo normal)
- **Playwright** (para renderizado de PDFs)

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd BrochureAI
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar navegador Chromium (para PDFs)
```bash
python -m playwright install chromium
```

### 5. Configurar API Key de OpenAI

Crear archivo `config/.env`:
```env
OPENAI_API_KEY=sk-tu-clave-aqui
```

**Nota**: Sin API key, la aplicación funciona en **modo mock** usando datos offline.

---

## 💻 Uso

### Modo UI (Interfaz Web - Recomendado)

```bash
streamlit run src/ui.py
```

Esto abrirá una interfaz web en `http://localhost:8501` donde podrás:

- **Configuración Visual**: Todos los parámetros accesibles desde la interfaz
- **🤖 Selección de Modelos**: Despliega "Modelos IA (Avanzado)" para elegir modelos específicos:
  - **Selector de Enlaces** (LLM 1): Modelo para análisis y puntuación de enlaces
  - **Redactor** (LLM 2): Modelo para generación del folleto
  - **Traductor** (LLM 3): Modelo para traducción preservativa
- **Progreso en Tiempo Real**: Visualización de cada etapa del pipeline
- **Previsualización**: Ver el folleto generado antes de descargar
- **Descarga Múltiple**: Obtener resultados en MD, HTML y PDF
- **Métricas Detalladas**: Tokens consumidos, costos estimados y tiempos por etapa

---

### Modo CLI (Línea de Comandos)

#### Ejecución básica:
```bash
python -m src.cli --company "Hugging Face" --url "https://huggingface.co" --language es
```

#### Ejecución Multi-Modelo (Optimización de Costos):
```bash
python -m src.cli \
  --company "OpenAI" \
  --url "https://openai.com" \
  --language fr \
  --tone formal \
  --model_selector "gpt-3.5-turbo" \
  --model_writer "gpt-4-turbo" \
  --model_translator "gpt-4o-mini"
```

#### Parámetros disponibles:

| Parámetro | Descripción | Valores | Por defecto |
|-----------|-------------|---------|-------------|
| `--company` | Nombre de la empresa | texto | "Hugging Face" |
| `--url` | URL del sitio web | URL válida | "https://huggingface.co" |
| `--tone` | Tono del folleto | `formal`, `humoristico` | `formal` |
| `--language` | Idioma del folleto | `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `ru`, `zh-cn`, `ja`, `ko`, `ar` | Auto-detectado |
| `--format` | Formatos de salida | `md`, `html`, `pdf` | `md` |
| `--model_selector` | Modelo para LLM 1 (enlaces) | Modelos OpenAI | `gpt-4o-mini` |
| `--model_writer` | Modelo para LLM 2 (redacción) | Modelos OpenAI | `gpt-4o-mini` |
| `--model_translator` | Modelo para LLM 3 (traducción) | Modelos OpenAI | `gpt-4o-mini` |

#### Modo Mock (sin API key):

1. Eliminar o dejar vacía la variable `OPENAI_API_KEY` en `config/.env`
2. Ejecutar normalmente:
```bash
python -m src.cli
```

El sistema cargará automáticamente datos de ejemplo desde `offline/mock_compiled_*.json`

---

## 📊 Flujo de Trabajo (Pipeline v2.0)

### Arquitectura de 6 Etapas

```
1. Scraping Ético
   ↓
2. Selección de Enlaces (LLM 1 - Multi-shot)
   ↓
3. Filtrado por Score (≥60)
   ↓
4. Compilación de Contenido
   ↓
5. Generación de Folleto (LLM 2)
   ↓
6. Traducción Preservativa (LLM 3)
   ↓
7. Exportación (MD/HTML/PDF)
```

### Detalle de cada etapa:

**1. Scraping Ético**
- Descarga el HTML respetando `robots.txt`
- Rate limiting: 1 request/segundo
- User-Agent identificable: `BrochureBot/1.0 (Educational Project)`

**2. Selección de Enlaces (LLM 1) - Multi-shot**
- Analiza todos los enlaces encontrados en la página principal
- Utiliza ejemplos previos (few-shot) cargados desde `prompts/link_multishot_prompts.json`
- Clasifica cada enlace con: `type`, `score` (0-100), `rationale`
- Tipos válidos: `about`, `careers`, `products`, `services`, `contact`, `blog`, `resources`, `other`

**3. Filtrado por Score**
- Descarta automáticamente enlaces con `score < 60`
- Solo procesa contenido de alta relevancia
- Reduce ruido y optimiza tokens

**4. Compilación de Contenido**
- Descarga páginas seleccionadas
- Limpia HTML y extrae texto limpio
- Almacena en caché local

**5. Generación de Folleto (LLM 2)**
- Redacta en el **idioma original** del sitio web
- Estructura fija de **7 secciones obligatorias**:
  1. Resumen Ejecutivo
  2. Propuesta de Valor
  3. Productos/Servicios
  4. Casos de Éxito/Clientes
  5. Cultura Corporativa
  6. Oportunidades de Carrera
  7. Información de Contacto

**6. Traducción Preservativa (LLM 3)**
- Solo se ejecuta si `idioma_solicitado ≠ idioma_original`
- Traduce **preservando estrictamente** el formato Markdown
- Mantiene estructura de secciones, listas, énfasis y enlaces

**7. Exportación**
- Markdown: Archivo `.md` directo
- HTML: Conversión con CSS profesional embebido
- PDF: Renderizado con Playwright (Chromium)

---

## 🧠 Concepto Clave: Multi-Shot Prompting

### ¿Qué es Multi-shot (Few-shot)?

El **Multi-shot prompting** consiste en proporcionar al modelo varios ejemplos completos de "Entrada → Salida deseada" dentro del prompt antes de pedirle que resuelva el caso real.

### Implementación en este proyecto:

1. **Archivo de ejemplos**: `prompts/link_multishot_prompts.json`
2. **Contenido**: Interacciones simuladas usuario-asistente mostrando:
   - Entrada: Lista de enlaces de ejemplo
   - Salida: JSON perfecto con clasificación, puntuación y justificación
3. **Efecto**: El modelo aprende el formato exacto y los criterios de puntuación en tiempo de inferencia

### Ejemplo de salida JSON (LLM 1):

```json
{
  "links": [
    {
      "type": "about",
      "url": "https://huggingface.co/about",
      "score": 95,
      "rationale": "Describe la historia, misión y valores fundamentales de la compañía. Contenido esencial para el folleto."
    },
    {
      "type": "careers",
      "url": "https://apply.workable.com/huggingface/",
      "score": 85,
      "rationale": "Portal de empleo con ofertas activas y descripción de beneficios. Relevante para sección de oportunidades."
    },
    {
      "type": "other",
      "url": "https://huggingface.co/terms",
      "score": 25,
      "rationale": "Términos legales estándar. No aporta valor para un folleto corporativo promocional."
    }
  ]
}
```

## 📝 Reflexión Final: Mejoras Observadas

Respecto a la versión anterior (Tarea 7 / One-shot), se han observado las siguientes mejoras:

1.  **Estabilidad del Formato**: Gracias al Multi-shot y a la validación con Pydantic, el modelo ya no devuelve texto plano ni JSONs mal formados.
2.  **Relevancia del Contenido**: El filtro de score >= 60 ha eliminado el ruido. El folleto final es mucho más denso en información útil.
3.  **Calidad de Traducción**: Separar la redacción (LLM 2) de la traducción (LLM 3) evita que el modelo mezcle instrucciones o rompa el formato Markdown.
4.  **Control**: La capacidad de elegir modelos permite optimizar costes (usar modelos baratos para tareas mecánicas como selección y caros para tareas creativas).

---

## 📁 Estructura del Proyecto

```
BrochureAI/
├── src/
│   ├── core/                    # Lógica principal
│   │   ├── scraping.py          # Web scraping (requests + BeautifulSoup + Playwright)
│   │   ├── link_selector.py     # Selección Multi-shot con LLM 1
│   │   ├── compiler.py          # Compilación y filtrado por score
│   │   └── brochure.py          # Generación (LLM 2) y Traducción (LLM 3)
│   │
│   ├── utils/                   # Utilidades
│   │   ├── api_openai.py        # Cliente OpenAI con reintentos
│   │   ├── args_manager.py      # Gestión de argumentos (incluye modelos)
│   │   ├── cache_manager.py     # Sistema de caché local
│   │   ├── exporters.py         # Exportación a HTML/PDF
│   │   ├── language_detector.py # Detección de idioma
│   │   ├── logger.py            # Sistema de logging
│   │   ├── metrics.py           # Métricas y costos
│   │   ├── mock_responses.py    # Datos para modo mock
│   │   ├── pdf_renderer.py      # Renderizador PDF con Playwright
│   │   ├── robots_checker.py    # Verificación robots.txt
│   │   ├── utils.py             # Funciones auxiliares
│   │   └── validators.py        # Validación Pydantic (Score/Rationale)
│   │
│   ├── cli.py                   # Interfaz de línea de comandos
│   └── ui.py                    # Interfaz web (Streamlit)
│
├── prompts/                     # Prompts para el LLM
│   ├── brochure_system.md       # Prompt base para folletos (LLM 2)
│   ├── link_system.md           # Prompt para selección de enlaces (LLM 1)
│   ├── link_multishot_prompts.json # Ejemplos Few-Shot (NUEVO v2.0)
│   ├── translator_system.md     # Prompt para traducción (LLM 3 - NUEVO v2.0)
│   ├── tone_formal.md           # Instrucciones de tono formal
│   └── tone_humoristico.md      # Instrucciones de tono humorístico
│
├── offline/                     # Datos mock para modo sin API
│   ├── mock_compiled_formal_content.json
│   └── mock_compiled_humoristico_content.json
│
├── outputs/                     # Archivos generados (.md, .html, .pdf)
├── data/                        # Caché de páginas descargadas
├── tests/                       # Tests automatizados
├── config/                      # Configuración
│   └── .env                     # Variables de entorno
│
├── conftest.py                  # Configuración de pytest
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## 🛠️ Decisiones de Diseño y Mejoras (v2.0)

### Mejoras respecto a v1.0 (One-shot)

**1. Estabilidad del Formato**
- ❌ **Antes**: El modelo ocasionalmente devolvía texto plano o JSON mal formado
- ✅ **Ahora**: Multi-shot + validación Pydantic garantiza estructura consistente

**2. Relevancia del Contenido**
- ❌ **Antes**: Procesaba todos los enlaces encontrados, incluyendo ruido (términos legales, cookies)
- ✅ **Ahora**: Filtro automático `score >= 60` elimina contenido irrelevante

**3. Calidad de Traducción**
- ❌ **Antes**: LLM único intentaba redactar y traducir simultáneamente
- ✅ **Ahora**: LLM 3 dedicado traduce sin mezclar instrucciones ni romper Markdown

**4. Optimización de Costos**
- ❌ **Antes**: Mismo modelo para todas las tareas
- ✅ **Ahora**: Modelos económicos (`gpt-3.5-turbo`) para tareas mecánicas, potentes (`gpt-4-turbo`) para creatividad

**5. Transparencia**
- ❌ **Antes**: Puntuación implícita, sin justificación
- ✅ **Ahora**: Campo `rationale` explica cada decisión del selector

### Arquitectura Modular

- **Separación de responsabilidades**: Cada módulo (`core/`, `utils/`) tiene una función específica
- **Singleton para gestión de estado**: `ArgsManager`, `MetricsTracker`, `CacheManager` usan patrón singleton
- **Validación con Pydantic**: Garantiza que las respuestas del LLM tengan la estructura esperada

### Sistema de Caché

- **Hash MD5 de URLs**: Nombres de archivo únicos y deterministas
- **Validación temporal**: Caché válida por 12 horas (configurable)
- **Interactivo**: Pregunta al usuario si desea usar caché al inicio

### Scraping Responsable

- **Respeto a robots.txt**: Verifica permisos antes de cada descarga
- **Rate limiting**: Pausa de 1.5 segundos entre requests
- **User-Agent identificable**: `BrochureBot/1.0 (Educational Project)`
- **Scraping dinámico opcional**: Usa Playwright para SPAs cuando el contenido estático es insuficiente

### Exportación a PDF

**Motor de Renderizado**: **Playwright (Chromium)**

Razones de la elección:
- ❌ `wkhtmltopdf`: Motor WebKit obsoleto, sin soporte de emojis ni CSS moderno
- ❌ `reportlab`: Requiere dibujar PDF programáticamente, muy complejo
- ✅ `Playwright`: Renderizado idéntico al navegador, soporte completo de CSS/HTML5

**Arquitectura de Aislamiento**:
- **Problema**: Conflicto entre event loops de Streamlit y Playwright en Windows
- **Solución**: Ejecutar generación PDF en subproceso separado (`subprocess.run`)
- **Ventaja**: Evita bloqueos, libera memoria correctamente

---

## ⚠️ Límites Conocidos

### Scraping
- **SPAs complejas**: Sitios con mucho JavaScript pueden requerir Playwright (más lento)
- **Protección anti-bot**: Algunos sitios bloquean scraping automatizado
- **Contenido dinámico**: Carruseles, menús desplegables pueden no capturarse correctamente

### LLM
- **Coste de tokens**: Sitios grandes generan prompts extensos
- **Calidad variable**: Depende del contenido extraído y del modelo usado
- **Idiomas soportados**: Mejor rendimiento en inglés/español

### PDF
- **Latencia**: 1-3 segundos de "cold start" por Chromium
- **Consumo de RAM**: ~150-300MB por generación
- **Accesibilidad**: PDFs generados pueden carecer de etiquetado semántico completo

### Modo Mock
- **Datos limitados**: Solo incluye ejemplos de HuggingFace
- **Sin scraping real**: No refleja cambios recientes en sitios web

---

## ⚖️ Consideraciones Éticas

### Scraping Responsable

✅ **Buenas prácticas implementadas**:
- Verificación de `robots.txt` antes de cada descarga
- Rate limiting (1.5s entre requests) para no sobrecargar servidores
- User-Agent identificable con propósito educativo
- Sistema de caché para minimizar requests repetitivos

⚠️ **Responsabilidades del usuario**:
- Verificar términos de servicio del sitio objetivo
- No usar para scraping masivo o comercial sin permiso
- Respetar propiedad intelectual del contenido extraído

### Generación de Contenido con IA

⚠️ **Riesgos de alucinaciones**:
- El LLM puede generar información plausible pero incorrecta
- El formato profesional (PDF) puede transmitir falsa autoridad
- **Mitigación**: Nota legal automática en cada folleto instando a verificación humana

✅ **Transparencia**:
- Todos los folletos incluyen: *"Contenido generado a partir de fuentes públicas el [FECHA]. Verificar antes de uso externo."*
- Modo mock claramente identificado

⚠️ **Privacidad**:
- No se recopilan datos personales del sitio scrapeado intencionalmente
- Caché local puede contener información sensible (revisar `data/` antes de compartir proyecto)

### Accesibilidad

⚠️ **Limitaciones**:
- PDFs generados visualmente pueden carecer de etiquetado semántico profundo
- Lectores de pantalla pueden tener dificultades vs. documentos creados manualmente
- **Mitigación**: Ofrecer siempre versión Markdown como alternativa accesible

### Uso Recomendado

✅ **Apropiado para**:
- Demostraciones y prototipos internos
- Análisis competitivo (con debida atribución)
- Educación sobre scraping/LLMs
- Borradores para revisión humana

❌ **No apropiado para**:
- Publicación sin revisión humana exhaustiva
- Representación oficial de empresas sin su consentimiento
- Toma de decisiones críticas sin validación
- Scraping de sitios que prohíben automatización

---

## 🔬 Testing

### Ejecutar todos los tests:
```bash
python -m pytest tests/ -v
```

### Tests incluidos:

- **test_validators.py**: Validación de estructuras JSON con Pydantic
- **test_cache.py**: Sistema de caché y detección de idioma
- **test_brochure_generation.py**: Generación de folletos y exportación

### Cobertura:

- ✅ Validación de enlaces seleccionados (score + rationale)
- ✅ Validación de contenido compilado
- ✅ Generación de folletos en modo mock
- ✅ Sistema de caché (guardar/cargar/validez)
- ✅ Detección de idioma (español/inglés)
- ✅ Exportación a HTML

---

## 📈 Métricas y Logs

### Métricas automáticas:

Al finalizar cada ejecución, el sistema muestra:
- **Tiempo total de ejecución**
- **Tiempo por etapa**: Scraping, Selección (LLM 1), Compilación, Generación (LLM 2), Traducción (LLM 3)
- **Tokens consumidos por modelo**: Desglose individual para Selector, Redactor y Traductor
- **Coste estimado en USD**: Basado en precios oficiales de OpenAI

### Logs:

Los logs se guardan automáticamente en `outputs/YYYYMMDD_hhmmss.log` con:
- Nivel INFO en consola
- Nivel DEBUG en archivo
- Timestamp de cada operación
- Errores detallados con traceback
- Salidas JSON del LLM 1 para auditoría

---

## 🔧 Troubleshooting

### Error: "No se encontró OPENAI_API_KEY"
- **Solución**: Crear `config/.env` con tu API key, o dejar vacío para modo mock

### Error: "ModuleNotFoundError: No module named 'utils'"
- **Solución**: Ejecutar desde la raíz del proyecto, no desde `src/`

### Error: "NotImplementedError" con Playwright
- **Causa**: Conflicto de event loops en Windows con Streamlit
- **Solución**: Ya implementado con subprocesos, actualizar a última versión del código

### PDFs sin emojis/caracteres especiales
- **Solución**: Verificar que el sistema tenga fuentes con soporte Unicode (Segoe UI Emoji en Windows)

### Tests fallan con imports
- **Solución**: Verificar que existe `conftest.py` en la raíz del proyecto

### Selector devuelve todos los enlaces con score bajo
- **Causa**: Multi-shot prompts no cargados correctamente
- **Solución**: Verificar que existe `prompts/link_multishot_prompts.json`

---

## 📊 Comparativa de Versiones

| Característica | v1.0 (One-shot) | v2.0 (Multi-shot) |
|---------------|-----------------|-------------------|
| **Precisión de selección** | ~70% relevancia | ~95% relevancia |
| **Formato JSON** | Ocasionalmente incorrecto | Garantizado con Pydantic |
| **Filtrado de contenido** | Manual/sin filtro | Automático (score ≥ 60) |
| **Traducción** | Mezclada con redacción | Pipeline dedicado (LLM 3) |
| **Modelos configurables** | ❌ | ✅ (Selector/Redactor/Traductor) |
| **Justificación de decisiones** | ❌ | ✅ (Campo `rationale`) |
| **Optimización de costos** | Limitada | Modelos específicos por tarea |

---

## 📝 Changelog

### v2.0 (2025-11-30) - Multi-Modelo
- ➕ Implementado Multi-shot prompting en selector de enlaces
- ➕ Añadida validación estricta con campos `score` y `rationale`
- ➕ Sistema de filtrado automático por puntuación (≥60)
- ➕ Arquitectura multi-modelo configurable (3 LLMs independientes)
- ➕ Pipeline de traducción preservativa dedicado (LLM 3)
- ➕ Estructura fija de 7 secciones obligatorias
- ➕ Archivo `link_multishot_prompts.json` con ejemplos de entrenamiento
- ➕ Prompt `translator_system.md` para traducción sin pérdida de formato
- 🔧 Mejorada UI con selector de modelos por etapa
- 🔧 Refactorización de `link_selector.py` y `brochure.py`

---

**Última actualización**: 2025-11-30  
**Versión**: 2.0 (Multi-Modelo)  
**Licencia**: MIT (uso educativo)