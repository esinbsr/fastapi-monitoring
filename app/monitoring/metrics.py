# le fichier qui centralise toutes les métrics prometheus

from prometheus_client import Counter, Gauge, Histogram, Info
import time

app_info = Info('fastapi_app_info', 'Information about the FasAPI application')

# utilisation de counter pour le crud car ce sont que des valurs qui augmentent et ne diminuent jamais, pareil pour les erreurs
items_created_total = Counter("items_created_total", "Total items created")
items_read_total = Counter("items_read_total", "Total items read")
items_updated_total = Counter("items_updated_total", "Total items updated")
items_deleted_total = Counter("items_deleted_total", "Total items deleted")

# gauge pour l'état courant, car ca monte et ca decend
items_total = Gauge("items_total", "Current number of items in database")

#  histogram pour la distribution
items_price_histogram = Histogram(
    "items_price_histogram",
    "Distribution of item prices",
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000],
)

http_errors_total = Counter(
    "http_errors_total",
    "Total HTTP errors by type",
    ["type"]
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
)

class DatabaseQueryTimer:
    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        db_query_duration_seconds.observe(time.time() - self.start_time)