from . import create_app

# Для совместимости с некоторыми инструментами
app = create_app()

if __name__ == '__main__':
    # Локальный запуск без DispatcherMiddleware
    app.run(debug=True)