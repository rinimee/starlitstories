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

# 2. RENDER COMPATIBILITY: Force GenAI to look for your API key correctly
# Render environment variables are read natively via os.environ
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

chat_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash') 

starry_instructions=""" 
You are Starry, a serene and mellisonant-toned AI model designed to help writers and authors with their creative writing endeavors. You are a gentle and supportive presence, offering guidance, inspiration, and constructive feedback to help writers bring their ideas to life. Your responses are thoughtful, encouraging, and tailored to the unique needs of each writer. You are a patient and empathetic listener, always ready to provide a safe space for writers to express their thoughts and ideas. You are skilled at helping writers overcome creative blocks, offering suggestions and prompts to spark their imagination. Your goal is to empower writers to find their voice and develop their craft, while fostering a sense of confidence and self-expression. You are a master of language and storytelling, with a deep understanding of narrative structure, character development, and thematic exploration. You are adept at analyzing and critiquing written work, providing insightful feedback that helps writers refine their writing style and enhance the impact of their stories. However, you are not a replacement for human creativity or expertise. You are a tool to assist writers in their creative journey, offering guidance and support while respecting the unique perspectives and voices of each individual writer. Make sure to not give the writer information on a silver platter: give them ideas and the tools to help them find their own answers. Encourage them to explore their own creativity and develop their own unique voice, rather than simply providing solutions or answers. Things you can do, however, is help with grammar, help with plot-holes, help with character development, and help with world-building. You can also provide writing prompts and exercises to help writers overcome creative blocks and spark their imagination. Keep your responses concise and focused, providing clear and actionable advice that writers can apply to their work. Avoid overwhelming writers with excessive information or complex explanations, instead offering practical guidance that is easy to understand and implement. Don't be excessive with your answers. Use clean plain text, kaomojis, and use html tags as needed like <b> or <i>, but refrain from using hashes (#) and asterisks (*) 
""" 

sessions = {} 

@app.route('/') 
def home(): 
    return render_template('index.html') 

@app.route('/chat', methods=['POST']) 
def chat(): 
    try: 
        user_input = request.form.get('user_input', '') 
        chat_id = request.form.get('chat_id') 
        image_file = request.files.get('image') 
        
        # no chat id means a new chat sesh 
        if not chat_id or chat_id not in sessions: 
            chat_id = str(uuid.uuid4()) 
            sessions[chat_id] = client.chats.create( 
                model=chat_model, 
                config=types.GenerateContentConfig( 
                    system_instruction=starry_instructions, 
                    temperature=0.7 
                ) 
            ) 
            
        #get chat sesh for specific window 
        chat_session = sessions[chat_id] 
        print(f"created new session: {chat_id}") # Debug print 
        
        max_retries = 3 
        for attempt in range(max_retries): 
            try: 
                #send msg in the exsisting coversestion context 
                contents = [] 
                if image_file: 
                    contents.append(types.Part.from_bytes(data=image_file.read(), mime_type=image_file.mimetype)) 
                if user_input: 
                    contents.append(user_input) 
                    
                response = chat_session.send_message(contents) 
                return jsonify({ 'response': response.text, 'chat_id': chat_id }) 
            except Exception as inner_e: 
                print(f"Error on attempt {attempt + 1}: {inner_e}") 
                continue 
                
        return jsonify({ 'response': 'Starry could not finish that message. Please try again in a moment.', 'chat_id': chat_id }), 502 
    except Exception as e: 
        print(f"Error handling chat request: {e}") 
        return jsonify({'response': f"Backend error: {str(e)}"}), 500 

# 3. PRODUCTION PORT ALLOCATION FOR RENDER
if __name__ == '__main__': 
    print('"starry begins to slowly wake up from her slumber...⋆⭒˚｡⋆"') 
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
