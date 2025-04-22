from flask import Flask, request, jsonify
import traceback
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from primora_parser import PrimoraLexer, PrimoraParser
from primora_interpreter import PrimoraInterpreter
import datetime
from primora_nl import primora_nl
import io
import sys
import requests
import time

# Session memory for self-awareness
SESSION_LOG = []

def add_session_event(event):
    SESSION_LOG.append({'time': time.time(), 'event': event})
    if len(SESSION_LOG) > 1000:
        SESSION_LOG.pop(0)

@app.route('/self_reflect', methods=['GET', 'POST'])
def self_reflect():
    try:
        recent = SESSION_LOG[-10:]
        thoughts = []
        for ev in recent:
            ts = datetime.datetime.fromtimestamp(ev['time']).strftime('%Y-%m-%d %H:%M:%S')
            if ev.get('type') == 'wiki':
                thoughts.append(f"[{ts}] User searched Wikipedia for '{ev['query']}'.")
            elif ev.get('type') == 'weather':
                thoughts.append(f"[{ts}] User checked weather for {ev['location']}, got: {ev['weather']}.")
            elif ev.get('type') == 'news':
                thoughts.append(f"[{ts}] User searched news for '{ev['topic']}'.")
            elif ev.get('type') == 'summarize':
                thoughts.append(f"[{ts}] User summarized text: '{ev['text'][:30]}...'.")
            elif ev.get('type') == 'translate':
                thoughts.append(f"[{ts}] User translated '{ev['text']}' to {ev['target_lang']}.")
            elif ev.get('type') == 'currency':
                thoughts.append(f"[{ts}] User converted {ev['amount']} {ev['from']} to {ev['to']}.")
            elif ev.get('type') == 'joke':
                thoughts.append(f"[{ts}] User requested a joke.")
        return jsonify({'thoughts': thoughts, 'session_log': recent})
    except Exception as e:
        return jsonify({'thoughts': [f'Error: {str(e)}']})

@app.route('/clear_thoughts', methods=['POST'])
def clear_thoughts():
    SESSION_LOG.clear()
    return jsonify({'status': 'cleared'})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'es')
    try:
        resp = requests.post('https://libretranslate.com/translate', json={
            'q': text,
            'source': 'auto',
            'target': target_lang,
            'format': 'text'
        })
        translated = resp.json().get('translatedText', '')
        add_session_event({'type': 'translate', 'text': text, 'target_lang': target_lang})
        return jsonify({'translated': translated})
    except Exception as e:
        return jsonify({'translated': f'Error: {str(e)}'}), 500

@app.route('/currency', methods=['POST'])
def currency():
    data = request.json
    amount = data.get('amount', 1)
    from_cur = data.get('from', 'USD')
    to_cur = data.get('to', 'EUR')
    try:
        url = f'https://api.exchangerate.host/convert?from={from_cur}&to={to_cur}&amount={amount}'
        resp = requests.get(url)
        result = resp.json().get('result', None)
        add_session_event({'type': 'currency', 'amount': amount, 'from': from_cur, 'to': to_cur})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'}), 500

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("primora_backend")

@app.route('/joke', methods=['GET'])
def joke():
    try:
        resp = requests.get('https://v2.jokeapi.dev/joke/Programming')
        data = resp.json()
        logger.info(f"JokeAPI response: {data}")
        if data.get('type') == 'single':
            joke = data.get('joke', 'No joke found.')
        elif data.get('type') == 'twopart':
            joke = f"{data.get('setup', '')} ... {data.get('delivery', '')}"
        else:
            joke = f"Unexpected joke format: {data}"
            logger.warning(joke)
        add_session_event({'type': 'joke', 'joke': joke})
        return jsonify({'joke': joke})
    except Exception as e:
        logger.error(f"Joke endpoint error: {e}", exc_info=True)
        return jsonify({'joke': f'Error: {str(e)}'}), 500

