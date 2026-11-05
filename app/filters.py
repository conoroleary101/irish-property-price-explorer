from datetime import datetime

def euro(value):
    if value is None:
        return "N/A"
    try:
        return f"€{int(value):,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def dateformat(value):
    if not value:
        return "N/A"
    try:
        # Assuming value is a string in 'YYYY-MM-DD' format
        dt = datetime.strptime(str(value), '%Y-%m-%d')
        return dt.strftime('%d %b %Y')
    except ValueError:
        return value

def init_app(app):
    app.add_template_filter(euro, "euro")
    app.add_template_filter(dateformat, "dateformat")