---
name: ISYN
description: CRM de prospección de compradores para ISYN — Internacional de Subastas y Negocios
colors:
  isyn-azul: "#046cb3"
  isyn-marino: "#014b72"
  isyn-azul-soft: "#dcebf5"
  isyn-azul-faint: "#eff6fb"
  esmeralda-ganada: "#10b981"
  esmeralda-ganada-deep: "#065f46"
  esmeralda-ganada-soft: "#d1fae5"
  side-bg-top: "#faf3e6"
  side-bg-bottom: "#f1e2c8"
  side-ink: "#35281b"
  side-ink-soft: "#6b5643"
  side-border: "#e7d7b8"
  side-accent: "#b54a26"
  side-accent-deep: "#8f3a1d"
  side-accent-soft: "#f0d7bd"
  ink-900: "#1a1a1a"
  text-primary: "#262626"
  text-secondary: "#595959"
  text-muted: "#737373"
  text-faint: "#a3a3a3"
  border: "#e5e5e5"
  surface-sunken: "#f2f2f2"
  canvas: "#fafafa"
  surface: "#ffffff"
  danger: "#ef4444"
  danger-soft: "#fee2e2"
typography:
  metric-value:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.7rem"
    fontWeight: 700
    letterSpacing: "-0.01em"
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  sidebar-brand:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.02rem"
    fontWeight: 700
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.925rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  table-data:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
  button:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 600
  subtitle:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 400
  button-sm:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 600
  stage-label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 650
  filter-label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.76rem"
    fontWeight: 650
    letterSpacing: "0.03em"
  tag:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 650
  table-header:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 700
    letterSpacing: "0.04em"
rounded:
  sm: "10px"
  md: "14px"
  pill: "999px"
spacing:
  xs: "0.35rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1.25rem"
  xl: "1.75rem"
components:
  button-primary:
    backgroundColor: "{colors.isyn-azul}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  button-primary-hover:
    backgroundColor: "{colors.isyn-marino}"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.sm}"
  icon-button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.sm}"
    size: "32px"
  icon-button-mail-hover:
    backgroundColor: "{colors.isyn-azul-faint}"
    textColor: "{colors.isyn-marino}"
  icon-button-chat-hover:
    backgroundColor: "{colors.esmeralda-ganada-soft}"
    textColor: "{colors.esmeralda-ganada-deep}"
  tag-neutral:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.pill}"
  input-text:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "0.5rem 0.75rem"
---

# Design System: ISYN

## Overview

**Creative North Star: "El Tablero de Despacho"**

Este CRM se piensa como el tablero de una oficina de despacho — de subastas, licitaciones y negocios internacionales: nada decorativo, cada marca en el tablero significa algo concreto, y quien lo opera es una persona de ventas o comercio exterior, no un diseñador — nunca debe detenerse a interpretar qué significa un color. La información se organiza por **intensidad de una sola tonalidad**, no por un código de colores que hay que memorizar.

El sistema usa como único acento el **azul de ISYN**, sacado directamente del logo real de la marca — para todo lo que es progreso o acción. El resto es una escala neutra de grises, también tomada del gris del logo. La única excepción ganada es el esmeralda, reservado estrictamente para el momento en que algo se cierra a favor: un comprador que llega a "Cliente", el canal de WhatsApp (el camino más directo hacia ese cierre). No hay una tercera familia de color por decoración; cuando algo no es progreso ni un cierre ganado, es neutro.

Confirmado explícitamente por el usuario: el carácter del **área de trabajo** (tabla, formularios, paneles — todo lo que vive a la derecha del sidebar) es **preciso y sin fricción**, no cálido — cada elemento existe para que una persona encuentre y contacte un prospecto más rápido, no para transmitir cercanía a través de la forma. La densidad de la tabla, la escala tipográfica ajustada, y la ausencia de decoración son deliberadas. Este carácter se mantuvo al adoptar la marca de ISYN — no se reblandeció el sistema para "verse más cálido" solo porque cambió la paleta.

