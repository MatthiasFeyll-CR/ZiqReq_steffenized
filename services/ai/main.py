"""AI service entry point — starts gRPC server + event consumers with Django ORM initialized."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings.development")
django.setup()


def main():
    pass


if __name__ == "__main__":
    main()
