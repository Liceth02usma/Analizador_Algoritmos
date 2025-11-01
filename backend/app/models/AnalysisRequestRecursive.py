from pydantic import BaseModel, Field

class AnalysisRequestRecursive(BaseModel):
    algorithm_name: str = Field(..., example="fibonacci")
    pseudocode: str = Field(
        ...,
        example="fibonacci(n)\nbegin\n    if (n <= 1) then\n    begin\n        return n\n    end\n    else\n    begin\n        fib1 🡨 CALL fibonacci(n-1)\n        fib2 🡨 CALL fibonacci(n-2)\n        return fib1 + fib2\n    end\nend"
    )