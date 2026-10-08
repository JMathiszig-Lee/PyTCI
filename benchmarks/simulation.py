"""Run with: python -m benchmarks.simulation (times are machine-dependent)."""

from statistics import median
from timeit import repeat

from PyTCI.models import propofol


def legacy_wait(patient, seconds):
    for _ in range(seconds):
        x1k10 = patient.x1 * patient.k10
        x1k12 = patient.x1 * patient.k12
        x1k13 = patient.x1 * patient.k13
        x2k21 = patient.x2 * patient.k21
        x3k31 = patient.x3 * patient.k31
        ce_in = patient.x1 * patient.keo
        ce_out = patient.xeo * patient.keo
        patient.x1 += x2k21 - x1k12 + x3k31 - x1k13 - x1k10
        patient.x2 += x1k12 - x2k21
        patient.x3 += x1k13 - x3k31
        patient.xeo += ce_in - ce_out


def run():
    def legacy():
        patient = propofol.Marsh(70)
        patient.give_drug(200)
        legacy_wait(patient, 3600)

    def cached():
        patient = propofol.Marsh(70)
        patient.give_drug(200)
        patient.wait_time(3600)

    patient = propofol.Marsh(70)
    patient.effect_bolus(4)  # Warm the unit-response cache separately.
    old = median(repeat(legacy, number=100, repeat=5)) / 100
    new = median(repeat(cached, number=100, repeat=5)) / 100
    bolus = median(repeat(lambda: patient.effect_bolus(4), number=100, repeat=5)) / 100
    print(f"One-hour washout, scalar Euler: {old * 1e6:.1f} us")
    print(
        f"One-hour washout, cached Euler: {new * 1e6:.1f} us ({old / new:.1f}x faster)"
    )
    print(f"Cached initial effect bolus: {bolus * 1e6:.1f} us")


if __name__ == "__main__":
    run()
