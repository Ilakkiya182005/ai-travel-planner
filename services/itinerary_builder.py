from services.budget_allocator import BudgetAllocator
from retrievers.travel_retriever import TravelRetriever
from retrievers.hotel_retriever import HotelRetriever
from retrievers.activity_retriever import ActivityRetriever
from llm.prompt_templates import ITINERARY_PROMPT

class ItineraryBuilder:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.travel_retriever = TravelRetriever()
        self.hotel_retriever = HotelRetriever()
        self.activity_retriever = ActivityRetriever()

    def build(self, source, dest, budget, days, preferences):
        # Convert to proper types (from JSON they may be strings)
        try:
            budget = float(budget)
            days = int(days)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid budget or days: budget={budget}, days={days}")
        
        # 1. Determine budget splits
        limits = BudgetAllocator.allocate(budget, days)

        # 2. Retrieve Logistics (Flights & Hotels)
        best_travel = self.travel_retriever.get_best_travel(
            source, dest, limits['transport_max']
        )
        
        best_hotels = self.hotel_retriever.get_best_hotels(
            dest, limits['stay_per_night']
        )

        # 3. Retrieve Experiences (Semantic Search)
        # Using vector search to find activities matching 'preferences'
        activities = self.activity_retriever.search(
            preferences, dest, top_k=days * 2
        )

        # 4. Construct Prompt with Context (Augmentation)
        # We pass only the top choices to keep the prompt concise
        context = {
            "source": source,
            "dest": dest,
            "days": days,
            "budget": budget,
            "prefs": preferences,
            "flights": best_travel[0] if best_travel else "No flights in budget found",
            "hotel": best_hotels[0] if best_hotels else "No hotels in budget found",
            "activities": [
                {"name": a['Place'], "desc": a['Place_desc'], "fee": a['entry_fee']} 
                for a in activities
            ]
        }

        final_prompt = ITINERARY_PROMPT.format(**context)
        print("DEBUG: Final Prompt for LLM:\n", final_prompt)  # Debugging line to check the prompt  
        # 5. Generate and return (Generation)
        return self.llm.generate_itinerary(final_prompt)