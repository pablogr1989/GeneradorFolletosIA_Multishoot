# 📄 Generador de Folletos Corporativos con IA

Aplicación Python que genera automáticamente folletos corporativos profesionales a partir de sitios web mediante scraping inteligente y procesamiento con LLMs (Large Language Models).

---

## 🎯 Características Principales

- **Scraping Inteligente**: Extrae contenido relevante de sitios web corporativos
- **Selección con IA**: Utiliza LLMs para identificar las páginas más importantes (About, Careers, Products, etc.)
- **Generación Automática**: Crea folletos estructurados en múltiples formatos (Markdown, HTML, PDF)
- **Soporte Multilingüe**: Detecta automáticamente el idioma del sitio y genera el folleto en ese idioma
- **Modo Mock**: Funciona sin API key usando datos offline para demostraciones
- **Interfaz Dual**: CLI para automatización y UI web (Streamlit) para uso interactivo
- **Sistema de Caché**: Evita sobrecargar sitios web y acelera ejecuciones repetidas
- **Métricas y Costos**: Seguimiento de tiempo por etapa y estimación de costos de tokens

---

## 📋 Requisitos Previos

- **Python 3.13+**
- **Cuenta OpenAI** (opcional, para modo normal)
- **Playwright** (para generación de PDFs)

---

## 🚀 Instalación

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
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

### 5. Configurar API Key de OpenAI (opcional)

Crear archivo `config/.env`:
```env
OPENAI_API_KEY=sk-tu-clave-aqui
```

**Nota**: Sin API key, la aplicación funciona en **modo mock** usando datos offline.

---

## 💻 Uso

### Modo CLI (Línea de Comandos)

#### Ejecución básica (modo normal con API key):
```bash
python -m src.cli
```

#### Con parámetros personalizados:
```bash
python -m src.cli --company "OpenAI" --url "https://openai.com" --tone humoristico --language es --format md html pdf
```

#### Parámetros disponibles:

| Parámetro | Descripción | Valores | Por defecto |
|-----------|-------------|---------|-------------|
| `--company` | Nombre de la empresa | texto | "Hugging Face" |
| `--url` | URL del sitio web | URL válida | "https://huggingface.co" |
| `--tone` | Tono del folleto | `formal`, `humoristico` | `formal` |
| `--language` | Idioma del folleto | `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `ru`, `zh-cn`, `ja`, `ko`, `ar` | Detectado automáticamente |
| `--format` | Formatos de salida | `md`, `html`, `pdf` | `md` |

#### Modo Mock (sin API key):

1. Eliminar o dejar vacía la variable `OPENAI_API_KEY` en `config/.env`
2. Ejecutar normalmente:
```bash
python -m src.cli
```

El sistema cargará automáticamente datos de ejemplo desde `offline/mock_compiled_*.json`

---

### Modo UI (Interfaz Web con Streamlit)
```bash
python -m streamlit run src/ui.py
```

Esto abrirá una interfaz web en `http://localhost:8501` donde podrás:
- Configurar todos los parámetros visualmente
- Ver progreso en tiempo real
- Previsualizar el folleto generado
- Descargar resultados en múltiples formatos
- Ver métricas de rendimiento

---

