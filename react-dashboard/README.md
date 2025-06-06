# Codex React Dashboard

This directory contains a [Next.js](https://nextjs.org/) application that renders tasks and epics directly from GitHub repositories via the GitHub API.

## Development

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

The dashboard loads tasks and epics at runtime directly from GitHub repositories using the GitHub API. No local data generation is required.

### Configuration

The dashboard can be configured to work with GitHub repositories in two ways:

1. **Runtime Repository Selection**: Users can select a repository through the `/repos` page after authentication
2. **Environment Variable**: Set `NEXT_PUBLIC_GITHUB_REPOS` to a comma-separated list of repositories (format: `owner/repo`)

### Authentication

The dashboard supports GitHub authentication via:
- Personal Access Tokens (recommended for static deployments)
- OAuth flow (requires server-side token exchange)

### Pages

- `/` - home page
- `/table` - task list view
- `/task/[id]` - view and edit an individual task
- `/epics` - browse epics and progress
- `/epic/[id]` - view an epic tree and details
- `/repos` - select GitHub repository
- `/login` - authentication page

### Deployment

To generate a static site for GitHub Pages:

```bash
npm run build
```

The output will be placed in the `out/` directory. The application works entirely client-side and fetches data directly from the GitHub API.

### Data Sources

- **Tasks**: Loaded from `.tasks/` directory in the configured GitHub repositories
- **Epics**: Loaded from `.epics/` directory in the configured GitHub repositories
- **Caching**: Data is cached in localStorage for offline access