**Pivote confirmado (sidebar):** en una sesión posterior el usuario pidió explícitamente que el sidebar dejara de sentirse "genérico" y se volviera cálido, minimalista y llamativo. Esto es un cambio de dirección real, no un descuido — ver la Regla del Rincón Cálido más abajo. El sidebar es ahora la única superficie del sistema con su propia paleta e identidad cromática, deliberadamente distinta del azul funcional del área de trabajo; el resto del carácter "preciso y sin fricción" descrito arriba sigue intacto en todo lo demás.

**Modo oscuro confirmado:** el usuario pidió un interruptor de tema explícito ("un botón para cambiar de tema claro a oscuro... el tema también afecta al navbar") — no un simple `prefers-color-scheme`. La app entera responde, incluido el sidebar cálido con su propia variante oscura (ver Colors → Tema oscuro). El login (`.auth-shell`/`.auth-card`) queda deliberadamente fuera — sigue el mismo "primer momento de marca" fijo de la Regla del Resplandor de Marca, sin importar el tema elegido en el resto de la app.

**Rebrand confirmado:** el cliente real de este proyecto es **ISYN (Internacional de Subastas y Negocios)**, una empresa panameña de subastas, licitaciones y negocios internacionales (isynsubastas.com). El producto llevaba antes el nombre provisional "CenterComp"; ese nombre queda retirado de toda superficie visible. El sistema de diseño construido bajo ese nombre (medidor de etapa, fila de contacto, regla de la sombra única, etc.) se conservó íntegro — solo se re-coloreó con la paleta real de ISYN, extraída por muestreo directo del archivo de logo entregado por el cliente.

**Key Characteristics:**
- Un solo acento de color (Azul ISYN) para toda acción/progreso en el área de trabajo; el esmeralda es una excepción con significado, no un color más. El sidebar vive aparte, en su propio mundo cálido (terracota) — ver Regla del Rincón Cálido
- Escala neutra tomada del gris real del logo de ISYN, que hace la mayor parte del trabajo visual
- Iconografía dibujada en trazo consistente, nunca emoji
- Densidad alta a propósito — la tabla es el producto, no un elemento decorativo alrededor de ella
- Tipografía única (Inter) en todo el sistema; sin par display/body
- El logo de marca es un asset real del cliente (`static/img/isyn-logo.png`), nunca un ícono inventado o un logotipo aproximado

## Colors

La paleta viene directamente del logo de ISYN — no fue inventada ni elegida por gusto. Se sampleó por color exacto de píxel del archivo entregado por el cliente.

### Primary
- **Azul ISYN** (`#046cb3`): el único acento del sistema, sacado del listón azul del logo. Botones primarios, enlaces, foco de campos, y el relleno del medidor de etapa mientras un prospecto avanza (por contactar → contactado → interesado). Aparece en degradado hacia tonos más suaves (`#6ba9d6`, `#b8d6ec`, `#dcebf5`, `#eff6fb`) para fondos con poco peso visual — nunca para transmitir estados distintos, solo intensidad.
- **Marino ISYN** (`#014b72`): sacado del listón inferior (globo) del logo. Estado hover/activo del acento primario, y el segundo tono del resplandor de marca.

### Secondary
- **Esmeralda Ganada** (`#10b981`): reservado, sin excepción, para lo que ya se ganó — el estado "Cliente" al 100% del medidor de etapa, y el canal de WhatsApp (el atajo más directo a ese cierre). No es un color de ISYN; es una excepción funcional universal (éxito/dinero) que se mantiene aparte de la identidad de marca a propósito — ver la Regla de la Excepción Única.
- **Esmeralda Ganada Profundo** (`#065f46`): texto sobre fondos esmeralda claros (tags, hover de botón de WhatsApp).

