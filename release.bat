@echo off
REM Script to build and publish modern-django-starter to PyPI
REM Usage: release.bat [test|prod]

set ENV=%1
if "%ENV%"=="" set ENV=test

echo 🚀 Building modern-django-starter package...

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info

REM Build the package
F:/djangos/modern-django-starter/.venv/Scripts/python.exe -m build

REM Check the package
echo 🔍 Checking package...
F:/djangos/modern-django-starter/.venv/Scripts/twine.exe check dist/*

if "%ENV%"=="test" (
    echo 📦 Uploading to Test PyPI...
    F:/djangos/modern-django-starter/.venv/Scripts/twine.exe upload --repository testpypi dist/*
    echo ✅ Upload complete! Test with:
    echo pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ modern-django-starter
) else if "%ENV%"=="prod" (
    echo 📦 Uploading to Production PyPI...
    F:/djangos/modern-django-starter/.venv/Scripts/twine.exe upload dist/*
    echo ✅ Upload complete! Install with:
    echo pip install modern-django-starter
) else (
    echo ❌ Invalid environment. Use 'test' or 'prod'
    exit /b 1
)
