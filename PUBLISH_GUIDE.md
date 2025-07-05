# Publishing to PyPI Guide

## Prerequisites

1. Create accounts on both:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. Get API tokens:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

## Step 1: Upload to Test PyPI (RECOMMENDED FIRST)

```bash
# Upload to Test PyPI
F:/djangos/modern-django-starter/.venv/Scripts/twine.exe upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: [your-test-pypi-api-token]
```

## Step 2: Test installation from Test PyPI

```bash
# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ modern-django-starter
```

## Step 3: Upload to Production PyPI

Once you've tested the package works from Test PyPI:

```bash
# Upload to Production PyPI
F:/djangos/modern-django-starter/.venv/Scripts/twine.exe upload dist/*

# When prompted:
# Username: __token__
# Password: [your-production-pypi-api-token]
```

## Step 4: Test installation from Production PyPI

```bash
# Install from production PyPI
pip install modern-django-starter
```

## Security Note

For better security, you can configure your tokens in ~/.pypirc:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-[your-production-token]

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-[your-test-token]
```

Then upload without entering credentials:
```bash
twine upload --repository testpypi dist/*  # for test
twine upload dist/*                        # for production
```
