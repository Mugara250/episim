from app.workers import celery_app


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> str:
    """Smoke-test task confirming the worker can pick up jobs from Redis."""
    return "pong"