### Sidebar (mundo cálido — ver Regla del Rincón Cálido)
Paleta propia, aparte de la marca ISYN, usada exclusivamente dentro del sidebar. No aparece en ningún otro lugar del sistema.
- **Fondo** (`#faf3e6` → `#f1e2c8`): degradado vertical muy sutil, arena/lino cálido — reemplaza el sidebar oscuro original.
- **Terracota** (`#b54a26`, hover/profundo `#8f3a1d`): único acento del sidebar. Enlace de navegación activo (relleno sólido, texto blanco).
- **Terracota suave** (`#f0d7bd`): fondo de hover en enlaces inactivos.
- **Tinta cálida** (`#35281b`): texto de los enlaces de navegación y el nombre de usuario — un café oscuro, no un gris neutro, para que el texto pertenezca a la misma familia de color que el fondo.
- **Tinta cálida suave** (`#6b5643`): pie del sidebar (usuario, botón de cerrar sesión).
- **Borde cálido** (`#e7d7b8`): línea divisoria bajo el logo y sobre el pie del sidebar.

### Neutral
- **Ink 900** (`#1a1a1a`): fondo del login (`.auth-shell`), texto de mayor peso en el área de trabajo.
- **Texto Primario** (`#262626`): color de texto base del cuerpo.
- **Texto Secundario** (`#595959`): el gris exacto del logo de ISYN. Enlaces del embudo, botones secundarios.
- **Texto Apagado** (`#737373`): metadatos, subtítulos, columnas de contexto (país, fuente).
- **Texto Tenue** (`#a3a3a3`): el estado "Descartado" (sale de la escala de progreso, se apaga), marcadores internacionales.
- **Borde** (`#e5e5e5`): bordes de tarjetas, tabla, campos.
- **Superficie Hundida** (`#f2f2f2`): encabezado de tabla, fila en hover, fondo de tags neutros.
- **Lienzo** (`#fafafa`): fondo de página.
- **Superficie** (`#ffffff`): tarjetas, tabla, campos.

### Named Rules
**La Regla de la Excepción Única.** Dentro del área de trabajo (todo lo que no es el sidebar), solo hay un color con significado especial fuera de la escala de progreso azul: esmeralda para lo ganado. Ningún otro estado, categoría o acción recibe un color propio ahí — se comunican con tono neutro, iconografía o forma, nunca inventando un color adicional con significado de estado. Esta regla sobrevivió intacta al rebrand: cuando la marca cambió de índigo a Azul ISYN, no se aprovechó para "agregar un color más"; el área de trabajo se mantuvo igual de restringida. El terracota del sidebar (Regla del Rincón Cálido) no es una excepción a esta regla — es identidad de marca/navegación, nunca comunica estado de un prospecto, y no debe usarse fuera del sidebar.

**La Regla del No-Semáforo.** El estado de un prospecto nunca se comunica con una paleta roja/ámbar/verde. Se comunica con cuánto se llenó un medidor de una sola tonalidad, más el texto — el color nunca es la única fuente de información.

**La Regla del Rincón Cálido.** El sidebar es la única superficie del sistema con licencia para ser cálida, minimalista y llamativa — por pedido explícito del usuario. Vive en su propia paleta (arena/lino + terracota, ver Colors → Sidebar) y no lleva ni el azul funcional de ISYN ni el esmeralda de cierre ganado. A cambio, su vocabulario de interacción sigue siendo el mismo del resto del sistema (mismo radio de esquina, mismo peso de ícono, mismo patrón de "activo = relleno sólido") para que siga sintiéndose parte de la misma app. Esta calidez nunca cruza al área de trabajo ni a los botones, tags o medidores — el terracota no aparece fuera del sidebar.

### Tema oscuro

Toda la app (excepto el login, ver Overview) lee sus colores a través de una capa semántica en `static/css/app.css` — `--bg-canvas`, `--bg-surface`, `--bg-surface-sunken`, `--text-heading`, `--text-primary`, `--text-secondary`, `--text-muted`, `--text-faint`, `--border-soft`, `--border-default`, `--border-strong` — más las rampas `--brand-*`, `--ok-*`, `--danger-*` y `--side-*`. `:root[data-theme="dark"]` redefine únicamente esos tokens; ningún componente referencia un hex crudo fuera de la capa semántica (con la única excepción deliberada de `.icon-btn-done`, que usa `--ink-900` fijo a propósito para su efecto de "sello" en ambos temas).

