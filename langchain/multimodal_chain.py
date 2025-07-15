from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.schema import HumanMessage
from PIL import Image
import base64
from io import BytesIO
import time

def encode_image(image_path: str) -> str:
    """Encode image to base64 string"""
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def create_multimodal_chain(image_model, text_model):
    """Create a three-step multimodal chain"""
    # Step 1: Image description
    def create_image_message(data: dict) -> list:
        return [HumanMessage(content=[
            {"type": "text", "text": "描述这张图片的内容"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{data['image_base64']}"
            }}
        ])]
    
    # Step 2: Story outline generation
    outline_prompt = ChatPromptTemplate.from_template(
        "基于以下图片描述生成一个故事大纲: {image_description}"
    )
    
    # Step 3: Full story generation
    story_prompt = ChatPromptTemplate.from_template(
        "根据以下故事大纲创作完整的故事内容: {story_outline}"
    )
    
    chain = (
        RunnablePassthrough.assign(
            image_base64=lambda x: encode_image(x["image_path"])
        )
        | {
            "image_description": RunnableLambda(create_image_message) | image_model | (lambda r: r.content),
        }
        | {
            "story_outline": outline_prompt | text_model | (lambda r: r.content),
            "image_description": lambda x: x["image_description"]
        }
        | {
            "full_story": story_prompt | text_model | (lambda r: r.content),
            "story_outline": lambda x: x["story_outline"],
            "image_description": lambda x: x["image_description"]
        }
    )
    return chain

def run_chain(chain, image_path, output_prefix="story"):
    """Execute chain and save results with timestamp"""
    result = chain.invoke({"image_path": image_path})
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    outline_filename = f"output/{output_prefix}_outline_{timestamp}.txt"
    story_filename = f"output/{output_prefix}_full_{timestamp}.txt"
    
    with open(outline_filename, "w", encoding="utf-8") as f:
        f.write(result["story_outline"])
    
    with open(story_filename, "w", encoding="utf-8") as f:
        f.write(result["full_story"])
    
    return {
        "outline_file": outline_filename,
        "story_file": story_filename,
        "image_description": result["image_description"],
        "story_outline": result["story_outline"],
        "full_story": result["full_story"]
    }
