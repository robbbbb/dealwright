"""Dealwright settings.

Split per HackSoft styleguide: `base` (shared), `development`, `testing`,
`production`. The active module is chosen explicitly:

- manage.py       -> dealwright.settings.development
- pytest          -> dealwright.settings.testing (pyproject)
- wsgi/asgi (prod)-> dealwright.settings.production
"""
