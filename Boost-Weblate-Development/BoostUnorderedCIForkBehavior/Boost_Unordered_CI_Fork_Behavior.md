# Boost Unordered CI/CD Workflow Behavior in Forked Repositories

## Overview

This document explains how the Boost Unordered CI/CD workflow behaves in forked repositories, specifically regarding documentation translation commits made through Weblate.

## Boost Unordered Repository Information

- **Repository**: Boost Unordered (typically `boostorg/unordered` or fork)
- **CI Workflow**: `.github/workflows/ci.yml`
- **Workflow Purpose**: Runs C++ tests across multiple compilers, platforms, and C++ standards
- **Documentation Format**: AsciiDoc (`.adoc` files)
- **Weblate Integration**: Pushes translations to `weblate-*` branches

---

## Boost Unordered CI Workflow Configuration

### Workflow Location
- **File**: `.github/workflows/ci.yml` in the Boost Unordered repository

### Trigger Conditions

The Boost Unordered CI workflow is configured as follows:

```yaml
on:
  pull_request:  # No branch filter - runs on ALL pull requests
  push:
    branches:
      - master
      - develop
      - bugfix/**
      - feature/**
      - fix/**
      - pr/**
```

**Key Points**:
- **Pull Requests**: The `pull_request:` trigger has **no branch filter**, meaning it runs on **ALL pull requests** regardless of:
  - Source branch (e.g., `weblate-intro`, `weblate-*`, or any other branch)
  - Target branch (e.g., `master`, `develop`, or any other branch)
  - Whether the PR is from a fork or the same repository

- **Pushes**: Only triggers on pushes to specific branch patterns:
  - `master`
  - `develop`
  - `bugfix/**`
  - `feature/**`
  - `fix/**`
  - `pr/**`

---

## CI/CD Pipeline Triggering for Forked Boost Unordered Documents

**Statement**: For **direct pushes** to forked boost-unordered documents, the CI/CD pipeline does not trigger. However, **pull requests** from forked repositories **WILL trigger** the CI/CD pipeline.

### Detailed Explanation:

1. **Default State (Most Common)**: 
   - Boost Unordered CI workflow is **disabled** in forks by default
   - Weblate translation commits **pushed directly** to fork branches **do not trigger** the CI workflow
   - The fork's own CI workflow **does not run** unless explicitly enabled in fork settings

2. **If CI Workflow Is Enabled in Fork**:
   - **For Push Events**: 
     - The workflow **can** run, but only if trigger conditions match
     - Boost Unordered CI requires pushes to: `master`, `develop`, `bugfix/**`, `feature/**`, `fix/**`, or `pr/**`
     - Weblate branches like `weblate-intro` **do not match** these patterns
     - Therefore, even if enabled, **direct pushes** to Weblate branches **will not trigger** the CI workflow
   
   - **For Pull Request Events**: 
     - The workflow **WILL run** on ALL pull requests
     - The `pull_request:` trigger has no branch filter, so it runs on every PR
     - If a PR is created from a `weblate-intro` branch, the CI workflow **WILL trigger** (if enabled)
     - This applies to PRs from forks to the base repository as well

---