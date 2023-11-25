from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel.orchestration.sk_context import SKContext

class Math:
    @sk_function(
        description="加法",
        name="add",
    )
    @sk_function_context_parameter(
        name="number1",
        description="被加数",
    )
    @sk_function_context_parameter(
        name="number2",
        description="加数",
    )
    def add(self, context: SKContext) -> str:
        return str(float(context["number1"]) + float(context["number2"]))
    
    @sk_function(
        description="减法",
        name="minus",
    )
    @sk_function_context_parameter(
        name="number1",
        description="被减数",
    )
    @sk_function_context_parameter(
        name="number2",
        description="减数",
    )
    def minus(self, context: SKContext) -> str:
        return str(float(context["number1"]) - float(context["number2"]))