# Sticker Cases

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A modern sticker platform built with **Next.js + Django + PostgreSQL**, containerized with Docker for easy local development.


# PROJECT Docs

## 📑 Navigation

1. [Quickstart for any new dev 🚀](#1-quickstart-for-any-new-dev)
2. [Testing on Local Network (LAN) 🌐](#2-testing-on-local-network-lan)
3. [Environment files 📄](#3-environment-files)
4. [First run explained ▶️](#4-first-run-explained)
5. [Daily Dev Workflow 🔧](#5-daily-dev-workflow)

   * [5.1 Common commands 📝](#51-common-commands)
   * [5.2 Backend (Django) 🐍](#52-backend-django)
   * [5.3 Frontend (Nextjs) ⚛️](#53-frontend-nextjs)
   * [5.4 Database (Postgres) 🐘](#54-database-postgres)
   * [5.5 Database GUI (pgAdmin) 📊](#55-database-gui-pgadmin)
6. [Common tasks 🔄](#6-common-tasks)
7. [One-time setup for Windows devs 🪟](#7-one-time-setup-for-windows-devs)
8. [Repo structure 📂](#8-repo-structure)

---

### 1. Quickstart for any new dev 🚀

1. Install **Docker Desktop**
2. **Clone** the repo
3. From repo root:

* On **Linux / macOS**:

```bash
make up
```

* On **Windows (PowerShell)**:

```powershell
.\dev.ps1 up
```

4. Open:

* Frontend → [http://localhost:3000](http://localhost:3000)
* API → [http://localhost:8000](http://localhost:8000) (Admin at `/admin`)
* **pgAdmin** → [http://localhost:5050](http://localhost:5050)

  **Login with:**

  * Email: `admin@gmail.com`
  * Password: `admin`

  **Add a connection:**

  * Host: `db`
  * Port: `5432`
  * User: `postgres`
  * Password: `postgres`
  * Database: `sticker_cases`

5. Stop everything:

* Linux/macOS:

```bash
make down
```

* Windows:

```powershell
.\dev.ps1 down
```

[⬆️ Back to Navigation](#-navigation)

---

### 2. Testing on Local Network (LAN) 🌐

You can run the project so it’s accessible from other devices on the same Wi-Fi (e.g. your phone or tablet).

#### 1. Start in LAN mode

* **Windows (PowerShell):**

```powershell
.\dev.ps1 up-lan
```

* **Linux / macOS:**

```bash
make up-lan
```

This will auto-detect your **LAN IP** (e.g. `192.168.1.25`) and pass it into Django/Next.js.

#### 2. Access from another device

* Frontend → `http://<LAN_IP>:3000`
* Backend API → `http://<LAN_IP>:8000`
* pgAdmin → `http://<LAN_IP>:5050`

Your startup dashboard will also print these URLs.

#### 3. Requirements

* Your PC and device must be on the **same Wi-Fi / subnet**.
* Allow Docker/Django/Next.js through your **Windows firewall** (it may prompt the first time).
* Make sure `.env` / `docker-compose.dev.yml` has:

  ```env
  DJANGO_HOSTS=localhost,127.0.0.1,${LAN_IP}
  DJANGO_HOSTS_URLS=http://localhost:3000,http://frontend:3000,http://${LAN_IP}:3000
  ```

#### 4. Switch back to normal

If you’re only developing locally on your machine, just use:

* Windows:

```powershell
.\dev.ps1 up
```

* Linux/macOS:

```bash
make up
```

️[⬆️ Back to Navigation](#-navigation)

---

### 3. Environment files 📄

* **`.env` in the repo root** → used by Docker Compose (DB creds, Django flags, etc).
* You may also have `backend/.env` for local (non-Docker) runs; not needed with Compose.

️[⬆️ Back to Navigation](#-navigation)

---

### 4. First run explained ▶️

* **db** → PostgreSQL 16, database auto-created from `.env`.
* **backend** → Django dev server at `http://localhost:8000`. Auto-migrates DB on start.
* **frontend** → Next.js dev server at `http://localhost:3000`.
* **Hot-reload** → code is mounted into containers, so changes refresh instantly.

️[⬆️ Back to Navigation](#-navigation)

---

## 5. Daily Dev Workflow 🔧

### 5.1 Common commands 📝

| Task                 | Linux/macOS    | Windows (PowerShell) |
| -------------------- | -------------- | -------------------- |
| Start stack          | `make up`      | `.\dev.ps1 up`       |
| Stop stack           | `make down`    | `.\dev.ps1 down`     |
| Show logs            | `make logs`    | `.\dev.ps1 logs`     |
| Check status         | `make ps`      | `.\dev.ps1 ps`       |
| Restart backend only | `make restart` | `.\dev.ps1 restart`  |

---

### 5.2 Backend (Django) 🐍

| Task              | Linux/macOS           | Windows (PowerShell)       |
| ----------------- | --------------------- | -------------------------- |
| Apply migrations  | `make migrate`        | `.\dev.ps1 migrate`        |
| Create migrations | `make makemigrations` | `.\dev.ps1 makemigrations` |
| Create superuser  | `make superuser`      | `.\dev.ps1 superuser`      |
| Open Django shell | `make shell`          | `.\dev.ps1 shell`          |
| Bash in container | `make bash-backend`   | `.\dev.ps1 bash-backend`   |

**Adding a new Python package (important!):**

```bash
# open backend container
make bash-backend     # Linux/macOS
.\dev.ps1 bash-backend  # Windows

# install package
pip install <package>

# freeze to requirements.txt
pip freeze > requirements.txt

# exit container and rebuild backend image
exit
docker compose -f docker-compose.dev.yml build backend
```

---

### 5.3 Frontend (Next.js) ⚛️

| Task                 | Linux/macOS          | Windows (PowerShell)      |
| -------------------- | -------------------- | ------------------------- |
| Open container shell | `make bash-frontend` | `.\dev.ps1 bash-frontend` |

**Adding a new JS/TS package:**

```bash
make bash-frontend       # Linux/macOS
.\dev.ps1 bash-frontend  # Windows

npm install <package>
```

> If using Yarn or PNPM, run `yarn add <pkg>` or `pnpm add <pkg>` inside the container.

---

### 5.4 Database (Postgres) 🐘

| Task             | Linux/macOS | Windows (PowerShell) |
| ---------------- | ----------- | -------------------- |
| Open psql client | `make psql` | `.\dev.ps1 psql`     |

Default creds from `.env`:

* Host: `localhost`
* Port: `5432`
* User: `postgres`
* Password: `postgres`
* DB: `sticker_cases`

**Reset DB (⚠️ deletes all data):**

```bash
docker compose -f docker-compose.dev.yml down -v
make up              # Linux/macOS
.\dev.ps1 up         # Windows
```

### 5.5 Database GUI (pgAdmin) 📊

We include **pgAdmin** for local development — a browser-based GUI to inspect PostgreSQL.

**Access:**
👉 [http://localhost:5050](http://localhost:5050)

**Login credentials** (from `.env`):

* Email: `admin@gmail.com`
* Password: `admin`

**Connect pgAdmin to our Postgres service:**

1. After logging in, click **Add New Server**.
2. In **General → Name**: `Sticker Cases DB`
3. In **Connection tab**:

   * **Host**: `db`
   * **Port**: `5432`
   * **Username**: `postgres`
   * **Password**: `postgres`
4. Save → you’ll now see the `sticker_cases` database with all Django tables.

️[⬆️ Back to Navigation](#-navigation)

---

## 6. Common tasks 🔄

* **Rebuild after dependency change:**

```bash
docker compose -f docker-compose.dev.yml build backend
docker compose -f docker-compose.dev.yml build frontend
```

* **Restart only backend:**

```bash
make restart        # Linux/macOS
.\dev.ps1 restart   # Windows
```

️[⬆️ Back to Navigation](#-navigation)

---

## 7. One-time setup for Windows devs 🪟

PowerShell blocks scripts by default. Run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

After that, `.\dev.ps1 <command>` works normally.

️[⬆️ Back to Navigation](#-navigation)

---

## 8. Repo structure 📂

```
sticker-cases/
├─ frontend/            # Next.js app
│  ├─ Dockerfile
│  └─ .dockerignore
├─ backend/             # Django project
│  ├─ Dockerfile
│  ├─ entrypoint.sh     # migrations + superuser + runserver
│  └─ .dockerignore
├─ docker-compose.dev.yml
├─ .env                 # Compose envs (dev)
├─ Makefile             # shortcuts (Linux/macOS)
├─ dev.ps1              # shortcuts (Windows PowerShell)
└─ README.md            # (this file)
```

️[⬆️ Back to Navigation](#-navigation)