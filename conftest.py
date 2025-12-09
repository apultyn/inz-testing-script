import pytest
import pandas as pd
import matplotlib.pyplot as plt
import time
from dataclasses import asdict

class PerformanceRecorder:
    def __init__(self):
        self.results = []

    def record(self, service_name, endpoint, method, latency, status):
        self.results.append({
            "service": service_name,
            "endpoint": endpoint,
            "method": method,
            "latency": latency,
            "status": status
        })

    def save_report(self):
        if not self.results:
            return

        df = pd.DataFrame(self.results)
        df.to_csv("results/performance_report.csv", index=False)

        self.generate_charts(df)

    def generate_charts(self, df):
        df['full_endpoint'] = df['service'] + " " + df['method'] + " " + df['endpoint']

        avg_times = df.groupby('full_endpoint')['latency'].mean().sort_values()

        plt.figure(figsize=(12, 8))

        colors = ['green' if x < 0.2 else 'orange' if x < 1.0 else 'red' for x in avg_times]

        avg_times.plot(kind='barh', color=colors)

        plt.title('Średni czas odpowiedz API (Latencja)')
        plt.xlabel('Sekundy')
        plt.ylabel('Endpoint')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.savefig("results/performance_chart.png")
        print("[INFO] Wygenerowano wykres performance_chart.png")

@pytest.fixture(scope="session")
def performance_metrics():
    recorder = PerformanceRecorder()
    yield recorder
    recorder.save_report()