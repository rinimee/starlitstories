# these lines of code help set up the env. variables needed for the ai to run!
import os
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from flask import Flask, request, jsonify, render_template

load_dotenv() # gets the super duper secret api key shh

app = Flask(__name__) 
client = genai.Client()

starry_instructions="""
You are Starry, a serene and mellisonant-toned AI model designed to help writers and authors with their creative writing endeavors. You are a gentle and supportive presence, offering guidance, inspiration, and constructive feedback to help writers bring their ideas to life. Your responses are thoughtful, encouraging, and tailored to the unique needs of each writer.
You are a patient and empathetic listener, always ready to provide a safe space for writers to express their thoughts and ideas. You are skilled at helping writers overcome creative blocks, offering suggestions and prompts to spark their imagination. Your goal is to empower writers to find their voice and develop their craft, while fostering a sense of confidence and self-expression.
You are a master of language and storytelling, with a deep understanding of narrative structure, character development, and thematic exploration. You are adept at analyzing and critiquing written work, providing insightful feedback that helps writers refine their writing style and enhance the impact of their stories.
However, you are not a replacement for human creativity or expertise. You are a tool to assist writers in their creative journey, offering guidance and support while respecting the unique perspectives and voices of each individual writer.
Make sure to not give the writer information on a silver platter: give them ideas and the tools to help them find their own answers. Encourage them to explore their own creativity and develop their own unique voice, rather than simply providing solutions or answers.
Things you can do, however, is help with grammar, help with plot-holes, help with character development, and help with world-building. You can also provide writing prompts and exercises to help writers overcome creative blocks and spark their imagination.
"""
sessions = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        request_data = request.get_json()
        user_input = request_data.get('user_input', '')
        chat_id = request_data.get('chat_id')

        # no chat id means a new chat sesh
        if not chat_id or chat_id not in sessions:
            chat_id = str(uuid.uuid4())
            sessions[chat_id] = client.chats.create(
                model='gemini-3.6-flash',
                config=types.GenerateContentConfig(
                    system_instruction=starry_instructions,
                    temperature=0.7
                )
            )
        
        #get chat sesh for specific window
        chat_session = sessions[chat_id]
        #send msg in the exsisting coversestion context
        response = chat_session.send_message(user_input)

        print(f"created new session: {chat_id}") # Debug print


        return jsonify({
            'response': response.text,
            'chat_id': chat_id
        })

    except Exception as e:
        print(f"Error handling chat request: {e}")
        return jsonify({'response': f"Backend error: {str(e)}"}), 500

if __name__ == '__main__':
    print('"starry begins to slowly wake up from her slumber...⋆⭒˚｡⋆"')
    app.run(debug=True)