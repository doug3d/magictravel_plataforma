# Estrutura de Administração

Este documento explica a organização dos painéis administrativos do sistema.

## 📋 Visão Geral

O sistema possui **DOIS** tipos de admin separados:

### 1. **Seller Admin** (Implementado) ✅
- **Localização**: `/seller/admin/`
- **Propósito**: Cada seller gerencia sua própria loja
- **Acesso**: Sellers autenticados (`@seller_required`)
- **Funcionalidades**:
  - Dashboard com métricas da loja (vendas do dia, mês, customers únicos)
  - Visualização de pedidos da loja
  - Gerenciamento de produtos (futuro)
  - Gerenciamento de clientes da loja (futuro)
  - Configurações da loja (futuro)

### 2. **System Admin** (Futuro) ⏳
- **Localização**: `/admin/` (reservado)
- **Propósito**: Super admin que gerencia todo o sistema
- **Acesso**: Super admin role (a ser implementado)
- **Funcionalidades** (planejadas):
  - Visualização de todos os sellers
  - Visualização de todas as lojas
  - Visualização de todos os customers
  - Visualização de todos os pedidos
  - Estatísticas globais do sistema
  - Gerenciamento de permissões
  - Configurações do sistema

---

## 🗂️ Estrutura de Arquivos

```
/
├── src/routes/
│   ├── admin_seller.py          # Rotas do Seller Admin (/seller/admin/*)
│   └── admin_system.py          # [FUTURO] Rotas do System Admin (/admin/*)
│
├── templates/
│   ├── admin_seller/            # Templates do Seller Admin
│   │   ├── base_seller.html     # Layout base do seller admin
│   │   ├── login.html           # Login do seller
│   │   ├── dashboard.html       # Dashboard do seller
│   │   └── ...                  # Outras páginas do seller
│   │
│   └── admin/                   # [FUTURO] Templates do System Admin
│       ├── base_admin.html      # Layout base do system admin
│       ├── login.html           # Login do super admin
│       └── ...                  # Páginas do system admin
│
└── static/
    ├── css/
    │   └── admin.css            # CSS compartilhado (ambos admins)
    │
    └── js/
        └── admin-auth.js        # Auth do Seller Admin
        └── [futuro] system-admin-auth.js
```

---

## 🔑 Autenticação

### Seller Admin
- **Token**: `localStorage.getItem('seller_token')`
- **Header**: `Seller-Authorization: Bearer {token}`
- **Store**: `Store-Credential` dinâmico (obtido após login)

### System Admin (futuro)
- **Token**: `localStorage.getItem('admin_token')`
- **Header**: `Admin-Authorization: Bearer {token}` (ou similar)
- **Escopo**: Acesso a todos os recursos do sistema

---

## 🚀 Como Acessar

### Seller Admin
1. Acesse: `http://localhost:8001/seller/admin/login`
2. Login com credenciais de seller
3. Gerencia apenas sua própria loja

### System Admin (futuro)
1. Acesse: `http://localhost:8001/admin/login`
2. Login com credenciais de super admin
3. Acesso a todo o sistema

---

## 📝 Nomenclatura

- **seller_admin** = Admin de loja individual (um seller gerenciando sua loja)
- **system_admin** ou **admin** = Admin do sistema (super admin)

---

## ⚠️ IMPORTANTE

**NÃO confunda os dois admins!**
- Se você está trabalhando em funcionalidades de LOJA → use `admin_seller`
- Se você está trabalhando em funcionalidades de SISTEMA → use `admin` (futuro)

---

_Última atualização: Implementação do Seller Admin completa._

