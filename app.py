import streamlit as st
from services.intent_service import IntentService
from services.itinerary_builder import ItineraryBuilder
from llm.llm_client import LLMClient
from config.settings import OPENAI_API_KEY

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")

# Initialize Services once
@st.cache_resource
def init_services():
    return IntentService(OPENAI_API_KEY), ItineraryBuilder(LLMClient(OPENAI_API_KEY))

intent_service, builder = init_services()

st.title("✈️ AI Travel Itinerary Chatbot")

# 1. Initialize Persistent State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "travel_params" not in st.session_state:
    st.session_state.travel_params = {
        "source": None, "dest": None, "days": None, "budget": None, "preferences": None
    }

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_input := st.chat_input("Where to next?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # 2. Extract NEW intent from current message
            new_params = intent_service.extract_params(user_input)
            
            # 3. MERGE new params with stored state (Update only what user provided)
            for key, value in new_params.items():
                if value is not None:
                    st.session_state.travel_params[key] = value
            
            params = st.session_state.travel_params
            missing = [k for k, v in params.items() if v is None]
            
            if missing:
                response = f"Got it! To plan your trip to **{params['dest'] or 'your destination'}**, I still need to know: **{', '.join(missing)}**."
            else:
                try:
                    # 4. Generate Itinerary
                    response = builder.build(
                        source=params['source'],
                        dest=params['dest'],
                        budget=params['budget'],
                        days=params['days'],
                        preferences=params['preferences']
                    )
                    print("response", response)  # Debugging line to check the final response from the builder
                    # Optional: Reset destination after planning to allow a new trip request
                    # st.session_state.travel_params["dest"] = None 
                except Exception as e:
                    response = f"❌ Error: {e}"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})