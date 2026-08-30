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

Confirmado explícitamente por el usuario: el carácter es **preciso y sin fricción**, no cálido — cada elemento existe para que una persona encuentre y contacte un prospecto más rápido, no para transmitir cercanía a través de la forma. La densidad de la tabla, la escala tipográfica ajustada, y la ausencia de decoración son deliberadas. Este carácter se mantuvo al adoptar la marca de ISYN — no se reblandeció el sistema para "verse más cálido" solo porque cambió la paleta.

**Rebrand confirmado:** el cliente real de este proyecto es **ISYN (Internacional de Subastas y Negocios)**, una empresa panameña de subastas, licitaciones y negocios internacionales (isynsubastas.com). El producto llevaba antes el nombre provisional "CenterComp"; ese nombre queda retirado de toda superficie visible. El sistema de diseño construido bajo ese nombre (medidor de etapa, fila de contacto, regla de la sombra única, etc.) se conservó íntegro — solo se re-coloreó con la paleta real de ISYN, extraída por muestreo directo del archivo de logo entregado por el cliente.

**Key Characteristics:**
- Un solo acento de color (Azul ISYN) para toda acción/progreso; el esmeralda es una excepción con significado, no un color más
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

### Neutral
- **Ink 900** (`#1a1a1a`): fondo del sidebar, texto de mayor peso.
- **Texto Primario** (`#262626`): color de texto base del cuerpo.
- **Texto Secundario** (`#595959`): el gris exacto del logo de ISYN. Enlaces del embudo, botones secundarios.
- **Texto Apagado** (`#737373`): metadatos, subtítulos, columnas de contexto (país, fuente).
- **Texto Tenue** (`#a3a3a3`): el estado "Descartado" (sale de la escala de progreso, se apaga), marcadores internacionales.
- **Borde** (`#e5e5e5`): bordes de tarjetas, tabla, campos.
- **Superficie Hundida** (`#f2f2f2`): encabezado de tabla, fila en hover, fondo de tags neutros.
- **Lienzo** (`#fafafa`): fondo de página.
- **Superficie** (`#ffffff`): tarjetas, tabla, campos.

### Named Rules
**La Regla de la Excepción Única.** Solo hay un color con significado especial fuera de la escala de progreso azul: esmeralda para lo ganado. Ningún otro estado, categoría o acción recibe un color propio — se comunican con tono neutro, iconografía o forma, nunca inventando un tercer color con significado. Esta regla sobrevivió intacta al rebrand: cuando la marca cambió de índigo a Azul ISYN, no se aprovechó para "agregar un color más"; el sistema se mantuvo igual de restringido.

**La Regla del No-Semáforo.** El estado de un prospecto nunca se comunica con una paleta roja/ámbar/verde. Se comunica con cuánto se llenó un medidor de una sola tonalidad, más el texto — el color nunca es la única fuente de información.

## Typography

**Body Font:** Inter (con -apple-system, Segoe UI, system-ui como respaldo)

**Character:** Una sola familia para todo — títulos, botones, etiquetas, cuerpo y datos de tabla. Es una decisión de modo Operate, no un descuido: la interfaz es una herramienta de trabajo diario, no una superficie de marca — confirmado explícitamente al documentar este sistema, y no se cuestionó al adoptar la marca de ISYN (el logo trae su propia tipografía condensada, pero esa vive solo dentro de la imagen del logo, nunca se replica como fuente del sistema).

