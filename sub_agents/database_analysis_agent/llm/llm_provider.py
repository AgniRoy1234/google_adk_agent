from dotenv import load_dotenv 
load_dotenv()

import os 
model_name = os.getenv("MODEL") 

from google import genai 
client = genai.Client(api_key= os.getenv("GOOGLE_API_KEY")) 
