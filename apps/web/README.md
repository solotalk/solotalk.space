# Solotalk Space — Web Frontend

Vue 3 + Vite + Naive UI frontend for Solotalk Space.

## Setup

```bash
pnpm install
```

## Develop

```bash
pnpm dev
```

The dev server proxies `/api` to `http://127.0.0.1:8000` (the FastAPI backend).

## Build

```bash
pnpm build
```

Static artifacts are emitted to `dist/`, ready to be served by nginx.

## Structure

- `src/main.ts` — app entry (Vue, router, Naive UI)
- `src/App.vue` — top navigation shell
- `src/router/` — routes with auth/admin guards
- `src/api/client.ts` — axios instance (Bearer token, 401 refresh retry)
- `src/stores/auth.ts` — auth state persisted in localStorage
- `src/views/` — Home, Download, Questions, Upload, Login, Register, Admin
