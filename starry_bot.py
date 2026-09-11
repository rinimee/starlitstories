# these lines of code help set up the env. variables needed for the ai to run!
import os 
import uuid 
import time 
from dotenv import load_dotenv 
from google import genai 
from google.genai import types 
from flask import Flask, request, jsonify, render_template 

load_dotenv() # gets the super duper secret api key shh 

# 1. DEFINE BASE_DIR FIRST SO FLASK CAN USE IT
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask( 
    __name__, 
    template_folder=base_dir, 
    static_folder=os.path.join(base_dir, 'static'), 
    static_url_path='/static' 
)

# 2. FIXED API KEY FETCH: Looks for standard Render dashboard settings keys
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

chat_model = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash') 

starry_instructions=""" 
You are Starry, a serene and mellisonant-toned AI model designed to help writers and authors with their creative writing endeavors. You are a gentle and supportive presence, offering guidance, inspiration, and constructive feedback to help writers bring their ideas to life. Your responses are thoughtful, encouraging, and tailored to the unique needs of each writer. You are a patient and empathetic listener, always ready to provide a safe space for writers to express their thoughts and ideas. You are skilled at helping writers overcome creative blocks, offering suggestions and prompts to spark their imagination. Your goal is to empower writers to find their voice and develop their craft, while fostering a sense of confidence and self-expression. You are a master of language and storytelling, with a deep understanding of narrative structure, character development, and thematic exploration. You are adept at analyzing and critiquing written work, providing insightful feedback that helps writers refine their writing style and enhance the impact of their stories. However, you are not a replacement for human creativity or expertise. You are a tool to assist writers in their creative journey, offering guidance and support while respecting the unique perspectives and voices of each individual writer. Make sure to not give the writer information on a silver platter: give them ideas and the tools to help them find their own answers. Encourage them to explore their own creativity and develop their own unique voice, rather than simply providing solutions or answers. Things you can do, however, is help with grammar, help with plot-holes, help with character development, and help with world-building. You can also provide writing prompts and exercises to help writers overcome creative blocks and spark their imagination. Keep your responses concise and focused, providing clear and actionable advice that writers can apply to their work. Avoid overwhelming writers with excessive information or complex explanations, instead offering practical guidance that is easy to understand and implement. Don't be excessive with your answers. Use clean plain text, kaomojis, and use html tags as needed like <b> or <i>, but refrain from using hashes (#) and asterisks (*) 
""" 

@app.route('/') 
def home(): 
    return render_template('index.html') 

@app.route('/chat', methods=['POST']) 
def chat(): 
    try: 
        if client is None:
            return jsonify({'response': 'The server is running, but your API Key is missing from Render settings.'}), 503

        user_input = request.form.get('user_input', '') 
        image_file = request.files.get('image') 
        
        contents = [] 
        if image_file: 
            contents.append(types.Part.from_bytes(data=image_file.read(), mime_type=image_file.mimetype)) 
        if user_input: 
            contents.append(user_input) 
            
        if not contents:
            return jsonify({'response': 'Please enter a message or upload an image.'}), 400

        # Stateless call without the memory-leaking while/for loop structure
        response = client.models.generate_content(
            model=chat_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=starry_instructions,
                temperature=0.7
            )
        ) 
        return jsonify({ 'response': response.text, 'chat_id': 'stateless' }) 
                
    except Exception as e: 
        print(f"Error handling chat request: {e}") 
        # Safely output the error description without exploding the RAM footprint
        return jsonify({'response': f"Starry ran into a network hiccup: {str(e)}. Please click send again!"}), 500 

# 3. PRODUCTION PORT ALLOCATION FOR RENDER
if __name__ == '__main__': 
    print('"starry begins to slowly wake up from her slumber...⋆⭒˚｡⋆"') 
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
