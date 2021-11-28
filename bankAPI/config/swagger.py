template = {
    "swagger": "2.0",
    "info": {
        "title": "Bank Employee API",
        "description": "API for Bank Employees to perform basic Bank Operations like retrieve balance",
        "contact": {
            "responsibleOrganization": "LocalFounder",
            "responsibleDeveloper": "Abuton",
            "email": "alaroabubakarolayemi@gmail.com",
            "url": "www.github.com/Abuton",
        },
        "termsOfService": "www.github.com/Abuton",
        "version": "1.0"
    },
    "basePath": "/",  # base bash for routes
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}
