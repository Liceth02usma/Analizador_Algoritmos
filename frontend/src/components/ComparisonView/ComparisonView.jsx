import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

export default function ComparisonView({ comparisonData }) {
  if (!comparisonData) {
    return (
      <div className="text-center text-gray-400 py-12">
        No hay datos de comparación disponibles
      </div>
    );
  }

  const { 
    tokens_comparison, 
    execution_time,
    complete_agent_analysis,
    metadata
  } = comparisonData;

  // Validación de datos con fallbacks
  const tokensData = [
    {
      name: 'Entrada',
      'Especializados': tokens_comparison?.specialized?.input || 0,
      'Completo': tokens_comparison?.complete?.input || 0
    },
    {
      name: 'Salida',
      'Especializados': tokens_comparison?.specialized?.output || 0,
      'Completo': tokens_comparison?.complete?.output || 0
    },
    {
      name: 'Total',
      'Especializados': tokens_comparison?.specialized?.total || 0,
      'Completo': tokens_comparison?.complete?.total || 0
    }
  ];

  const timeData = [
    { name: 'Especializados', value: execution_time?.specialized || 0, fill: '#3b82f6' },
    { name: 'Completo', value: execution_time?.complete || 0, fill: '#10b981' }
  ];

  const tokensDifference = tokens_comparison?.percentage_difference?.total || 0;

  return (
    <div className="space-y-8 bg-gray-900 text-white p-6 rounded-lg">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">
          📊 Comparación de Análisis
        </h2>
        <p className="text-gray-400">
          {comparisonData?.metadata?.algorithm_name || 'Algoritmo'}
        </p>
      </div>

      {/* Gráfica de Tokens */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">📈 Comparación de Tokens</h3>
        <div className="mb-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Diferencia Total:</span>
            <span className={`text-xl font-bold ${tokensDifference > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {tokensDifference > 0 ? '+' : ''}{tokensDifference.toFixed(1)}%
            </span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={tokensData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              labelStyle={{ color: '#fff' }}
            />
            <Legend />
            <Bar dataKey="Especializados" fill="#3b82f6" />
            <Bar dataKey="Completo" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfica de Tiempo */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">⏱️ Tiempo de Ejecución</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={timeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value.toFixed(2)}s`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {timeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* 🤖 Análisis del Agente Completo */}
      {complete_agent_analysis && (
        <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="text-4xl">🤖</div>
            <div>
              <h3 className="text-2xl font-bold text-green-400">
                Análisis del Agente Completo
              </h3>
              <p className="text-gray-400 text-sm">
                Resultado sin especialización por casos
              </p>
            </div>
          </div>

          {/* Información General */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Algoritmo</p>
              <p className="text-lg font-semibold text-green-300">
                {complete_agent_analysis.algorithm_name || 'N/A'}
              </p>
            </div>

            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Categoría</p>
              <p className="text-sm text-gray-300">
                {complete_agent_analysis.algorithm_category || 'N/A'}
              </p>
            </div>

            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Tipo</p>
              <p className="text-sm text-gray-300">
                {complete_agent_analysis.algorithm_type === 'iterative' ? 'Iterativo' : 'Recursivo'}
              </p>
            </div>

            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Propósito</p>
              <p className="text-xs text-gray-300">
                {complete_agent_analysis.algorithm_purpose || 'No especificado'}
              </p>
            </div>
          </div>

          {/* Complejidad Final Destacada */}
          <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 border-2 border-green-500 p-6 rounded-lg mb-6">
            <h4 className="text-sm font-semibold text-green-400 mb-3">🎯 Complejidad Final del Algoritmo</h4>
            <div className="text-center">
              <p className="text-4xl font-bold text-green-300 mb-2">
                {complete_agent_analysis.final_complexity || 'N/A'}
              </p>
              <p className="text-sm text-gray-400">
                Complejidad temporal determinada por el agente completo
              </p>
            </div>
          </div>

          {/* Notación Asintótica */}
          <div className="bg-gray-800/50 p-6 rounded-lg mb-6">
            <h4 className="text-lg font-semibold text-green-400 mb-4">📊 Notación Asintótica</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-900/50 rounded-lg border-l-4 border-green-500">
                <p className="text-xs text-gray-400 mb-1">Mejor Caso (Ω)</p>
                <p className="text-xl font-bold text-green-300">
                  {complete_agent_analysis.asymptotic_best || 'N/A'}
                </p>
              </div>

              <div className="p-4 bg-gray-900/50 rounded-lg border-l-4 border-yellow-500">
                <p className="text-xs text-gray-400 mb-1">Caso Promedio (Θ)</p>
                <p className="text-xl font-bold text-yellow-300">
                  {complete_agent_analysis.asymptotic_average || 'N/A'}
                </p>
              </div>

              <div className="p-4 bg-gray-900/50 rounded-lg border-l-4 border-red-500">
                <p className="text-xs text-gray-400 mb-1">Peor Caso (O)</p>
                <p className="text-xl font-bold text-red-300">
                  {complete_agent_analysis.asymptotic_worst || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Ecuación */}
          {complete_agent_analysis.equation && complete_agent_analysis.equation !== 'No disponible' && (
            <div className="bg-gray-800/50 p-4 rounded-lg mb-6">
              <p className="text-xs text-gray-400 mb-2">Ecuación de Recurrencia/Sumatoria</p>
              <div className="bg-gray-900/50 p-4 rounded border border-gray-700">
                <code className="text-green-300 font-mono text-sm break-all">
                  {complete_agent_analysis.equation}
                </code>
              </div>
            </div>
          )}

          {/* Método de Solución */}
          <div className="bg-gray-800/50 p-4 rounded-lg mb-6">
            <p className="text-xs text-gray-400 mb-2">Método de Solución</p>
            <p className="text-sm text-gray-200">
              {complete_agent_analysis.solution_method || 'No especificado'}
            </p>
          </div>

          {/* Pasos de Solución */}
          {complete_agent_analysis.solution_steps && complete_agent_analysis.solution_steps.length > 0 && (
            <div className="bg-gray-800/50 p-4 rounded-lg mb-6">
              <p className="text-xs text-gray-400 mb-3">Pasos de Solución ({complete_agent_analysis.solution_steps.length})</p>
              <ol className="space-y-2 max-h-64 overflow-y-auto">
                {complete_agent_analysis.solution_steps.map((step, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="text-green-400 font-bold flex-shrink-0">{idx + 1}.</span>
                    <span className="text-gray-300 text-sm">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Métricas de Ejecución */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">⏱️ Tiempo de Ejecución</p>
              <p className="text-2xl font-semibold text-green-300">
                {complete_agent_analysis.execution_time?.toFixed(3) || '0.000'}s
              </p>
            </div>

            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">🎫 Tokens Utilizados</p>
              <p className="text-2xl font-semibold text-green-300">
                {complete_agent_analysis.tokens_used?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
