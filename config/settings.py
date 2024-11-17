# config/settings.py
PORTAL_CREDENTIALS = {
    'clickar': {
        'username': 'W81072F',
        'password': 'Fammiincollare!'
    },
    'ayvens': {
        'username': 'justcars',
        'password': 'Sandaliecalzini11!'
    }
}

# URL portali
PORTAL_URLS = {
    'clickar': 'https://www.clickar.biz/private',
    'ayvens': 'https://carmarket.ayvens.com'
}

# Configurazioni cache
CACHE_SETTINGS = {
    'enabled': True,
    'expiry_minutes': 30
}

# Altre configurazioni
SELENIUM_SETTINGS = {
    'implicit_wait': 10,
    'page_load_timeout': 30
}