### Hierarchy
Escala ajustada e intencionalmente granular (ratio de paso corto, ~1.02–1.06 entre escalones vecinos) — típica de modo Operate, donde cada componente de UI necesita su propio tamaño exacto en vez de compartir 3-4 tallas genéricas.

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
Sidebar oscuro (`#1a1a1a`) fijo de 240px. El logo real de ISYN (`static/img/isyn-logo.png`, el asset entregado por el cliente, recortado a su contenido real) vive en una placa blanca redondeada arriba del sidebar — el archivo entregado no tenía fondo transparente, así que en vez de forzarlo sobre el fondo oscuro (se vería como una caja rota) se le dio una superficie propia, un patrón estándar para logos sin canal alfa. El fondo del sidebar no es un relleno plano: lleva el mismo resplandor de marca descrito en la Regla del Resplandor de Marca (abajo), anclado detrás del logo con tamaño fijo en píxeles (`320px 260px` y `260px 220px`, nunca porcentaje del alto de viewport, para que no se filtre hacia los enlaces de navegación en pantallas altas), más un grano de ruido casi imperceptible (`feTurbulence` SVG inline, 5% de opacidad, `mix-blend-mode: overlay`) y un realce interior de 1px en el borde superior y derecho (`rgba(255,255,255,.06)` / `.04`) que le da un borde físico sutil en vez de un corte plano. Los enlaces activos ganan fondo Azul ISYN sólido. En móvil, colapsa detrás de un botón de menú fijo y un fondo oscuro que cierra al tocar fuera.

### Pantalla de login
Único lugar fuera del shell de la app. Fondo oscuro (`#1a1a1a`) con dos degradados radiales muy tenues (Azul ISYN al 18% y Marino ISYN al 20%) — el mismo par de colores de la marca, nunca un tercer acento nuevo. Una sola tarjeta centrada (`.auth-card`) con el logo real de ISYN arriba (sin placa, porque la tarjeta ya es blanca) y la sombra dramática descrita en Elevation & Depth.

### Named Rules
**La Regla del Resplandor de Marca.** Toda superficie oscura del producto (el sidebar, el fondo de login) lleva el mismo resplandor: dos degradados radiales muy tenues en el par Azul/Marino ISYN, nunca un color nuevo y nunca en la misma proporción exacta — cada superficie ajusta la opacidad y el tamaño a su propia escala, pero el par de colores es siempre el mismo. Una superficie oscura nunca es un relleno plano sin ese resplandor.

**La Regla del Logo Real.** El logo de marca en cualquier pantalla es siempre el asset real entregado por ISYN (`static/img/isyn-logo.png`), nunca una recreación, aproximación o ícono inventado que se le parezca. Si el archivo cambia (por ejemplo, si el cliente entrega una versión con fondo transparente), se reemplaza el archivo — nunca se dibuja un sustituto.

## Do's and Don'ts

### Do:
- **Do** usar Azul ISYN para todo lo que sea progreso o acción, en cualquier intensidad de su rampa de tinte.
- **Do** reservar esmeralda exclusivamente para un cierre ganado (Cliente, WhatsApp) — nunca para "positivo" en general.
- **Do** acompañar siempre el color de estado con texto — nunca solo color.
- **Do** dibujar íconos propios en SVG de trazo consistente (`stroke-width: 1.6`, sin relleno).
- **Do** usar radio `999px` solo en medidores, tracks y tags — nunca en contenedores de contenido.
- **Do** usar siempre el archivo de logo real de ISYN, nunca una recreación.

### Don't:
- **Don't** introducir un tercer color con significado de estado (esto sería reconstruir el semáforo que este sistema reemplazó explícitamente).
- **Don't** usar emoji como ícono en ningún lugar del producto.
- **Don't** usar azul genérico de Bootstrap para acciones que no son la acción primaria de la pantalla.
- **Don't** agregar una segunda familia tipográfica "de marca" — Inter es la única voz del sistema, por elección de modo Operate, no por omisión.
- **Don't** introducir tarjetas de métrica tipo "número grande + etiqueta" sin una función real — el Embudo reemplazó ese patrón precisamente porque además de mostrar filtra.
- **Don't** referirse al producto como "CenterComp" en ninguna superficie visible — ese nombre quedó retirado; solo sobrevive como nombre interno del paquete de Python (`centercomp/`).
