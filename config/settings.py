# config/settings.py

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

# Configurazioni UI
UI_SETTINGS = {
    'items_per_page': 20,
    'default_currency': 'EUR',
    'date_format': '%d/%m/%Y'
}

# Configurazioni business logic
BUSINESS_SETTINGS = {
    'min_margin_percentage': 20,
    'max_vehicle_age_years': 5,
    'max_mileage_km': 100000
}