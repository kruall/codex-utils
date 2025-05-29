# Codex React Dashboard

This directory contains a small [Next.js](https://nextjs.org/) application that renders tasks from the `.tasks` directory in both table and kanban views.

## Development

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

The dashboard reads local task files during build time using `getStaticProps`.

### Pages

- `/` - main dashboard with table and kanban views
- `/todo` - page showing only tasks with a `todo` status

To generate a static site for GitHub Pages run:

```bash
npm run build
```

The output will be placed in the `out/` directory.
