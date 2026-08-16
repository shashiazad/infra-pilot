from app.llm.groq import create_groq_model


def main() -> None:
    model = create_groq_model()

    response = model.invoke("Explain what an HTTP 500 error means in one sentence.")

    print(response.content)


if __name__ == "__main__":
    main()
