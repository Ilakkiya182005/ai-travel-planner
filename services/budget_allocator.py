class BudgetAllocator:
    @staticmethod
    def allocate(total_budget, days):
        # Weighted allocation logic
        allocations = {
            "transport_max": total_budget * 0.35,  # Round trip
            "stay_per_night": (total_budget * 0.40) / max(1, days - 1),
            "activities_total": total_budget * 0.25
        }
        return allocations