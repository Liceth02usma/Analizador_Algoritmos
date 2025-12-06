"""
Motor Matemático Determinista para Resolución de Sumatorias
Usa SymPy para garantizar precisión algebraica del 100%
"""

import re
from typing import Dict, List, Tuple, Optional
from sympy import symbols, summation, simplify, expand, factor, latex
from sympy.abc import n, i, j, k  # Variables comunes

# Definimos símbolos de constantes (c0, c1, c2, ..., c20)
c_symbols = symbols("c0:21", real=True)
c_map = {f"c{i}": c_symbols[i] for i in range(21)}


class SummationSolver:
    """
    Resuelve sumatorias algebraicas usando SymPy.

    Soporta:
    - Sumatorias anidadas: SUM(i=1,n)[SUM(j=1,i)[...]]
    - Términos constantes: c1, c2*n
    - Expresiones complejas: c1 + c2*n + SUM(...)
    """

    def __init__(self):
        self.n = n
        self.variables = {"n": n, "i": i, "j": j, "k": k}
        self.constants = c_map

    def parse_and_solve(self, expression: str) -> Dict:
        """
        Pipeline completo: Parsea -> Resuelve -> Simplifica

        Args:
            expression: String con sumatorias. Ej: "c1 + SUM(i=1,n)[c2*i]"

        Returns:
            Dict con:
                - original: Expresión original
                - steps: Lista de pasos intermedios
                - expanded: Expresión expandida
                - simplified: Resultado final simplificado
                - latex: Versión LaTeX del resultado
                - big_o: Complejidad asintótica
        """

        steps = []

        # PASO 1: Limpiar espacios
        clean_expr = expression.replace(" ", "")
        steps.append(
            {
                "step": 1,
                "description": "Expresión original limpia",
                "expression": clean_expr,
            }
        )

        # PASO 2: Resolver sumatorias recursivamente (de adentro hacia afuera)
        resolved_expr, resolution_steps = self._resolve_summations(clean_expr)
        steps.extend(resolution_steps)

        # PASO 3: Convertir a expresión SymPy
        sympy_expr = self._to_sympy(resolved_expr)

        # PASO 4: Expandir
        expanded = expand(sympy_expr)
        steps.append(
            {
                "step": len(steps) + 1,
                "description": "Expandir productos y simplificar fracciones",
                "expression": str(expanded),
            }
        )

        # PASO 5: Simplificar agrupando términos
        simplified = simplify(expanded)
        steps.append(
            {
                "step": len(steps) + 1,
                "description": "Agrupar términos por potencias de n",
                "expression": str(simplified),
            }
        )

        # PASO 6: Calcular Big-O
        big_o = self._extract_big_o(simplified)

        return {
            "original": expression,
            "steps": steps,
            "expanded": str(expanded),
            "simplified": str(simplified),
            "latex": latex(simplified),
            "big_o": big_o,
            "sympy_object": simplified,
        }

    def _resolve_summations(self, expr: str) -> Tuple[str, List[Dict]]:
        """
        Resuelve sumatorias de forma recursiva (innermost first).

        Returns:
            (expresión_resuelta, lista_de_pasos)
        """
        steps = []
        step_counter = 2  # Empezamos desde paso 2

        # Regex para capturar SUM(var=inicio,fin)[cuerpo]
        pattern = r"SUM\((\w)=(\w+),(\w+)\)\[([^\[\]]+)\]"

        max_iterations = 10  # Prevenir loops infinitos
        iteration = 0

        while "SUM" in expr and iteration < max_iterations:
            iteration += 1

            # Encontrar la sumatoria más interna (sin SUM anidado en el cuerpo)
            matches = list(re.finditer(pattern, expr))

            if not matches:
                break

            # Procesamos la primera sumatoria encontrada
            match = matches[0]
            var = match.group(1)  # 'i', 'j', etc.
            start = match.group(2)  # '1', '0', etc.
            end = match.group(3)  # 'n', 'n-1', 'i', etc.
            body = match.group(4)  # 'c2*i', 'c3+c4', etc.

            # Resolver esta sumatoria específica
            result = self._solve_single_summation(var, start, end, body)

            steps.append(
                {
                    "step": step_counter,
                    "description": f"Resolver SUM({var}={start},{end})[{body}]",
                    "formula_applied": self._get_formula_name(body, var),
                    "result": result,
                }
            )
            step_counter += 1

            # Reemplazar en la expresión original
            expr = expr[: match.start()] + f"({result})" + expr[match.end() :]

        return expr, steps

    def _solve_single_summation(self, var: str, start: str, end: str, body: str) -> str:
        """
        Resuelve una sumatoria individual usando SymPy.

        Ejemplo:
            var='i', start='1', end='n', body='c2*i'
            -> Retorna: 'c2*n*(n+1)/2'
        """

        # Convertir strings a símbolos SymPy
        var_symbol = self.variables.get(var, symbols(var, integer=True))

        # Parsear límites (pueden ser 'n', 'n-1', 'i', etc.)
        start_expr = self._to_sympy(start)
        end_expr = self._to_sympy(end)

        # Parsear el cuerpo de la sumatoria
        body_expr = self._to_sympy(body)

        # Resolver con SymPy
        result = summation(body_expr, (var_symbol, start_expr, end_expr))

        # Simplificar
        result_simplified = simplify(result)

        return str(result_simplified)

    def _to_sympy(self, expr_str: str):
        """
        Convierte un string a expresión SymPy.

        Maneja:
        - Constantes: c1, c2, c3
        - Variables: n, i, j
        - Operaciones: +, -, *, /, ^, **
        """

        # Reemplazar ^ por ** (notación Python)
        expr_str = expr_str.replace("^", "**")

        # Crear namespace con todas las constantes y variables
        namespace = {**self.constants, **self.variables}

        try:
            # Usar sympify de forma segura
            from sympy import sympify

            return sympify(expr_str, locals=namespace)
        except Exception as e:
            raise ValueError(f"No se pudo parsear: '{expr_str}'. Error: {e}")

    def _get_formula_name(self, body: str, var: str) -> str:
        """
        Identifica qué fórmula de serie se aplicó.
        """

        body_clean = body.replace(" ", "")

        # Patrón de constante pura
        if var not in body_clean or body_clean.replace(var, "").replace(
            "*", ""
        ).replace("c", "").replace("0123456789", ""):
            return "Sumatoria de constante: Σc = c*n"

        # Patrón lineal
        if f"*{var}" in body_clean or f"{var}*" in body_clean:
            if f"{var}**2" not in body_clean and f"{var}^2" not in body_clean:
                return "Serie aritmética: Σi = n(n+1)/2"

        # Patrón cuadrático
        if f"{var}**2" in body_clean or f"{var}^2" in body_clean:
            return "Serie cuadrática: Σi² = n(n+1)(2n+1)/6"

        return "Fórmula general de sumatoria"

    def _extract_big_o(self, sympy_expr) -> str:
        """
        Extrae la complejidad asintótica (término dominante).
        """

        # Expandir para ver todos los términos
        expanded = expand(sympy_expr)

        # Obtener el grado del polinomio en 'n'
        from sympy import degree, poly

        try:
            p = poly(expanded, n)
            deg = degree(p, n)

            if deg == 0:
                return "O(1)"
            elif deg == 1:
                return "O(n)"
            elif deg == 2:
                return "O(n²)"
            elif deg == 3:
                return "O(n³)"
            else:
                return f"O(n^{deg})"
        except:
            # Si no es un polinomio estándar
            return "O(f(n))"


