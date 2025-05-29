# Codex React Dashboard

This directory contains a small [Next.js](https://nextjs.org/) application that renders tasks from the `.tasks` directory. The task list and kanban board are now available on separate pages.

## Development

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

The dashboard loads tasks at runtime using a shared React hook and API route.

### Pages

- `/` - home page
- `/table` - task list view
- `/kanban` - kanban board view
- `/todo` - page showing only tasks with a `todo` status
- `/task/[id]` - view and edit an individual task

To generate a static site for GitHub Pages run:

```bash
npm run build
```

The output will be placed in the `out/` directory.