- **Área de trabajo (oscuro):** lienzo `#16181b`, superficie `#1e2124`, superficie hundida `#24272b`. Texto de `#f2f0ed` (encabezados) a `#6b665d` (tenue). El Azul ISYN se aclara a `#4a9de0`/`#7cc4f0` para mantener contraste sobre fondos oscuros; esmeralda y rojo reciben el mismo tratamiento.
- **Sidebar (oscuro):** el mundo cálido no desaparece, se re-tonaliza — degradado de espresso oscuro (`#241a10` → `#160f09`) en vez de arena/lino, texto crema (`#f0e4d4`), terracota más profundo en el relleno activo (`#c9502a`, para que el texto blanco tenga contraste) y un terracota claro (`#f2a679`) como color de texto en el hover (que ahora tiene fondo oscuro `#3a2415`, no claro).
- **Interruptor:** un botón en la topbar (ícono de sol/luna) alterna `data-theme` entre `"light"` y `"dark"` y lo guarda en `localStorage`. Sin preferencia guardada, arranca según `prefers-color-scheme` del sistema. Un script inline en `<head>` aplica el atributo antes del primer render para que no haya parpadeo del tema equivocado — la app es multi-página (Django clásico, no SPA), así que cada navegación es una carga completa.

### Named Rules
**La Regla de la Capa Semántica.** Ningún componente nuevo fija un color de fondo, texto o borde con un hex literal si ese rol ya tiene un token semántico — se usa el token, nunca el valor crudo, para que el modo oscuro lo herede automáticamente. Los únicos hex fijos permitidos son los que son intencionalmente invariables por tema (el sello de `.icon-btn-done`, el shell del login).

## Typography

**Body Font:** Inter (con -apple-system, Segoe UI, system-ui como respaldo)

**Character:** Una sola familia para todo — títulos, botones, etiquetas, cuerpo y datos de tabla. Es una decisión de modo Operate, no un descuido: la interfaz es una herramienta de trabajo diario, no una superficie de marca — confirmado explícitamente al documentar este sistema, y no se cuestionó al adoptar la marca de ISYN (el logo trae su propia tipografía condensada, pero esa vive solo dentro de la imagen del logo, nunca se replica como fuente del sistema).

### Hierarchy
Escala ajustada e intencionalmente granular (ratio de paso corto, ~1.02–1.06 entre escalones vecinos) — típica de modo Operate, donde cada componente de UI necesita su propio tamaño exacto en vez de compartir 3-4 tallas genéricas.

- **1.7rem** (700, tabular-nums): valor numérico de las tarjetas KPI del dashboard de inventario — el escalón más grande del sistema, reservado para cifras que se leen de un vistazo.
- **1.15rem** (650): título de página, encabezado del topbar.
- **1.02rem** (700): nombre de marca en el sidebar.
- **0.925rem** (400, 1.5): cuerpo base — texto por defecto de toda la app.
- **0.875rem** (400–600): datos de tabla, enlaces de navegación del sidebar, campos de formulario.
- **0.85rem** (600): botones estándar, nombre de usuario en el pie del sidebar.
- **0.82rem** (400–650): subtítulo del topbar, `form-label`, enlaces del embudo.
- **0.8rem** (600): botones pequeños (`btn-sm`), texto secundario del sidebar.
- **0.78rem** (650): etiqueta del medidor de etapa.
- **0.76rem** (650, mayúsculas, tracking 0.03em): etiquetas de filtro.
- **0.74rem** (650): texto de tags/pills.
- **0.72rem** (700, mayúsculas, tracking 0.04em): encabezados de columna de tabla — el escalón más pequeño del sistema.

### Named Rules
**La Regla de la Familia Única.** Ninguna pantalla introduce una segunda familia tipográfica. La jerarquía se construye con peso y tamaño, nunca con una fuente "de marca" adicional — ni siquiera la condensada del logotipo de ISYN, que se queda dentro de la imagen del logo.

