# Contributing to Endo Adeno Resources

Thank you for your interest in contributing to this comprehensive resource for Endometriosis and Adenomyosis! This guide will help you understand how to contribute effectively.

## How to Contribute

### Adding New Resources

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Awesome-Endo-Adeno-Resources.git
   cd Awesome-Endo-Adeno-Resources
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/add-new-resource
   ```

4. **Edit the appropriate content file**:
   - Content pages are in `content/` (e.g., `diagnosis.md`, `healthcare.md`, `resources.md`, etc.)
   - Add your resource in the appropriate section
   - Follow the existing format and style

5. **Test your changes locally**:
   ```bash
   python3 build.py
   python3 -m http.server 8000 --directory dist
   ```
   Visit `http://localhost:8000` to preview your changes

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add [resource name] to [section]"
   git push origin feature/add-new-resource
   ```

7. **Create a Pull Request** on GitHub

### Resource Guidelines

When adding resources, please ensure:

- **Accuracy**: Verify the information is current and accurate
- **Relevance**: Resources should be directly related to Endometriosis or Adenomyosis
- **Quality**: Prefer reputable medical sources, research institutions, or established organizations
- **Format**: Follow the existing markdown format and structure
- **Descriptions**: Include brief descriptions explaining why the resource is valuable

### Types of Resources We Accept

- **Healthcare Providers**: Vetted specialists and clinics
- **Research Studies**: Current and relevant medical research
- **Support Groups**: Community and advocacy organizations
- **Educational Materials**: Books, articles, and learning resources
- **Treatment Options**: Medical and therapeutic approaches
- **Diagnostic Tools**: Testing and assessment resources
- **Financial Assistance**: Grants, programs, and support

### Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Provide accurate, helpful information
- Respect medical privacy and confidentiality
- Support evidence-based approaches
- Maintain a supportive community environment

## Technical Contributions

### Development Setup

If you're contributing to the site's technical aspects:

1. **Requirements**: Python 3.8+ (no pip dependencies needed)

2. **Build the site**:
   ```bash
   python3 build.py
   ```

3. **Serve locally**:
   ```bash
   python3 -m http.server 8000 --directory dist
   ```

4. **Make your changes** to the appropriate files:
   - `site.json` - Site configuration
   - `content/` - Content files (Markdown)
   - `assets/css/` - Stylesheets
   - `assets/js/` - JavaScript modules
   - `templates/` - HTML templates

5. **Test thoroughly** before submitting

### Link Validation

Links are checked automatically in CI using [lychee](https://github.com/lycheeverse/lychee). You can also run it locally:
```bash
lychee dist/
```

## Pull Request Guidelines

When submitting a Pull Request:

1. **Clear Title**: Use a descriptive title like "Add [Resource Name] to [Section]"
2. **Detailed Description**: Explain what you're adding and why it's valuable
3. **Testing**: Confirm you've tested the changes locally
4. **Formatting**: Ensure proper markdown formatting
5. **Links**: Verify all links are working

## Getting Help

If you need help or have questions:

1. **Check existing issues** on GitHub
2. **Create a new issue** for bugs or feature requests
3. **Join discussions** in existing pull requests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for helping make this resource better for the Endometriosis and Adenomyosis community!**
