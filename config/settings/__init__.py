"""Dealwright settings.

Split per HackSoft styleguide: `base` (shared), `development`, `testing`,
`production`. The active module is chosen explicitly:

- manage.py       -> config.settings.development
- pytest          -> config.settings.testing (pyproject)
- wsgi/asgi (prod)-> config.settings.production
"""