## Layout

Shell fijo de dos columnas: sidebar de 240px (`--sidebar-w`) a la izquierda, contenido fluido a la derecha con un `topbar` (título + subtítulo) y un área de contenido con padding `1.5rem 1.75rem`. Por debajo de 860px el sidebar se convierte en panel deslizante fuera de pantalla (`transform: translateX(-100%)`), con un botón de menú fijo arriba-izquierda y un fondo oscuro (`backdrop`) que lo cierra al tocar fuera — la navegación nunca queda inaccesible en móvil.

Las tablas usan densidad alta a propósito (`0.62rem 1rem` de padding vertical por celda) para maximizar cuántos prospectos caben en pantalla sin scroll — la escaneabilidad de muchas filas es más importante que el aire entre ellas. Contenedores anchos (tabla, formularios) envueltos en `.table-responsive` para scroll horizontal en pantallas angostas, nunca recorte de contenido.

## Elevation & Depth

Sistema mayormente plano con una sola sombra ambiental compartida (`--shadow-card`: `0 1px 2px rgba(26,26,26,.04), 0 8px 24px -12px rgba(26,26,26,.12)`) para todo lo que "flota" sobre el lienzo: paneles, la tabla, la barra de filtros. No hay una escala de elevación con múltiples niveles — algo tiene esta sombra suave, o no tiene sombra.

### Named Rules
**La Regla de la Sombra Única.** Dentro de la app (todo lo que vive detrás del login) existe un solo valor de sombra. No se introduce una sombra "más fuerte" para jerarquía; la jerarquía la da el color y la tipografía, no la profundidad. La única excepción confirmada es la pantalla de login (`.auth-card`), que no es una superficie de trabajo sino el primer momento de la marca: usa una sombra más dramática (`0 20px 60px -20px rgba(26,26,26,.45)`) derivada del mismo Ink 900, no un color nuevo.

## Shapes

Dos lenguajes de forma conviven a propósito:
- **Contenedores** (tarjetas, botones, campos, tabla): radio moderado — `10px` (`--radius-sm`) en controles interactivos, `14px` (`--radius`) en superficies grandes como paneles y la tabla.
- **Medidores y etiquetas** (el track del medidor de etapa, el track del embudo agregado, los tags/pills): completamente redondeados (`999px`). Esta forma está reservada para elementos que comunican una proporción o una categoría — nunca se usa en un contenedor rectangular de contenido.

## Components

### Buttons
- **Shape:** `10px` de radio (`--radius-sm`), consistente en todos los botones.
- **Primary:** fondo Azul ISYN (`#046cb3`), texto blanco, `0.5rem 1rem`. Reservado para la acción principal de cada pantalla ("+ Nuevo comprador", "Guardar", "Buscar").
- **Hover:** el primario oscurece a Marino ISYN (`#014b72`); los botones outline ganan un fondo sutil de su propio color (nunca azul genérico de Bootstrap para acciones que no son la acción principal de la página).
- **Outline secondary / danger:** fondo transparente, borde y texto en el color de rol correspondiente. `danger` (`#ef4444`) reservado exclusivamente para eliminar — nunca para comunicar estado.

### Icon Buttons (componente de firma)
Clúster de botones fantasma de 32×32px, borde neutro por defecto. Cada uno se tiñe de un color distinto solo al pasar el mouse, según su significado — no por decoración:
- **Correo:** hover tiñe a Azul ISYN (fondo `#eff6fb`, texto `#014b72`) — es una acción de progreso.
- **WhatsApp:** hover tiñe a Esmeralda Ganada (fondo `#d1fae5`, texto `#065f46`) — es el canal más cercano a un cierre.
- **Marcar contactado:** hover se vuelve sólido en Ink 900 — es un cambio de estado, no un canal, y se distingue deliberadamente de los dos anteriores.

