from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os

r1 = ChatOpenAI(
    openai_api_base=os.getenv("R1_URL"),
    openai_api_key=os.getenv("R1_KEY"),
    model_name=os.getenv("R1_NAME"),
    temperature=0.7
)

q_omin = ChatOpenAI(
    openai_api_base=os.getenv("7B_URL"),
    model_name=os.getenv("7B_NAME"),
    openai_api_key="x",
    temperature=0.1
)

from multimodal_chain import create_multimodal_chain, run_chain
def main():
    chain = create_multimodal_chain(
        image_model=q_omin,
        text_model=r1
    )
    result = run_chain(chain, "static/test.jpeg")

    print("Image description:", result["image_description"])
    print("\nStory outline:")
    print(result["story_outline"])
    print("\nGenerated Full Story:")
    print(result["full_story"])
    print(f"\nOutput files: {result['outline_file']}, {result['story_file']}")

if __name__ == "__main__":
    main()
