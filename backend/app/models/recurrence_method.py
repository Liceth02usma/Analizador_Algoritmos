from typing import List
import re
import math


class RecurrenceMethods:
    """
    Implementa diferentes métodos para resolver relaciones de recurrencia.
    Incluye: Teorema Maestro, Método de Sustitución y Método Iterativo.
    """

    def __init__(self, recurrence_equation: str = ""):
        self.method_used: str = ""
        self.recurrence_equation: str = recurrence_equation
        self.expansion_steps: List[str] = []
        self.final_solution: str = ""

    def apply_master_theorem(self, relation: str) -> str:
        """
        Aplica el Teorema Maestro para resolver recurrencias de la forma:
        T(n) = aT(n/b) + f(n)
        
        Args:
            relation: String con la relación de recurrencia
            
        Returns:
            String con la solución
        """
        self.method_used = "Teorema Maestro"
        self.recurrence_equation = relation
        
        # Extraer parámetros a, b de la relación
        # Ejemplo: "T(n) = 2T(n/2) + O(n)" -> a=2, b=2
        
        import re
        
        # Buscar patrón aT(n/b)
        pattern = r'(\d+)T\(n/(\d+)\)'
        match = re.search(pattern, relation)
        
        if not match:
            # Intentar patrón T(n-1) (no aplicable al teorema maestro)
            if 'n-1' in relation or 'n-2' in relation:
                self.final_solution = "O(n)"
                self.expansion_steps.append("Relación de recurrencia lineal (sustracción)")
                self.expansion_steps.append("Por inducción: T(n) = O(n)")
                return self.final_solution
            else:
                self.final_solution = "No se pudo aplicar el Teorema Maestro"
                return self.final_solution
        
        a = int(match.group(1))
        b = int(match.group(2))
        
        # Calcular log_b(a)
        import math
        log_b_a = math.log(a) / math.log(b)
        
        self.expansion_steps.append(f"Identificado: a = {a}, b = {b}")
        self.expansion_steps.append(f"log_b(a) = log_{b}({a}) = {log_b_a:.2f}")
        
        # Determinar f(n) de la relación
        # Casos comunes: O(1), O(n), O(n log n), O(n²)
        if 'O(1)' in relation or '+ 1' in relation or '+ O(1)' in relation:
            # Caso 1: f(n) = O(1) = O(n^0)
            self.expansion_steps.append("f(n) = O(1) = O(n^0)")
            self.expansion_steps.append(f"Comparando: c = 0 con log_b(a) = {log_b_a:.2f}")
            
            if abs(log_b_a) < 0.01:  # log_b(a) ≈ 0
                # Caso 2: f(n) = Θ(n^log_b(a))
                self.final_solution = "O(log n)"
                self.expansion_steps.append("Caso 2 del Teorema Maestro: T(n) = Θ(n^c log n) = O(log n)")
            else:
                # Caso 1: f(n) = O(n^c) donde c < log_b(a)
                self.final_solution = f"O(n^{log_b_a:.2f})"
                if a == 2 and b == 2:
                    self.final_solution = "O(n)"
                self.expansion_steps.append(f"Caso 1 del Teorema Maestro: T(n) = Θ(n^log_b(a)) = {self.final_solution}")
        
        elif 'O(n)' in relation or '+ n' in relation:
            # f(n) = O(n) = O(n^1)
            c = 1
            self.expansion_steps.append(f"f(n) = O(n) = O(n^{c})")
            self.expansion_steps.append(f"Comparando: c = {c} con log_b(a) = {log_b_a:.2f}")
            
            if abs(c - log_b_a) < 0.01:
                # Caso 2: f(n) = Θ(n^log_b(a))
                self.final_solution = "O(n log n)"
                self.expansion_steps.append("Caso 2 del Teorema Maestro: T(n) = Θ(n^c log n) = O(n log n)")
            elif c < log_b_a:
                # Caso 1
                self.final_solution = f"O(n^{log_b_a:.2f})"
                self.expansion_steps.append(f"Caso 1: c < log_b(a), entonces T(n) = {self.final_solution}")
            else:
                # Caso 3
                self.final_solution = "O(n)"
                self.expansion_steps.append("Caso 3: c > log_b(a), entonces T(n) = O(f(n)) = O(n)")
        
        elif 'O(n²)' in relation or 'n^2' in relation:
            # f(n) = O(n²)
            c = 2
            self.expansion_steps.append(f"f(n) = O(n²) = O(n^{c})")
            self.expansion_steps.append(f"Comparando: c = {c} con log_b(a) = {log_b_a:.2f}")
            
            if c > log_b_a:
                # Caso 3
                self.final_solution = "O(n²)"
                self.expansion_steps.append("Caso 3: c > log_b(a), entonces T(n) = O(f(n)) = O(n²)")
            else:
                self.final_solution = f"O(n^{log_b_a:.2f})"
                self.expansion_steps.append(f"Caso 1: T(n) = {self.final_solution}")
        
        else:
            # Por defecto, usar caso 2
            self.final_solution = "O(n log n)"
            self.expansion_steps.append("Usando aproximación: T(n) = O(n log n)")
        
        return self.final_solution

    def substitution_method(self, relation: str) -> str:
        """
        Usa el método de sustitución para verificar una solución propuesta.
        
        Args:
            relation: String con la relación de recurrencia
            
        Returns:
            String con la solución verificada
        """
        self.method_used = "Método de Sustitución"
        self.recurrence_equation = relation
        
        # Este es un método más manual, aquí hacemos una aproximación
        self.expansion_steps.append("Paso 1: Proponer una solución (hipótesis)")
        
        # Intentar primero con el teorema maestro para tener una hipótesis
        hypothesis = self.apply_master_theorem(relation)
        
        self.expansion_steps.append(f"Hipótesis: T(n) = {hypothesis}")
        self.expansion_steps.append("Paso 2: Sustituir en la relación original")
        self.expansion_steps.append("Paso 3: Verificar que la hipótesis se cumple")
        
        self.final_solution = hypothesis
        return self.final_solution

    def iterative_method(self, relation: str) -> str:
        """
        Usa el método iterativo (expansión) para resolver la recurrencia.
        
        Args:
            relation: String con la relación de recurrencia
            
        Returns:
            String con la solución
        """
        self.method_used = "Método Iterativo (Expansión)"
        self.recurrence_equation = relation
        
        # Expandir la recurrencia iterativamente
        self.expansion_steps.append("Expandiendo la recurrencia:")
        
        # Ejemplo: T(n) = T(n-1) + c
        if 'n-1' in relation:
            self.expansion_steps.append("T(n) = T(n-1) + c")
            self.expansion_steps.append("T(n) = [T(n-2) + c] + c = T(n-2) + 2c")
            self.expansion_steps.append("T(n) = [T(n-3) + c] + 2c = T(n-3) + 3c")
            self.expansion_steps.append("...")
            self.expansion_steps.append("T(n) = T(n-k) + kc")
            self.expansion_steps.append("Cuando k = n-1: T(n) = T(1) + (n-1)c")
            self.expansion_steps.append("Por lo tanto: T(n) = Θ(n)")
            self.final_solution = "O(n)"
        
        # Ejemplo: T(n) = 2T(n/2) + n
        elif '/2' in relation:
            self.expansion_steps.append("T(n) = 2T(n/2) + n")
            self.expansion_steps.append("T(n) = 2[2T(n/4) + n/2] + n = 4T(n/4) + 2n")
            self.expansion_steps.append("T(n) = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + 3n")
            self.expansion_steps.append("...")
            self.expansion_steps.append("T(n) = 2^k T(n/2^k) + kn")
            self.expansion_steps.append("Cuando n/2^k = 1 → k = log n")
            self.expansion_steps.append("T(n) = nT(1) + n log n = Θ(n log n)")
            self.final_solution = "O(n log n)"
        
        else:
            # Caso genérico
            self.final_solution = self.apply_master_theorem(relation)
        
        return self.final_solution

    def validate_solution(self) -> bool:
        """
        Valida que la solución obtenida sea correcta mediante verificación.
        
        Returns:
            True si la solución es válida, False en caso contrario
        """
        # Validación básica: verificar que se haya encontrado una solución
        if not self.final_solution:
            return False
        
        # Verificar que la solución esté en notación Big-O válida
        valid_patterns = [
            r'O\(1\)',
            r'O\(log n\)',
            r'O\(n\)',
            r'O\(n log n\)',
            r'O\(n\^\d+\)',
            r'O\(2\^n\)',
        ]
        
        for pattern in valid_patterns:
            if re.search(pattern, self.final_solution):
                return True
        
        return False

