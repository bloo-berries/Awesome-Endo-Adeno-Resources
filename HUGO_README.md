# Hugo Site Setup

This repository now uses [Hugo](https://gohugo.io/) with the [Poison theme](https://github.com/lukeorth/poison) to create a beautiful, professional website for the Awesome Endo Adeno Resources.

## Features

- **Clean, Professional Design**: The Poison theme provides a modern, readable layout
- **Dark/Light Mode**: Users can toggle between dark and light themes
- **Responsive**: Works great on desktop, tablet, and mobile devices
- **Fast Loading**: Static site generation ensures quick page loads
- **SEO Optimized**: Built-in SEO features and meta tags
- **No External Dependencies**: Everything is self-contained for privacy

## Local Development

### Prerequisites

1. Install Hugo (if not already installed):

   ```bash
   brew install hugo  # macOS
   # or visit https://gohugo.io/installation/
   ```

2. Clone the repository with submodules:

   ```bash
   git clone --recurse-submodules https://github.com/bloo-berries/Awesome-Endo-Adeno-Resources.git
   cd Awesome-Endo-Adeno-Resources
   ```

### Running Locally

1. Start the development server:

   ```bash
   hugo server
   ```

2. Open your browser to `http://localhost:1313`

3. The site will automatically reload when you make changes to content files.

### Building for Production

```bash
hugo
```

This creates a `public/` directory with the built site.

## Content Structure

- `content/posts/` - Main resource articles
- `content/about.md` - About page
- `config.toml` - Site configuration
- `themes/poison/` - The Poison theme (Git submodule)

## Customization

### Colors and Styling

Edit `config.toml` to customize:

- Sidebar colors
- Light/dark mode colors
- Brand name and description
- Menu structure
- Social media links

### Adding Content

1. Create new posts in `content/posts/`:

   ```bash
   hugo new posts/your-post-name.md
   ```

2. Edit the front matter at the top of the file:

   ```yaml
   ---
   title: "Your Post Title"
   date: 2025-01-27
   draft: false
   tags: ["tag1", "tag2"]
   ---
   ```

### Custom CSS

Add custom styles in `assets/css/custom.css` to override theme styles.

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when you push to the `main` branch.

### Manual Deployment

If you need to deploy manually:

1. Build the site:

   ```bash
   hugo
   ```

2. The built files are in the `public/` directory

## Theme Information

- **Theme**: [Poison](https://github.com/lukeorth/poison) by Luke Orth
- **License**: GPL-3.0
- **Features**: Dark/light mode, table of contents, comments support, RSS feeds

## Support

For Hugo-specific questions, check the [Hugo documentation](https://gohugo.io/documentation/).

For theme-specific questions, visit the [Poison theme repository](https://github.com/lukeorth/poison).
