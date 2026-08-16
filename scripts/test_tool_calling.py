from app.tools.registry import INFRASTRUCTURE_TOOLS

from app.llm.groq import create_groq_model


def main() -> None:

    model = create_groq_model()

    model_with_tools = model.bind_tools(INFRASTRUCTURE_TOOLS)

    response = model_with_tools.invoke(
        """
        The payment-service is returning a large number
        of HTTP 5xx errors.

        Determine which infrastructure information
        you should inspect first.

        Service: payment-service
        """
    )

    print("\nContent:")
    print(response.content)

    print("\nTool Calls:")
    print(response.tool_calls)


if __name__ == "__main__":
    main()
