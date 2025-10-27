import os
from pathlib import Path

from dotenv import load_dotenv

from cryptography.fernet import Fernet

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Prod | Dev init
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# RICH SETUP
mode = "DEV" if DEBUG else "PROD"
color = "green" if DEBUG else "red"

# HOSTS Setup
HOSTS = os.getenv("DJANGO_HOSTS", "localhost,127.0.0.1").split(",")
HOSTS_URLS = os.getenv("DJANGO_HOSTS_URLS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# ALLOWED HOSTS for Prod | Dev
ALLOWED_HOSTS = HOSTS

INSTALLED_APPS = [
    # Native Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "daphne",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "channels",
    # Apps
    "cases",
    "packs",
    "users",
    "wallet",
    "upgrade",
    "rolls"
]

# MIDDLEWARE THE ORDER IS IMPORTANT!!!!!!!
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# TEMPLATES FOR EMAILS OR ANYTHING ELSE
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# DB SETUP
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "sticker_cases"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "qwerty"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        # helpful timeouts for dev
        "CONN_MAX_AGE": 0,  # 0 = no persistent connections
        "OPTIONS": {},  # extra psycopg options if needed later
    }
}

# PASS VALIDATION DEFAULT OF DJANGO
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.CustomUser"

# INTERNALIZATION
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# STATIC SETUP
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECRET_ENCRYPTION_KEY = Fernet.generate_key()

# ============================ Cors & Rest setups =================================
SESSION_COOKIE_NAME = "sc_sessionid"
SESSION_COOKIE_SAMESITE = "Lax"  # or "None" if we use a different site/port and HTTPS
SESSION_COOKIE_SECURE = False  # True in production (HTTPS)
CSRF_COOKIE_SECURE = False  # True in production (HTTPS)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CORS_ALLOWED_ORIGINS = HOSTS_URLS
CSRF_TRUSTED_ORIGINS = HOSTS_URLS

CELERY_BROKER_URL = os.getenv(
    "DJANGO_BROKER_URL", default="redis://localhost:6379/0"
)  # вместо localhost название сервиса
CELERY_ACCEPT_CONTENT = [
    "pickle",
    "application/json",
]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_EVENT_SERIALIZER = "pickle"

APPEND_SLASH = False

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Sticker Cases API",
    "DESCRIPTION": "Свага для фронта",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ========================= Startup Dashboard (Rich + PyFiglet) =========================
if os.environ.get("RUN_MAIN") == "true":
    import getpass
    import platform
    import socket

    import django
    import pyfiglet
    from rich import box
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()


    def yes_no(val: bool) -> str:  # noqa: E303
        return f"[green]Yes[/green]" if val else "[red]No[/red]"  # noqa: F541


    def list_to_columns(items: list, title: str | None = None, color: str = "cyan") -> Panel:  # noqa: E303
        if not items:
            return Panel.fit(
                "[dim]— none —[/dim]",
                title=title,
                border_style="grey37",
                box=box.ROUNDED,
            )
        bullets = [f"[{color}]•[/] {i}" for i in items]
        return Panel.fit(
            Columns(bullets, equal=True, expand=True),
            title=title,
            border_style="grey37",
            box=box.ROUNDED,
        )


    mode = "DEV" if DEBUG else "PROD"  # noqa: E303
    color = "green" if DEBUG else "red"

    py_ver = platform.python_version()
    dj_ver = django.get_version()
    user = getpass.getuser()
    host = platform.node()
    os_str = f"{platform.system()} {platform.release()}"

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = "N/A"

    # pick up LAN_IP (if provided via compose up-lan)
    lan_ip = os.getenv("LAN_IP")

    db = DATABASES.get("default", {})
    db_engine = db.get("ENGINE", "N/A")
    db_name = db.get("NAME", "N/A")

    installed_apps = INSTALLED_APPS
    native_apps = [a for a in installed_apps if a.startswith("django.")]
    third_party_apps = [a for a in installed_apps if not a.startswith("django.")]

    # --------- ASCII Banner ---------
    banner = pyfiglet.figlet_format("Sticker Cases")
    console.print(f"[bold cyan]{banner}[/bold cyan]")

    # --------- Main Info Table ---------
    info = Table.grid(padding=(0, 2))
    info.add_row("Mode", f"[bold {color}]{mode}[/bold {color}]")
    info.add_row("DEBUG", yes_no(DEBUG))
    info.add_row("Django", f"[bold]{dj_ver}[/bold]")
    info.add_row("Python", f"[bold]{py_ver}[/bold]")
    info.add_row("User", f"[cyan]{user}[/cyan]")
    info.add_row("Machine", f"[cyan]{host}[/cyan]")
    info.add_row("OS", f"[cyan]{os_str}[/cyan]")
    info.add_row("Local IP", f"[cyan]{local_ip}[/cyan]")
    if lan_ip:
        info.add_row("LAN IP (env)", f"[cyan]{lan_ip}[/cyan]")
        info.add_row(
            "LAN URLs",
            f"[cyan]http://{lan_ip}:3000[/cyan]  |  [cyan]http://{lan_ip}:8000[/cyan]",
        )

    info.add_row("Allowed Hosts", f"[yellow]{', '.join(ALLOWED_HOSTS) or '—'}[/yellow]")
    info.add_row("CORS Origins", f"[yellow]{', '.join(CORS_ALLOWED_ORIGINS) or '—'}[/yellow]")
    info.add_row("Timezone", f"[bold]{TIME_ZONE}[/bold]")
    info.add_row("Language", f"[bold]{LANGUAGE_CODE}[/bold]")
    info.add_row("Database Engine", f"[bold]{db_engine}[/bold]")
    info.add_row("Database Name", f"[bold]{db_name}[/bold]")
    info.add_row("Installed Apps", f"[green]{len(installed_apps)}[/green]")
    info.add_row("Middleware", f"[green]{len(MIDDLEWARE)}[/green]")

    console.print(
        Panel.fit(
            info,
            title=":rocket: [bold cyan]Sticker Cases Backend[/bold cyan]",
            subtitle="© 2025 Sticker Cases",
            border_style=color,
            box=box.DOUBLE,
        )
    )

    # --------- Detailed Panels ---------
    console.print(
        Columns(
            [
                list_to_columns(native_apps, title="[bold]Django Built-ins[/bold]", color="cyan"),
                list_to_columns(
                    third_party_apps,
                    title="[bold]Third-party & Local Apps[/bold]",
                    color="green",
                ),
            ],
            expand=True,
        )
    )

    if MIDDLEWARE:
        mw_table = Table.grid(padding=(0, 1))
        for i, mw in enumerate(MIDDLEWARE):
            mw_table.add_row(f"[white]{i + 1:02}.[/] {mw}")
        console.print(
            Panel.fit(
                mw_table,
                title="[bold]Middleware Order[/bold]",
                border_style="grey37",
                box=box.ROUNDED,
            )
        )
    # ==============================================================================