Nunca son botones azules genéricos ni usan emoji como ícono — cada uno es un SVG de trazo propio (`stroke-width: 1.6`, `currentColor`).

Los perfiles externos (LinkedIn, Facebook, Instagram, sitio web — visibles solo en el detalle del comprador, nunca en la fila del listado, para no saturar la tabla) comparten la misma clase y el mismo tinte azul que Correo (`.icon-btn-link`): son canales de contacto alternativos, no un cierre ganado, así que no reciben un color de marca propio por plataforma — eso rompería la Regla de la Excepción Única. Los íconos de estas redes son representaciones genéricas de trazo propio, no los logotipos oficiales de cada marca.

### Contact Row (componente de firma)
En el detalle del comprador, cada canal de contacto (correo, teléfono/WhatsApp, LinkedIn, Facebook, Instagram, sitio web) se muestra como una sola fila clicable: el Icon Button a la izquierda y el valor (el correo, el número, o el nombre de la plataforma) a la derecha, en la misma línea — nunca el valor como texto suelto arriba y el botón de acción suelto más abajo, que es como empezó este componente y generaba doble información para el mismo dato. Toda la fila es un enlace; el valor se trunca con elipsis si es muy largo. Solo se muestran las filas de los canales que el comprador realmente tiene.

### Stage Meter (componente de firma)
Barra de 44×6px, completamente redondeada, que se llena en Azul ISYN proporcional a la etapa del prospecto (25% / 50% / 75% / 100%), más la etiqueta de texto siempre visible al lado — el color nunca es la única fuente de información. Al llegar a "Cliente" (100%), el relleno cambia a Esmeralda Ganada. "Descartado" no usa el medidor: se muestra con una marca de "×" en Texto Tenue, fuera de la escala de progreso. El mismo componente se repite a escala agregada como el **Embudo** al inicio del listado de compradores — una barra segmentada por todo el pipeline, donde cada segmento es clicable y filtra la tabla a esa etapa.

### Tags / Pills
- **Style:** completamente redondeados, sin borde, fondo de tinte plano. `tag-neutral` (fondo `#f2f2f2`, texto `#737373`) para categorías descriptivas (sector, categoría de producto). Los tags de canal (tipo de plantilla) heredan los mismos colores que los Icon Buttons — azul para correo, esmeralda para WhatsApp — para que el mismo canal se reconozca igual en cualquier pantalla.

### Cards / Containers (`.panel`, `.table-panel`)
- **Corner Style:** `14px`.
- **Background:** blanco sobre lienzo `#fafafa`.
- **Shadow Strategy:** la sombra única descrita en Elevation & Depth.
- **Border:** `1px solid #e5e5e5`.

### Inputs / Fields
- **Style:** fondo blanco, borde `#e5e5e5`, radio `10px`, padding `0.5rem 0.75rem`.
- **Focus:** borde Azul ISYN claro (`#6ba9d6`) más halo de `0 0 0 3px` en Azul ISYN Faint (`#eff6fb`).
- **Search fields:** ícono de lupa incrustado a la izquierda (`.search-field`), nunca un campo de búsqueda sin señal visual de qué hace.

### Navigation
Sidebar fijo de 240px, en el mundo cálido descrito en la Regla del Rincón Cálido: fondo en degradado vertical muy sutil de arena a lino (`#faf3e6` → `#f1e2c8`), sin grano ni resplandor — la calidez viene del color plano, no de textura, para que se lea minimalista. El logo real de ISYN (`static/img/isyn-logo.png`, ya con fondo transparente) flota directo sobre el degradado cálido, sin placa ni tarjeta propia — el archivo anterior tenía fondo blanco opaco y necesitaba una superficie propia para no verse como una caja rota; la versión actual ya no la necesita. Los enlaces de navegación usan tinta cálida (`#35281b`) por defecto; en hover ganan un fondo terracota suave (`#f0d7bd`); el enlace activo gana relleno terracota sólido (`#b54a26`) con texto blanco y peso 600 — mismo patrón de "activo = relleno sólido" que el resto del sistema, solo que en el acento propio del sidebar. En móvil, colapsa detrás de un botón de menú fijo y un fondo oscuro neutro que cierra al tocar fuera (ese scrim no es parte de la identidad del sidebar, así que se queda neutro). En escritorio existe un segundo control, independiente del menú móvil: un botón `.chrome-btn` en la topbar (ícono de panel lateral) que oculta el sidebar por completo — se retira del flujo (`width: 0`), el contenido ocupa el ancho libre, y el mismo botón lo trae de vuelta. Ese estado también se guarda en `localStorage` y se aplica antes del primer render, igual que el tema.

