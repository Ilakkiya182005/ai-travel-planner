import React from "react";
import Chat from "./components/Chat";
import "./styles/style.css";

function App() {
  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>✈️ AI Travel Planner</h1>
          <p className="subtitle">
            Plan your perfect trip with AI-powered recommendations
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="main-content">
        <Chat />
      </main>
    </div>
  );
}

export default App;