# Read the Docs Integration

This project is set up to be hosted on [Read the Docs](https://readthedocs.org/). This page explains how to set up and manage the Read the Docs integration.

## Setting Up Read the Docs

1. Go to [Read the Docs](https://readthedocs.org/) and sign in or create an account.
2. Click on "Import a Project" and select your GitHub repository.
3. Configure the project settings:
   - Name: `rodrunner`
   - Repository URL: `https://github.com/bilgehannevruz/rodrunner`
   - Repository type: `Git`
   - Default branch: `main`
   - Documentation type: `Mkdocs`
4. Click "Next" and then "Build".

## Configuration

The project includes a `.readthedocs.yaml` file in the root directory that configures the Read the Docs build process:

```yaml
# .readthedocs.yaml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Set the OS, Python version and other tools you might need
build:
  os: ubuntu-22.04
  tools:
    python: "3.10"
  jobs:
    post_create_environment:
      # Install uv
      - pip install uv
      # Install dependencies with uv
      - uv pip install --system -e ".[dev]"

# Build documentation in the docs/ directory with MkDocs
mkdocs:
  configuration: mkdocs.yml

# Optionally declare the Python requirements required to build your docs
python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - dev
```

This configuration:

1. Uses Ubuntu 22.04 as the build environment
2. Uses Python 3.10
3. Installs `uv` for package management
4. Installs the project and its development dependencies
5. Builds the documentation using MkDocs with the configuration in `mkdocs.yml`

## Webhooks

Read the Docs can automatically build your documentation when you push changes to your repository. To set up webhooks:

1. Go to your project on Read the Docs
2. Click on "Admin" > "Integrations"
3. Select "GitHub incoming webhook"
4. Copy the webhook URL
5. Go to your GitHub repository
6. Click on "Settings" > "Webhooks" > "Add webhook"
7. Paste the webhook URL in the "Payload URL" field
8. Set "Content type" to "application/json"
9. Select "Just the push event"
10. Click "Add webhook"

## Versioning

Read the Docs supports versioning your documentation. To create a new version:

1. Create a new tag or branch in your repository
2. Go to your project on Read the Docs
3. Click on "Admin" > "Versions"
4. Activate the new version
5. Build the new version

## Custom Domain

You can use a custom domain for your documentation:

1. Go to your project on Read the Docs
2. Click on "Admin" > "Domains"
3. Add your custom domain
4. Configure your DNS settings as instructed

## Troubleshooting

If you encounter issues with the Read the Docs build:

1. Check the build logs on Read the Docs
2. Verify that your `.readthedocs.yaml` file is correct
3. Make sure your `mkdocs.yml` file is valid
4. Test building the documentation locally with `mkdocs build`
5. Check that all required dependencies are installed

For more information, see the [Read the Docs documentation](https://docs.readthedocs.io/).
