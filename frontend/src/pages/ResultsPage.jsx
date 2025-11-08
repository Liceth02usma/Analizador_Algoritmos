 // src/pages/ResultsPage.js
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  if (!result) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>No hay resultados disponibles</h2>
        <button onClick={() => navigate("/")}>Volver</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Resultado del análisis</h2>
      <pre
        style={{
          backgroundColor: "#f4f4f4",
          padding: "15px",
          borderRadius: "10px",
          textAlign: "left",
        }}
      >
        {JSON.stringify(result, null, 2)}
      </pre>
      <button onClick={() => navigate("/")}>Volver</button>
    </div>
  );
}

export default ResultsPage;

