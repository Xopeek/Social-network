import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now = datetime.datetime.now()
    return {
        'year': year_now.year
    }
