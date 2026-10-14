# Pharma Kalsoom Final

pharma-kalsoom-final is a desktop pharmacy inventory and sales application.

![Tkinter](https://img.shields.io/badge/Tkinter-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The Tkinter implementation is organized around the entry points and modules below.

## Modules

- [`admin_dashboard.py`](admin_dashboard.py) — Admin Dashboard
- [`app.py`](app.py) — App
- [`manage_categories.py`](manage_categories.py) — Manage Categories
- [`manage_items.py`](manage_items.py) — Manage Items
- [`manage_purchase.py`](manage_purchase.py) — Manage Purchase
- [`manage_sale.py`](manage_sale.py) — Manage Sale
- [`manage_users.py`](manage_users.py) — Manage Users
- [`pharma_db.py`](pharma_db.py) — Pharma Db
- [`reports.py`](reports.py) — Reports
- [`user_dashboard.py`](user_dashboard.py) — User Dashboard

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/pharma-kalsoom-final.git
cd pharma-kalsoom-final
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Pillow tkcalendar reportlab
```

Dependency versions are not pinned in this repository.

A working Tkinter installation and a graphical desktop session are required.

### 3. Configure and run

Run from the repository root so relative file paths resolve correctly:

```bash
python app.py
```

## Repository guide

| Path | Purpose |
| --- | --- |
| [`app.py`](app.py) | Application entry point |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
