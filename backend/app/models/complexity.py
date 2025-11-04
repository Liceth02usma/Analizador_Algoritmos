from typing import Optional


class Complexity:
    """
    Representa la complejidad computacional de un algoritmo.
    Incluye análisis de mejor caso (Ω), peor caso (O), caso promedio (Θ),
    complejidad temporal y espacial.
    """

    def __init__(self):
        """Inicializa el objeto de complejidad."""
        # Complejidades básicas
        self.time_complexity: str = ""
        self.space_complexity: str = ""
        self.worst_case: str = ""
        self.best_case: str = ""
        self.average_case: str = ""
        
        # Notaciones asintóticas
        self.big_o: str = ""        # Cota superior
        self.big_omega: str = ""    # Cota inferior
        self.big_theta: str = ""    # Cota ajustada
        
        # Razonamiento y documentación
        self.reasoning: str = ""  # Explicación detallada del análisis

    def compute_from_recurrence(self, rec) -> None:
        """
        Calcula la complejidad a partir de una relación de recurrencia.
        
        Args:
            rec: Objeto RecurrenceMethods con la solución de la recurrencia
        """
        self.time_complexity = rec.final_solution
        self.worst_case = rec.final_solution
        
        # Agregar razonamiento
        self.reasoning += f"\n--- Análisis desde Recurrencia ---\n"
        self.reasoning += f"Método usado: {rec.method_used}\n"
        self.reasoning += f"Ecuación: {rec.recurrence_equation}\n"
        self.reasoning += f"Solución: {rec.final_solution}\n"
        
        if rec.expansion_steps:
            self.reasoning += "Pasos de expansión:\n"
            for i, step in enumerate(rec.expansion_steps, 1):
                self.reasoning += f"  {i}. {step}\n"

    def compute_from_loops(self, iterative) -> None:
        """
        Calcula la complejidad a partir del análisis de ciclos iterativos.
        
        Args:
            iterative: Objeto Iterative con información de los ciclos
        """
        # Análisis basado en ciclos anidados
        if iterative.nested_loops == 0:
            self.time_complexity = "O(1)"
            self.worst_case = "O(1)"
            self.best_case = "Ω(1)"
            self.average_case = "Θ(1)"
        elif iterative.nested_loops == 1:
            self.time_complexity = "O(n)"
            self.worst_case = "O(n)"
            self.best_case = "Ω(n)"
            self.average_case = "Θ(n)"
        elif iterative.nested_loops == 2:
            self.time_complexity = "O(n²)"
            self.worst_case = "O(n²)"
            self.best_case = "Ω(n²)"
            self.average_case = "Θ(n²)"
        elif iterative.nested_loops == 3:
            self.time_complexity = "O(n³)"
            self.worst_case = "O(n³)"
            self.best_case = "Ω(n³)"
            self.average_case = "Θ(n³)"
        else:
            self.time_complexity = f"O(n^{iterative.nested_loops})"
            self.worst_case = f"O(n^{iterative.nested_loops})"
            self.best_case = f"Ω(n^{iterative.nested_loops})"
            self.average_case = f"Θ(n^{iterative.nested_loops})"
        
        # Razonamiento
        self.reasoning += f"\n--- Análisis desde Ciclos ---\n"
        self.reasoning += f"Número de ciclos anidados: {iterative.nested_loops}\n"
        self.reasoning += f"Tipos de ciclos: {', '.join(iterative.loop_types)}\n"
        self.reasoning += f"Operaciones por ciclo: {iterative.operations_per_loop}\n"
        
        # Complejidad espacial (aproximación)
        self.space_complexity = "O(1)"  # Asumiendo que no hay uso extra de memoria
        self.reasoning += f"Complejidad espacial: {self.space_complexity}\n"

    def summarize_results(self) -> str:
        """
        Genera un resumen textual de los resultados de complejidad.
        
        Returns:
            String con el resumen formateado
        """
        summary = []
        summary.append("Análisis de Complejidad:")
        summary.append(f"  Mejor caso (Ω): {self.best_case}")
        summary.append(f"  Peor caso (O): {self.worst_case}")
        summary.append(f"  Caso promedio (Θ): {self.average_case}")
        summary.append(f"  Complejidad temporal: {self.time_complexity}")
        summary.append(f"  Complejidad espacial: {self.space_complexity}")
        
        if self.reasoning:
            summary.append("\nRazonamiento:")
            summary.append(self.reasoning)
        
        return "\n".join(summary)

    def export_report(self, format: str = "text") -> str:
        """
        Exporta el reporte de complejidad en diferentes formatos.
        
        Args:
            format: Formato de salida ('text', 'json', 'markdown')
            
        Returns:
            String con el reporte formateado
        """
        if format == "json":
            import json
            return json.dumps({
                "best_case": self.best_case,
                "worst_case": self.worst_case,
                "average_case": self.average_case,
                "time_complexity": self.time_complexity,
                "space_complexity": self.space_complexity,
                "reasoning": self.reasoning
            }, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            md = []
            md.append("# Análisis de Complejidad\n")
            md.append("## Notaciones Asintóticas\n")
            md.append(f"- **Mejor caso (Ω)**: `{self.best_case}`")
            md.append(f"- **Peor caso (O)**: `{self.worst_case}`")
            md.append(f"- **Caso promedio (Θ)**: `{self.average_case}`")
            md.append(f"\n## Complejidades\n")
            md.append(f"- **Temporal**: `{self.time_complexity}`")
            md.append(f"- **Espacial**: `{self.space_complexity}`")
            md.append(f"\n## Razonamiento\n")
            md.append(f"```\n{self.reasoning}\n```")
            return "\n".join(md)
        
        else:  # text
            return self.summarize_results()

