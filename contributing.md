# Contributing to Endo Adeno Resources

Thank you for your interest in contributing to this comprehensive resource for Endometriosis and Adenomyosis! This guide will help you understand how to contribute effectively.

## 🌟 How to Contribute

### Adding New Resources

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Awesome-Endo-Adeno-Resources.git
   cd Awesome-Endo-Adeno-Resources
   git submodule update --init --recursive
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/add-new-resource
   ```

4. **Edit the main resource file**:
   - Open `content/posts/endo-adeno-resources-overview.md`
   - Add your resource in the appropriate section
   - Follow the existing format and style

5. **Test your changes locally**:
   ```bash
   hugo server
   ```
   Visit `http://localhost:1313` to preview your changes

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

## 🛠️ Technical Contributions

### Hugo Development

If you're contributing to the site's technical aspects:

1. **Install Hugo** (if not already installed):
   ```bash
   brew install hugo  # macOS
   ```

2. **Make your changes** to the appropriate files:
   - `config.toml` - Site configuration
   - `content/` - Content files
   - `assets/css/custom.css` - Custom styles (if needed)

3. **Test thoroughly** before submitting

### Link Validation

We maintain link quality with our validation script:
```bash
python3 check_links.py
```

Please run this before submitting changes to ensure all links are working.

## 📝 Pull Request Guidelines

When submitting a Pull Request:

1. **Clear Title**: Use a descriptive title like "Add [Resource Name] to [Section]"
2. **Detailed Description**: Explain what you're adding and why it's valuable
3. **Testing**: Confirm you've tested the changes locally
4. **Formatting**: Ensure proper markdown formatting
5. **Links**: Verify all links are working

## 🚀 Getting Help

If you need help or have questions:

1. **Check existing issues** on GitHub
2. **Create a new issue** for bugs or feature requests
3. **Join discussions** in existing pull requests

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for helping make this resource better for the Endometriosis and Adenomyosis community!** ❤️