### Pantalla de login
Único lugar fuera del shell de la app. Fondo oscuro (`#1a1a1a`) con dos degradados radiales muy tenues (Azul ISYN al 18% y Marino ISYN al 20%) — el mismo par de colores de la marca, nunca un tercer acento nuevo. Una sola tarjeta centrada (`.auth-card`) con el logo real de ISYN arriba (sin placa, porque la tarjeta ya es blanca) y la sombra dramática descrita en Elevation & Depth.

### Named Rules
**La Regla del Resplandor de Marca.** La pantalla de login es ahora la única superficie oscura del producto (el sidebar pasó al mundo cálido de la Regla del Rincón Cálido y ya no aplica esta regla). Lleva un resplandor de dos degradados radiales muy tenues en el par Azul/Marino ISYN, nunca un color nuevo — es el primer momento de marca de la sesión, antes de que el usuario entre al sidebar cálido o al área de trabajo azul. Una superficie oscura nunca es un relleno plano sin ese resplandor.

**La Regla del Logo Real.** El logo de marca en cualquier pantalla es siempre el asset real entregado por ISYN (`static/img/isyn-logo.png`, actualizado a una versión con fondo transparente), nunca una recreación, aproximación o ícono inventado que se le parezca. Si el archivo vuelve a cambiar, se reemplaza el archivo — nunca se dibuja un sustituto.

## Do's and Don'ts

### Do:
- **Do** usar Azul ISYN para todo lo que sea progreso o acción, en cualquier intensidad de su rampa de tinte.
- **Do** reservar esmeralda exclusivamente para un cierre ganado (Cliente, WhatsApp) — nunca para "positivo" en general.
- **Do** acompañar siempre el color de estado con texto — nunca solo color.
- **Do** dibujar íconos propios en SVG de trazo consistente (`stroke-width: 1.6`, sin relleno).
- **Do** usar radio `999px` solo en medidores, tracks y tags — nunca en contenedores de contenido.
- **Do** usar siempre el archivo de logo real de ISYN, nunca una recreación.
- **Do** mantener el terracota del sidebar contenido ahí — es identidad de navegación, no un segundo color de acción.
- **Do** usar los tokens semánticos (`--bg-surface`, `--text-primary`, etc.) para cualquier color nuevo de fondo/texto/borde, nunca un hex literal, para que el modo oscuro lo herede sin trabajo extra.

### Don't:
- **Don't** introducir un tercer color con significado de estado (esto sería reconstruir el semáforo que este sistema reemplazó explícitamente).
- **Don't** usar el terracota del sidebar (o el fondo cálido) en botones, tags, medidores o cualquier superficie del área de trabajo — rompería la Regla del Rincón Cálido, que existe precisamente para mantener esa calidez contenida.
- **Don't** usar emoji como ícono en ningún lugar del producto.
- **Don't** usar azul genérico de Bootstrap para acciones que no son la acción primaria de la pantalla.
- **Don't** agregar una segunda familia tipográfica "de marca" — Inter es la única voz del sistema, por elección de modo Operate, no por omisión.
- **Don't** introducir tarjetas de métrica tipo "número grande + etiqueta" sin una función real — el Embudo reemplazó ese patrón precisamente porque además de mostrar filtra.
- **Don't** referirse al producto como "CenterComp" en ninguna superficie visible — ese nombre quedó retirado; solo sobrevive como nombre interno del paquete de Python (`centercomp/`).
