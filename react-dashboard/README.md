# Codex React Dashboard

This directory contains a small [Next.js](https://nextjs.org/) application that renders tasks from the `.tasks` directory.

## Development

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

This script uses a small Python helper to export tasks from the `.tasks`
directory before starting the Next.js server. Ensure Python is available in your
environment.

The dashboard loads tasks at runtime using a shared React hook and API route.

### Pages

- `/` - home page
- `/table` - task list view
- `/task/[id]` - view and edit an individual task

To generate a static site for GitHub Pages run:

```bash
npm run build
```

The output will be placed in the `out/` directory.