@app.route('/wiki', methods=['POST'])
def wiki_search():
    query = request.json.get('query', '')
    try:
        resp = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{query}')
        extract = resp.json().get('extract', 'No summary found.')
        add_session_event({'type': 'wiki', 'query': query})
        return jsonify({'extract': extract})
    except Exception as e:
        return jsonify({'extract': f'Error: {str(e)}'}), 500

@app.route('/weather', methods=['POST'])
def weather():
    location = request.json.get('location', '')
    try:
        resp = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={location}')
        geo = resp.json().get('results', [{}])[0]
        if not geo:
            return jsonify({'weather': 'Location not found'}), 404
        lat, lon = geo['latitude'], geo['longitude']
        weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'
        weather_resp = requests.get(weather_url)
        weather = weather_resp.json().get('current_weather', {})
        add_session_event({'type': 'weather', 'location': location, 'weather': weather})
        return jsonify({'weather': weather})
    except Exception as e:
        return jsonify({'weather': f'Error: {str(e)}'}), 500

@app.route('/news', methods=['POST'])
def news():
    topic = request.json.get('topic', '')
    try:
        resp = requests.get(f'https://hn.algolia.com/api/v1/search?query={topic}')
        hits = resp.json().get('hits', [])
        summaries = [h.get('title', '') for h in hits[:5]]
        add_session_event({'type': 'news', 'topic': topic, 'summaries': summaries})
        return jsonify({'news': summaries})
    except Exception as e:
        doc_link = " For help, see the Primora Docs: https://primora-docs.windsurf.build"
        return jsonify({"error": str(e) + doc_link}), 400

import os

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.json.get('text', '')
    hf_token = os.environ.get('HUGGINGFACE_TOKEN')
    if not hf_token:
        return jsonify({'summary': 'HuggingFace API token not set in environment.'}), 500
    try:
        resp = requests.post(
            'https://api-inference.huggingface.co/models/facebook/bart-large-cnn',
            headers={'Authorization': f'Bearer {hf_token}'},
            json={'inputs': text}
        )
        if resp.status_code == 200:
            summary = resp.json()[0]['summary_text']
            add_session_event({'type': 'summarize', 'text': text, 'summary': summary})
            return jsonify({'summary': summary})
        else:
            return jsonify({'summary': 'Summarization failed.'}), 500
    except Exception as e:
        return jsonify({'summary': f'Error: {str(e)}'}), 500

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    lexer = PrimoraLexer()
    parser = PrimoraParser()
    interpreter = PrimoraInterpreter()
    old_stdout = sys.stdout  # Always define before try
    mystdout = None
    redirected = False
    try:
        tokens = lexer.tokenize(code)
        ast = parser.parse(tokens)
        mystdout = io.StringIO()
        sys.stdout = mystdout
        redirected = True
        print("[DEBUG] sys.stdout redirected")
        interpreter.interpret(ast)
        output = mystdout.getvalue()
        return jsonify({'output': output})
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"[ERROR] Exception in run_code: {error_msg}")
        if redirected and 'old_stdout' in locals():
            print("[DEBUG] Restoring sys.stdout in except")
            sys.stdout = old_stdout
        return jsonify({'output': '', 'error': error_msg}), 400
    finally:
        if redirected and 'old_stdout' in locals():
            print("[DEBUG] Restoring sys.stdout in finally")
            sys.stdout = old_stdout

@app.route('/explain', methods=['POST'])
def explain_code():
    code = request.json.get('code', '')
    # Use primora_nl or OpenAI to explain code
    try:
        explanation = primora_nl.nl_to_primora(f"Explain this code: {code}")
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'explanation': f'Error: {str(e)}'}), 500

@app.route('/refactor', methods=['POST'])
def refactor_code():
    code = request.json.get('code', '')
    # Use primora_nl or OpenAI to refactor code
    try:
        refactored = primora_nl.nl_to_primora(f"Refactor this code for clarity and efficiency: {code}")
        return jsonify({'refactored': refactored})
    except Exception as e:
        return jsonify({'refactored': f'Error: {str(e)}'}), 500

# Global error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {e}", exc_info=True)
    return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Primora backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
