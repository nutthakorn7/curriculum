"""Shared minimal auto-scaling simulation engine.

Models exactly the one concept this lesson is about: a fleet behind a load
balancer that reacts to load by adding instances, bounded by a configured
minimum and maximum capacity. This is an original, deliberately simplified
teaching model of Cloud Foundations' "target group + Auto Scaling Group"
behavior (deterministic, synchronous, no timers, no real AWS calls) — it is
not AWS code and does not simulate ALB/ASG internals beyond the concept
needed for this exercise.

Scaling rule: every UNITS_PER_INSTANCE load units accumulated triggers +1
instance, capped at MAX_INSTANCES. This stands in for a CPU-utilization
scaling policy (e.g., "add capacity when average CPU exceeds a threshold")
without needing real CPU load or wall-clock timers.
"""

MIN_INSTANCES = 2
MAX_INSTANCES = 6
UNITS_PER_INSTANCE = 10  # every 10 load units triggers one more instance


class AutoScaler:
    def __init__(self):
        self.load_units = 0
        self.current_instances = MIN_INSTANCES

    def generate_load(self):
        """Simulate one CPU-intensive job request hitting the fleet."""
        self.load_units += 1
        target = MIN_INSTANCES + (self.load_units // UNITS_PER_INSTANCE)
        self.current_instances = min(target, MAX_INSTANCES)
        return self.state()

    def state(self):
        return {
            "load_units": self.load_units,
            "current_instances": self.current_instances,
            "min_instances": MIN_INSTANCES,
            "max_instances": MAX_INSTANCES,
        }
