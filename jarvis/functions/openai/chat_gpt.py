import openai

openai.api_key = "..."


def get_response(question):

    max_length = 500

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Antworte in maximal {max_length} Zeichen."},
            {"role": "user", "content": question},
        ],
    )

    response_text = response["choices"][0]["message"]["content"]

    print(response)
    print(response_text)

    return response_text
