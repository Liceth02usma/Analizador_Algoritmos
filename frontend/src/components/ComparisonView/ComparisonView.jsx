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
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function ComparisonView({ comparisonData }) {
  if (!comparisonData) {
    return (
      <div className="text-center text-gray-400 py-12">
        No hay datos de comparación disponibles
      </div>
    );
  }

  const { tokens_comparison, complexity_comparison, methods_comparison, detail_comparison, execution_time } = comparisonData;

  // Datos para gráfica de tokens
  const tokensData = [
    {
      name: 'Tokens de Entrada',
      'Especializados': tokens_comparison.specialized.input,
      'Completo': tokens_comparison.complete.input
    },
    {
      name: 'Tokens de Salida',
      'Especializados': tokens_comparison.specialized.output,
      'Completo': tokens_comparison.complete.output
    },
    {
      name: 'Total',
      'Especializados': tokens_comparison.specialized.total,
      'Completo': tokens_comparison.complete.total
    }
  ];

  // Datos para gráfica de tiempo
  const timeData = [
    { name: 'Especializados', value: execution_time.specialized, fill: '#3b82f6' },
    { name: 'Completo', value: execution_time.complete, fill: '#10b981' }
  ];

  // 📊 Calcular complejidad algorítmica basada en tokens
  const calculateComplexity = (tokens) => {
    if (tokens < 1000) return 'O(1) - Constante';
    if (tokens < 5000) return 'O(log n) - Logarítmica';
    if (tokens < 15000) return 'O(n) - Lineal';
    if (tokens < 30000) return 'O(n log n) - Lineal-Logarítmica';
    if (tokens < 50000) return 'O(n²) - Cuadrática';
    return 'O(n³+) - Cúbica o superior';
  };

  const specializedComplexity = calculateComplexity(tokens_comparison.specialized.total);
  const completeComplexity = calculateComplexity(tokens_comparison.complete.total);

  const tokensDifference = tokens_comparison.percentage_difference.total;
  const complexityMatch = complexity_comparison.match;

  return (
    <div className="space-y-8 bg-gray-900 text-white p-6 rounded-lg">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">
          📊 Comparación de Análisis
        </h2>
        <p className="text-gray-400">
          {comparisonData.metadata.algorithm_name}
        </p>
      </div>

      {/* Tarjeta de Complejidad Tokens */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4 text-orange-400">
          📊 Complejidad de Consumo de Tokens
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <p className="text-gray-400 text-sm">Agentes Especializados</p>
            <p className="text-2xl font-bold text-blue-400">{specializedComplexity}</p>
            <p className="text-sm text-gray-500">{tokens_comparison.specialized.total.toLocaleString()} tokens</p>
          </div>
          <div className="space-y-2">
            <p className="text-gray-400 text-sm">Agente Completo</p>
            <p className="text-2xl font-bold text-green-400">{completeComplexity}</p>
            <p className="text-sm text-gray-500">{tokens_comparison.complete.total.toLocaleString()} tokens</p>
          </div>
        </div>
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

      {/* Gráfica de Tiempo de Ejecución */}
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

      {/* Métodos Utilizados */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 text-blue-400">
            🔧 Métodos Especializados
          </h3>
          <ul className="space-y-2">
            {Array.isArray(methods_comparison.specialized) ? (
              methods_comparison.specialized.map((method, idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="text-blue-400">•</span>
                  <span>{method}</span>
                </li>
              ))
            ) : (
              <li className="flex items-center space-x-2">
                <span className="text-blue-400">•</span>
                <span>{methods_comparison.specialized}</span>
              </li>
            )}
          </ul>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 text-green-400">
            🤖 Método Completo
          </h3>
          <p className="text-gray-300">{methods_comparison.complete}</p>
        </div>
      </div>

      {/* Métricas Detalladas */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-4">📊 Métricas Detalladas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-gray-700 rounded">
            <p className="text-gray-400 text-sm">Tokens Especializados</p>
            <p className="text-2xl font-bold text-blue-400">
              {tokens_comparison.specialized.total.toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-gray-700 rounded">
            <p className="text-gray-400 text-sm">Tokens Completo</p>
            <p className="text-2xl font-bold text-green-400">
              {tokens_comparison.complete.total.toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-gray-700 rounded">
            <p className="text-gray-400 text-sm">Ahorro/Gasto</p>
            <p className={`text-2xl font-bold ${tokensDifference < 0 ? 'text-green-400' : 'text-red-400'}`}>
              {Math.abs(tokens_comparison.difference.total).toLocaleString()}
            </p>
          </div>
          <div className="p-4 bg-gray-700 rounded">
            <p className="text-gray-400 text-sm">Diferencia %</p>
            <p className={`text-2xl font-bold ${tokensDifference < 0 ? 'text-green-400' : 'text-red-400'}`}>
              {Math.abs(tokensDifference).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Conclusión */}
      <div className="bg-gradient-to-r from-blue-900 to-purple-900 p-6 rounded-lg border border-blue-700">
        <h3 className="text-xl font-semibold mb-3">💡 Conclusión</h3>
        <p className="text-gray-200">
          {tokensDifference > 0 ? (
            <>
              Los agentes especializados utilizan <strong>{Math.abs(tokensDifference).toFixed(1)}% más tokens</strong> que el agente completo,
              pero proporcionan <strong>{detail_comparison.specialized_cases}x más detalle</strong> en el análisis con{' '}
              <strong>{detail_comparison.specialized_steps} pasos de solución</strong>.
            </>
          ) : (
            <>
              Los agentes especializados son <strong>{Math.abs(tokensDifference).toFixed(1)}% más eficientes</strong> en tokens que el agente completo,
              además de proporcionar <strong>{detail_comparison.specialized_cases}x más detalle</strong> en el análisis.
            </>
          )}
        </p>
        <div className="mt-4 pt-4 border-t border-blue-700">
          <p className="text-sm text-gray-300">
            <strong>📊 Complejidad de Tokens:</strong>
            <br />
            Especializados: <span className="text-blue-300">{specializedComplexity}</span>
            <br />
            Completo: <span className="text-green-300">{completeComplexity}</span>
          </p>
        </div>
        {!complexityMatch && (
          <p className="mt-3 text-yellow-300">
            ⚠️ Nota: Las complejidades del algoritmo difieren entre ambos métodos, revisar resultados detallados.
          </p>
        )}
      </div>
    </div>
  );
}
