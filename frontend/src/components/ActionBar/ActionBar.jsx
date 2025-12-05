import React from "react";

export default function ActionBar() {
  return (
    <aside className="w-1/6 bg-gray-900 border-l border-gray-700 flex flex-col items-center justify-center gap-4 p-4">
      <button className="bg-purple-700 hover:bg-purple-800 text-white px-4 py-2 rounded-full shadow-md text-sm w-40 text-center">
        ⚙️ Comprobar Algoritmo
      </button>
    </aside>
  );
}
