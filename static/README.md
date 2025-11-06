# 📁 Static Files

Esta pasta contém todos os arquivos estáticos da aplicação.

## 🎨 CSS

### `css/base.css`

CSS base compartilhado por todas as páginas do site. Inclui:

- **Reset e variáveis CSS** (`:root` com cores e estilos padrão)
- **Estilos globais**: body, container, header, nav
- **Componentes reutilizáveis**: cards, buttons, forms, badges, grid, loading, empty states
- **Utilitários**: margins, text-align, etc
- **Responsividade**: media queries para mobile

### Como usar

#### 1. No `base.html` (já configurado):
```html
<link rel="stylesheet" href="/static/css/base.css">
```

#### 2. Nas páginas específicas (dentro do `{% block styles %}`):
```html
{% block styles %}
<style>
    /* CSS específico desta página */
    .meu-componente {
        /* ... */
    }
</style>
{% endblock %}
```

## 🎨 Variáveis CSS Disponíveis

```css
--primary: #667eea
--primary-dark: #764ba2
--secondary: #4caf50
--secondary-dark: #45a049
--danger: #f44336
--warning: #ff9800
--info: #2196f3
--light: #f5f5f5
--dark: #333
--gray: #666
--border: #e0e0e0
--shadow: rgba(0, 0, 0, 0.1)
--shadow-hover: rgba(0, 0, 0, 0.15)
```

## 📦 Classes Utilitárias

### Cards
- `.card` - Card básico com hover
- `.card:hover` - Elevação no hover

### Buttons
- `.btn` - Botão base
- `.btn-primary` - Botão primário (gradient roxo)
- `.btn-secondary` - Botão secundário (verde)
- `.btn-outline` - Botão outline

### Grid
- `.grid` - Grid base
- `.grid-2` - Grid de 2 colunas (responsivo)
- `.grid-3` - Grid de 3 colunas (responsivo)
- `.grid-4` - Grid de 4 colunas (responsivo)

### Loading
- `.loading` - Container de loading
- `.spinner` - Spinner animado

### Empty State
- `.empty-state` - Estado vazio padrão

### Badges
- `.badge` - Badge base
- `.badge-primary` - Badge azul
- `.badge-success` - Badge verde
- `.badge-warning` - Badge laranja
- `.badge-danger` - Badge vermelho

### Margins
- `.mt-1`, `.mt-2`, `.mt-3`, `.mt-4` - Margin top
- `.mb-1`, `.mb-2`, `.mb-3`, `.mb-4` - Margin bottom

### Text
- `.text-center` - Texto centralizado

## 📂 Estrutura

```
static/
├── css/
│   └── base.css (estilos globais)
├── js/ (futuro)
├── images/ (futuro)
└── README.md (este arquivo)
```

## 🚀 Próximos passos

Quando precisar adicionar:
- **JavaScript global**: criar `js/base.js`
- **Imagens**: criar pasta `images/`
- **Fontes**: criar pasta `fonts/`

