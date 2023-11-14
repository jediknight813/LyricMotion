import openai
from dotenv import load_dotenv
import os
load_dotenv()

LOCAL_TEXT_GENERATION_URL = os.getenv("LOCAL_TEXT_GENERATION_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")


def text_generation(lyric, useLocalGeneration, theme):

    text_generation_retrys = 4

    if useLocalGeneration == True:
        prompt = generate_with_llama(lyric, theme)
        print(len(prompt.split(" ")))

        if len(prompt.split(" ")) <= 7:
            print("Retrying lyric generation.")
            while text_generation_retrys >= 1:
                prompt = generate_with_llama(lyric, theme)
                if len(prompt.split(" ")) > 7:
                    break
        return prompt.strip()
    else:
        return generate_with_gpt(lyric, theme)


def generate_with_llama(lyric, theme):
    os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    os.environ["OPENAI_API_BASE"] = "http://"+LOCAL_TEXT_GENERATION_URL+"/v1"
    os.environ["OPENAI_API_HOST"] = "http://"+LOCAL_TEXT_GENERATION_URL
    import guidance
    guidance.llm = guidance.llms.OpenAI("text-davinci-003", caching=False)

    context_detection = guidance('''SYSTEM:
Given a Lyric respond with an image description that encapsulates the lryic.
Please Don't be vague with any details, please don't use any symbolism, be very blunt, do not explain yourself.
Please do not include the lyrics in your response.
Please focus on bringing the lyric to life, the theme doesn't matter as much as the lyric it should be like: Character, Scene, Action, Theme.
USER:
Theme: {{theme}}
Lyric: "{{lyric_input}}"
ASSISTANT: 
Image Description: {{~gen 'context' temperature=0.8 max_tokens=100 stop='\n'}}                   
''')

    response = context_detection(
        lyric_input=lyric,
        theme=theme
    )

    return response.variables()["context"]


def generate_with_gpt(lyric, theme):
    openai.organization = OPENAI_ORGANIZATION
    openai.api_key = OPENAI_API_KEY

    lyric_input_string = f"Lyric: {lyric}\nTheme: {theme}"
    from openai import OpenAI

    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": """
Given a Lyric respond with an image description that encapsulates the lryic.
Do not write explainations, only respond with the lyric description, do not write image description in your response.
"""},
                {"role": "user", "content": lyric_input_string},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result