# ============================================================================
# 🧪 TESTS
# ============================================================================


def test_solver():
    """
    Suite de pruebas con casos reales de algoritmos.
    """

    solver = SummationSolver()

    test_cases = [
        {
            "name": "Insertion Sort - Peor Caso",
            "expression": "c1 + c2*n + SUM(i=2,n)[c3 + c4 + c5 + SUM(j=1,i-1)[c6 + c7] + c8] + c9",
            "expected_big_o": "O(n²)",
        },
        {
            "name": "Bubble Sort - Peor Caso",
            "expression": "c1 + SUM(i=0,n-1)[c2 + SUM(j=0,n-i-1)[c3 + c4 + c5]]",
            "expected_big_o": "O(n²)",
        },
        {
            "name": "Suma Simple",
            "expression": "c1 + SUM(i=1,n)[c2]",
            "expected_big_o": "O(n)",
        },
        {
            "name": "Loop Lineal",
            "expression": "c1 + SUM(i=1,n)[c2 + c3*i]",
            "expected_big_o": "O(n²)",
        },
    ]

    print("=" * 80)
    print("🧪 PRUEBAS DEL MOTOR MATEMÁTICO")
    print("=" * 80)

    for test in test_cases:
        print(f"\n📌 TEST: {test['name']}")
        print(f"   Input: {test['expression']}")

        try:
            result = solver.parse_and_solve(test["expression"])

            print(f"\n   ✅ Resultado Simplificado:")
            print(f"      {result['simplified']}")
            print(
                f"\n   📊 Complejidad: {result['big_o']} (Esperado: {test['expected_big_o']})"
            )

            print(f"\n   📝 Pasos de Resolución:")
            for step in result["steps"]:
                print(f"      {step['step']}. {step['description']}")
                if "formula_applied" in step:
                    print(f"         Fórmula: {step['formula_applied']}")
                    print(f"         Resultado: {step['result']}")

            print("\n" + "-" * 80)

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            print("-" * 80)


if __name__ == "__main__":
    test_solver()
