import re
from typing import List, Dict, Any
from sympy import symbols, sympify, O, limit, oo, log
from pydantic import BaseModel, Field

# ==========================================
# MODELOS DE DATOS (Mismos que el Agente)
# ==========================================


class ComplexityCaseInput(BaseModel):
    case_name: str
    efficiency_function: str


class ComplexityInput(BaseModel):
    algorithm_name: str
    cases: List[ComplexityCaseInput]


class AsymptoticResult(BaseModel):
    case_name: str
    notation_type: str = Field(description="Tipo de cota: 'O', 'Ω', 'Θ'.")
    complexity_class: str = Field(
        description="Clase de complejidad (ej: n, n^2, log n)."
    )
    formatted_notation: str = Field(description="Ej: 'O(n^2)', 'Ω(1)'.")
    justification: str = Field(
        description="Explicación basada en el término dominante."
    )


class ComplexityResponse(BaseModel):
    algorithm_name: str
    analysis: List[AsymptoticResult]
    final_conclusion: str


# ==========================================
# SERVICIO DETERMINISTA
# ==========================================


class ComplexityAnalysisService:
    """
    Servicio determinista que reemplaza al ComplexityAnalysisAgent.
    Utiliza SymPy para calcular matemáticamente el orden asintótico.
    """

    def __init__(self):
        # Definimos 'n' como símbolo positivo real para evitar problemas con límites complejos
        self.n = symbols("n", real=True, positive=True)

    def _clean_expression(self, expr_str: str) -> str:
        """
        Limpia la ecuación para que SymPy pueda entenderla.
        Ej: "T(n) = 3n^2 + c1" -> "3*n**2 + 1"
        """
        # 1. Eliminar comentarios //...
        clean = re.sub(r"//.*", "", expr_str)

        # 2. Eliminar prefijos tipo "T(n) =" o "t(n) ="
        clean = re.sub(r"^[tT](?:_[a-zA-Z0-9]+)?\(n\)\s*=\s*", "", clean)

        # 3. Reemplazar constantes arbitrarias (c1, c2, A, B) por 1
        # Esto es crucial: SymPy no sabe que 'c1' es constante a menos que se defina.
        # Preservamos 'n', 'log', y funciones matemáticas, reemplazamos el resto por '1'
        allowed = ["n", "log", "ln", "log2", "sqrt", "exp", "pow", "sin", "cos"]

        def replace_token(match):
            token = match.group(0)
            # Preservar números
            if token.isnumeric():
                return token
            # Preservar palabras permitidas (sin distinción de mayúsculas)
            if token.lower() in allowed:
                return token
            # Preservar 'n' específicamente (caso especial)
            if token == "n":
                return token
            # Todo lo demás es una constante
            return "1"

        # Regex para identificar tokens de palabras (pero no dentro de operadores)
        # Usa negative lookbehind/lookahead para evitar reemplazar en medio de números
        clean = re.sub(
            r"(?<![0-9])\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?![0-9])", replace_token, clean
        )

        # 4. Convertir sintaxis de potencia ^ a ** (Python)
        clean = clean.replace("^", "**")

        return clean.strip() or "1"

    def _get_dominant_term(self, expr_str: str) -> str:
        """
        Usa SymPy para extraer la clase de complejidad (O-grande).
        """
        try:
            cleaned_expr = self._clean_expression(expr_str)

            # Crear un contexto con 'n' como símbolo para sympify
            local_dict = {"n": self.n, "log": log}
            expr = sympify(cleaned_expr, locals=local_dict)

            # Calculamos Big-O en infinito: O(expr, (n, oo))
            # Esto simplifica automáticamente al término dominante.
            # Ej: O(3*n**2 + 5*n) -> O(n**2)
            big_o = O(expr, (self.n, oo))

            # Extraemos el argumento interno de O(...)
            if big_o.args:
                term = big_o.args[0]  # El núcleo de la expresión (ej: n**2)
            else:
                # Si es O(1), args puede estar vacío o comportarse distinto según versión
                term = 1

            # Formateo para lectura humana
            term_str = str(term)

            # Normalizar logaritmos: log(1/n) -> log(n)
            term_str = term_str.replace("log(1/n)", "log(n)")
            term_str = term_str.replace("log(n**(-1))", "log(n)")

            # Normalizar exponenciales: exp(n*log(2)) -> 2^n
            if "exp(n*log(" in term_str:
                # Extraer la base: exp(n*log(2)) -> 2
                import re

                match = re.search(r"exp\(n\*log\((\d+)\)\)", term_str)
                if match:
                    base = match.group(1)
                    term_str = f"{base}^n"

            term_str = term_str.replace("**", "^")
            term_str = term_str.replace("*", "")  # Quitar * explícitos

            return term_str

        except Exception as e:
            # Fallback manual de emergencia si SymPy falla
            print(f"⚠️ Error SymPy: {e} en '{expr_str}'. Usando fallback regex.")
            if "n^2" in expr_str or "n**2" in expr_str:
                return "n^2"
            if "log" in expr_str:
                return "log n"
            if "n" in expr_str:
                return "n"
            return "1"

    def _get_notation_symbol(self, case_name: str) -> str:
        """Asigna la notación según la regla de negocio del proyecto."""
        cn = case_name.lower()
        if "worst" in cn or "peor" in cn:
            return "O"
        elif "best" in cn or "mejor" in cn:
            return "Ω"  # Omega
        elif "average" in cn or "promedio" in cn or "medio" in cn:
            return "Θ"  # Theta
        return "Θ"  # Default

    def determine_complexity(
        self, algorithm_name: str, cases_data: List[dict]
    ) -> ComplexityResponse:
        """
        Método principal que imita la firma del Agente original.
        """
        results = []

        for case in cases_data:
            c_name = case.get("case_name", "General")
            func_str = case.get("efficiency_function", "1")

            # 1. Determinar símbolo
            symbol = self._get_notation_symbol(c_name)

            # 2. Calcular término dominante (Matemática Pura)
            dominant_term = self._get_dominant_term(func_str)

            # 3. Construir resultado
            formatted = f"{symbol}({dominant_term})"

            justification = (
                f"La función de eficiencia '{func_str}' tiene un comportamiento asintótico dominado por {dominant_term}. "
                f"Al tratarse del caso '{c_name}', se utiliza la notación {symbol}."
            )

            results.append(
                AsymptoticResult(
                    case_name=c_name,
                    notation_type=symbol,
                    complexity_class=dominant_term,
                    formatted_notation=formatted,
                    justification=justification,
                )
            )

        # Conclusión final
        # Buscamos el peor caso para la conclusión general, o usamos el primero
        worst_result = next(
            (r for r in results if r.notation_type == "O"),
            results[-1] if results else None,
        )

        if worst_result:
            conclusion = f"El algoritmo {algorithm_name} tiene una complejidad temporal de {worst_result.formatted_notation} en el peor caso."
        else:
            conclusion = f"El análisis asintótico indica un comportamiento de {results[0].formatted_notation}."

        return ComplexityResponse(
            algorithm_name=algorithm_name, analysis=results, final_conclusion=conclusion
        )
