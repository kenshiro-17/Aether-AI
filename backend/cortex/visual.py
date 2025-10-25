import base64
import os
import time
from openai import OpenAI

class VisualCortex:
    def __init__(self):
        # Vision Cortex runs on Port 8083 (8081=Text, 8082=Expo)
        self.client = OpenAI(base_url="http://localhost:8083/v1", api_key="vision")
        self.is_active = False

    def health_check(self):
        """Check if Vision Cortex is online."""
        try:
            self.client.models.list()
            self.is_active = True
            return True
        except:
            self.is_active = False
            return False

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail focusing on visual elements.") -> str:
        """
        Send an image to the Vision Cortex for analysis.
        Returns the text description.
        """
        if not self.is_active:
            if not self.health_check():
                return "[Error] Vision Cortex (Port 8083) is offline. Please check start_system.bat"

        try:
            # Detect mime type roughly
            mime_type = "image/jpeg"
            if image_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_path.lower().endswith(".webp"):
                mime_type = "image/webp"

            # 1. Encode Image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # 2. Call Vision Model
            # LLaVA-Phi-3 uses standard LLaVA architecture
            response = self.client.chat.completions.create(
                model="llava-phi-3-mini-int4.gguf", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ],
                max_tokens=512,
                temperature=0.1 # Keep it factual
            )
            
            description = response.choices[0].message.content
            return f"[VISION CORTEX ANALYZED IMAGE]: {description}"

        except Exception as e:
            print(f"[VISION ERROR] {e}")
            return f"[Error] Vision analysis failed: {str(e)}"

# Global Instance
visual_cortex = VisualCortex()