## 📁 Estructura del Proyecto
```
BrochureAI/
├── src/
│   ├── core/                    # Lógica principal
│   │   ├── scraping.py          # Web scraping (requests + BeautifulSoup + Playwright)
│   │   ├── link_selector.py     # Selección de enlaces con LLM
│   │   ├── compiler.py          # Compilación de contenido
│   │   └── brochure.py          # Generación del folleto
│   │
│   ├── utils/                   # Utilidades
│   │   ├── api_openai.py        # Cliente OpenAI
│   │   ├── args_manager.py      # Gestión de argumentos CLI
│   │   ├── cache_manager.py     # Sistema de caché local
│   │   ├── exporters.py         # Exportación a HTML/PDF
│   │   ├── language_detector.py # Detección de idioma
│   │   ├── logger.py            # Sistema de logging
│   │   ├── metrics.py           # Métricas y costos
│   │   ├── mock_responses.py    # Datos para modo mock
│   │   ├── pdf_renderer.py      # Renderizador PDF con Playwright
│   │   ├── robots_checker.py    # Verificación robots.txt
│   │   ├── utils.py             # Funciones auxiliares
│   │   └── validators.py        # Validación con Pydantic
│   │
│   ├── cli.py                   # Interfaz de línea de comandos
│   └── ui.py                    # Interfaz web (Streamlit)
│
├── prompts/                     # Prompts para el LLM
│   ├── brochure_system.md       # Prompt base para folletos
│   ├── link_system.md           # Prompt para selección de enlaces
│   ├── tone_formal.md           # Instrucciones de tono formal
│   └── tone_humoristico.md      # Instrucciones de tono humorístico
│
├── offline/                     # Datos mock para modo sin API
│   ├── mock_compiled_formal_content.json
│   └── mock_compiled_humoristico_content.json
│
├── outputs/                     # Archivos generados
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

## 🔄 Flujo de Trabajo

### Modo Normal (con API key):

1. **Scraping**: Descarga la página principal del sitio web
2. **Extracción**: Limpia HTML y extrae todos los enlaces
3. **Selección con IA**: El LLM identifica enlaces relevantes (About, Careers, Products, etc.)
4. **Compilación**: Descarga y procesa el contenido de cada página seleccionada
5. **Generación**: El LLM crea un folleto estructurado en el idioma detectado
6. **Exportación**: Guarda en los formatos solicitados (MD/HTML/PDF)

### Modo Mock (sin API key):

1. Carga contenido precompilado desde `offline/`
2. Genera folleto usando plantillas predefinidas
3. Exporta en los formatos solicitados

---

## 🛠️ Decisiones de Diseño y Límites Conocidos

### Arquitectura Modular

- **Separación de responsabilidades**: Cada módulo (`core/`, `utils/`) tiene una función específica
- **Singleton para gestión de estado**: `ArgsManager`, `MetricsTracker`, `CacheManager` usan patrón singleton para compartir estado global
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

**Motor de Renderizado**: Se eligió **Playwright (Chromium)** sobre alternativas como:
- ❌ `wkhtmltopdf`: Motor WebKit obsoleto, sin soporte de emojis ni CSS moderno
- ❌ `reportlab`: Requiere dibujar PDF programáticamente, muy complejo
- ✅ `Playwright`: Renderizado idéntico al navegador, soporte completo de CSS/HTML5

**Arquitectura de Aislamiento de Procesos**:
- Problema: Conflicto entre event loops de Streamlit y Playwright en Windows
- Solución: Ejecutar generación PDF en subproceso separado (`subprocess.run`)
- Ventaja: Evita bloqueos, libera memoria correctamente

**Pipeline**: Markdown → HTML (con CSS) → PDF

### Límites Conocidos

#### Scraping
- **SPAs complejas**: Sitios con mucho JavaScript pueden requerir Playwright (más lento)
- **Protección anti-bot**: Algunos sitios bloquean scraping automatizado
- **Contenido dinámico**: Carruseles, menús desplegables pueden no capturarse correctamente

#### LLM
- **Coste de tokens**: Sitios grandes generan prompts extensos
- **Calidad variable**: Depende del contenido extraído y del modelo usado
- **Idiomas soportados**: Mejor rendimiento en inglés/español

#### PDF
- **Latencia**: 1-3 segundos de "cold start" por Chromium
- **Consumo de RAM**: ~150-300MB por generación
- **Accesibilidad**: PDFs generados pueden carecer de etiquetado semántico completo

#### Modo Mock
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

## 📊 Testing

### Ejecutar todos los tests:
```bash
python -m pytest tests/ -v
```

### Tests incluidos:

- **test_validators.py**: Validación de estructuras JSON
- **test_cache.py**: Sistema de caché y detección de idioma
- **test_brochure_generation.py**: Generación de folletos y exportación

### Cobertura:

- ✅ Validación de enlaces seleccionados
- ✅ Validación de contenido compilado
- ✅ Generación de folletos en modo mock
- ✅ Sistema de caché (guardar/cargar/validez)
- ✅ Detección de idioma (español/inglés)
- ✅ Exportación a HTML

---

## 📈 Métricas y Logs

### Métricas automáticas:

Al finalizar cada ejecución, el sistema muestra:
- Tiempo total de ejecución
- Tiempo por etapa (scraping, selección, compilación, generación)
- Tokens totales consumidos
- Coste estimado en USD

### Logs:

Los logs se guardan automáticamente en `outputs/brochure_YYYYMMDD.log` con:
- Nivel INFO en consola
- Nivel DEBUG en archivo
- Timestamp de cada operación
- Errores detallados con traceback

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

---

**Última actualización**: 2025-11-27