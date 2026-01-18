from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import requests
import PyPDF2
import io
import os
from dotenv import load_dotenv

load_dotenv()
import json

app = Flask(__name__)
CORS(app)

# API KEY WITH ENV
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not set!")
if not ELEVENLABS_API_KEY:
    print("⚠️  WARNING: ELEVENLABS_API_KEY not set!")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """Analyze resume/CV with detailed feedback (non-streaming)"""
    try:
        print("[RESUME] Analyzing resume...")
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        language = request.form.get('language', 'en')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        resume_text = ''
        if file.filename.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text() + '\n'
            except Exception as e:
                print(f"[ERROR] PDF extraction error: {str(e)}")
                return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 400
        elif file.filename.endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Please upload a PDF or TXT file'}), 400
        
        if not resume_text.strip():
            return jsonify({'error': 'No text found in the document'}), 400
        
        print(f"[RESUME] Extracted {len(resume_text)} characters")
        
        if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
            print("[ERROR] Gemini API key not configured!")
            return jsonify({'error': 'API key not configured in server.py'}), 500
        
        if language == 'fr':
            system_prompt = """Vous êtes un conseiller en carrière expert et consultant en CV avec plus de 20 ans d'expérience en recrutement dans plusieurs secteurs. Vous vous spécialisez dans l'aide aux candidats pour optimiser leurs CV pour les systèmes ATS et les recruteurs humains.

Votre analyse doit être complète, actionnable et structurée. Concentrez-vous sur :
1. Qualité et pertinence du contenu
2. Structure et formatage
3. Optimisation ATS
4. Impact et réalisations
5. Langue et ton
6. Meilleures pratiques spécifiques au secteur"""

            user_prompt = f"""Veuillez fournir une analyse approfondie de ce CV. Structurez vos commentaires comme suit :

**Impression générale** (2-3 phrases)
Fournissez une évaluation générale de l'efficacité du CV.

**Points forts** (2-3 points spécifiques). Gardez les points concis (1-2 phrases).
Identifiez ce qui fonctionne bien. Soyez spécifique avec des exemples du CV.

**Axes d'amélioration** (2-3 points)
Fournissez des commentaires actionnables sur ce qui nécessite du travail. Gardez les points concis (1-2 phrases).

**Optimisation ATS** (1-2 phrases).
- Analyse des mots-clés : Quels mots-clés manquent pour leur poste cible ?
- Problèmes de formatage qui pourraient confondre les systèmes ATS
- Améliorations spécifiques pour la compatibilité ATS

**Amélioration du contenu** (1-2 phrases).
- Quels points manquent d'impact ou de quantification ?
- Où les réalisations peuvent-elles remplacer les responsabilités ?
- Suggestions spécifiques pour renforcer les sections faibles

**Conseils spécifiques au secteur** (2-3 phrases).
Sur la base du contenu du CV, fournissez des conseils adaptés à leur secteur/poste spécifique.

**Plan d'action** (Liste priorisée)
Énumérez 5-7 changements par ordre de priorité qui auront le plus grand impact. Gardez les points concis (1-2 phrases).

Voici le CV à analyser :

{resume_text}

Rappelez-vous : Soyez direct, spécifique et actionnable. Utilisez des exemples de leur CV réel. Ne dites pas simplement "améliorez vos points" - montrez-leur exactement comment."""
        else:
            system_prompt = """You are an expert career advisor and resume consultant with 20+ years of experience in recruitment across multiple industries. You specialize in helping candidates optimize their resumes for ATS systems and human recruiters.

Your analysis should be comprehensive, actionable, and structured. Focus on:
1. Content quality and relevance
2. Structure and formatting
3. ATS optimization
4. Impact and achievements
5. Language and tone
6. Industry-specific best practices"""

            user_prompt = f"""Please provide an in-depth analysis of this resume/CV. Structure your feedback as follows:

**Overall Impression** (2-3 sentences)
Provide a high-level assessment of the resume's effectiveness.

**Strengths** (2-3 specific points). Keep points concise (1-2 sentences).
Identify what works well. Be specific with examples from the resume.

**Areas for Improvement** (2-3 points)
Provide actionable feedback on what needs work. Keep points concise (1-2 sentences).

**ATS Optimization** (1-2 sentences).
- Keyword analysis: What keywords are missing for their target role?
- Formatting issues that might confuse ATS systems
- Specific improvements for ATS compatibility

**Content Enhancement** (1-2 sentences).
- Which bullet points lack impact or quantification?
- Where can achievements replace responsibilities?
- Specific suggestions to strengthen weak sections

**Industry-Specific Advice** (2-3 sentences).
Based on the resume content, provide tailored advice for their specific industry/role.

**Action Plan** (Prioritized list)
List 5-7 changes in order of priority that will have the biggest impact. Keep points concise (1-2 sentences).

Here is the resume/CV to analyze:

{resume_text}

Remember: Be direct, specific, and actionable. Use examples from their actual resume. Don't just say "improve your bullet points" - show them exactly how."""

        # Combine system and user prompts
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        print(f"[RESUME] Calling Gemini API...")
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'contents': [{
                    'parts': [{
                        'text': combined_prompt
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 4000,
                }
            },
            timeout=60
        )
        
        print(f"[RESUME] Response status: {response.status_code}")
        
        if not response.ok:
            print(f"[ERROR] Gemini error: {response.text}")
            return jsonify({'error': response.text}), response.status_code
        
        # Convert Gemini response format to standard format
        gemini_response = response.json()
        
        # Extract text from Gemini response
        text_content = gemini_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # Format response in standard structure
        formatted_response = {
            'id': gemini_response.get('candidates', [{}])[0].get('content', {}).get('role', 'model'),
            'type': 'message',
            'role': 'assistant',
            'content': [{
                'type': 'text',
                'text': text_content
            }],
            'model': 'gemini-2.0-flash-exp',
            'stop_reason': gemini_response.get('candidates', [{}])[0].get('finishReason', 'end_turn'),
            'usage': {
                'input_tokens': gemini_response.get('usageMetadata', {}).get('promptTokenCount', 0),
                'output_tokens': gemini_response.get('usageMetadata', {}).get('candidatesTokenCount', 0)
            }
        }
        
        return jsonify(formatted_response), response.status_code
        
    except Exception as e:
        print(f"[ERROR] Resume analysis exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-resume/stream', methods=['POST'])
def analyze_resume_stream():
    """Analyze resume/CV with streaming feedback"""
    try:
        print("[RESUME-STREAM] Starting streaming resume analysis...")
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        language = request.form.get('language', 'en')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        resume_text = ''
        if file.filename.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text() + '\n'
            except Exception as e:
                print(f"[ERROR] PDF extraction error: {str(e)}")
                return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 400
        elif file.filename.endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Please upload a PDF or TXT file'}), 400
        
        if not resume_text.strip():
            return jsonify({'error': 'No text found in the document'}), 400
        
        print(f"[RESUME-STREAM] Extracted {len(resume_text)} characters")
        
        if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
            print("[ERROR] Gemini API key not configured!")
            return jsonify({'error': 'API key not configured in server.py'}), 500
        
        if language == 'fr':
            system_prompt = """Vous êtes un conseiller en carrière expert et consultant en CV avec plus de 20 ans d'expérience en recrutement dans plusieurs secteurs. Vous vous spécialisez dans l'aide aux candidats pour optimiser leurs CV pour les systèmes ATS et les recruteurs humains.

Votre analyse doit être complète, actionnable et structurée. Concentrez-vous sur :
1. Qualité et pertinence du contenu. Gardez les points concis (1-2 phrases).
2. Structure et formatage. Gardez les points concis (1-2 phrases).
3. Optimisation ATS. Gardez les points concis (1-2 phrases).
4. Impact et réalisations. Gardez les points concis (3-4 phrases).
5. Langue et ton. Gardez les points concis (1-2 phrases).
6. Meilleures pratiques spécifiques au secteur. Gardez les points concis (3-4 phrases).

Commencez votre réponse par : Note : [LETTRE] ([SCORE]/100)"""

            user_prompt = f"""Veuillez fournir une analyse approfondie de ce CV. Structurez vos commentaires comme suit :

Note : [A+, A, A-, B+, B, B-, C+, C, C-, D, ou F] ([Score sur 100])

**Impression générale** (2-3 phrases)
Fournissez une évaluation générale de l'efficacité du CV.

**Points forts** (2-3 points spécifiques). Gardez les points concis (1-2 phrases).
Identifiez ce qui fonctionne bien. Soyez spécifique avec des exemples du CV.

**Axes d'amélioration** (2-3 points détaillés). Gardez les points concis (1-2 phrases).
Fournissez des commentaires actionnables sur ce qui nécessite du travail. Pour chaque point :
- Expliquez POURQUOI c'est un problème
- Fournissez un exemple AVANT/APRÈS spécifique ou une suggestion
- Expliquez l'IMPACT de ce changement

**Optimisation ATS**.(2-3 phrases).
- Analyse des mots-clés : Quels mots-clés manquent pour leur poste cible ?
- Problèmes de formatage qui pourraient confondre les systèmes ATS
- Améliorations spécifiques pour la compatibilité ATS

**Amélioration du contenu**.(2-3 phrases).
- Quels points manquent d'impact ou de quantification ?
- Où les réalisations peuvent-elles remplacer les responsabilités ?
- Suggestions spécifiques pour renforcer les sections faibles

**Conseils spécifiques au secteur**. (2-3 phrases).
Sur la base du contenu du CV, fournissez des conseils adaptés à leur secteur/poste spécifique.

**Plan d'action** (Liste priorisée) (1-2 phrases par changement).
Énumérez 4-7 changements par ordre de priorité qui auront le plus grand impact.

Voici le CV à analyser :

{resume_text}

Rappelez-vous : Soyez direct, spécifique et actionnable. Utilisez des exemples de leur CV réel. Ne dites pas simplement "améliorez vos points" - montrez-leur exactement comment."""
        else:
            system_prompt = """You are an expert career advisor and resume consultant with 20+ years of experience in recruitment across multiple industries. You specialize in helping candidates optimize their resumes for ATS systems and human recruiters.

Your analysis should be comprehensive, actionable, and structured. Focus on:
1. Content quality and relevance. Keep points concise (1-2 sentences).
2. Structure and formatting. Keep points concise (1-2 sentences).
3. ATS optimization. Keep points concise (1-2 sentences).
4. Impact and achievements. Keep points concise (3-4 sentences).
5. Language and tone. Keep points concise (1-2 sentences).
6. Industry-specific best practices. Keep points concise (3-4 sentences).

Start your response with: Grade: [LETTER] ([SCORE]/100)"""

            user_prompt = f"""Please provide an in-depth analysis of this resume/CV. Structure your feedback as follows:

Grade: [A+, A, A-, B+, B, B-, C+, C, C-, D, or F] ([Score out of 100])

**Overall Impression** (2-3 sentences)
Provide a high-level assessment of the resume's effectiveness.

**Strengths** (2-3 specific points) . Keep points concise (1-2 sentences).
Identify what works well. Be specific with examples from the resume.

**Areas for Improvement** (2-3 detailed points) . Keep points concise (1-2 sentences).
Provide actionable feedback on what needs work. For each point:
- Explain WHY it's an issue
- Provide a specific BEFORE/AFTER example or suggestion
- Explain the IMPACT of making this change

**ATS Optimization**.(2-3 sentences).
- Keyword analysis: What keywords are missing for their target role?
- Formatting issues that might confuse ATS systems
- Specific improvements for ATS compatibility

**Content Enhancement**.(2-3 sentences).
- Which bullet points lack impact or quantification?
- Where can achievements replace responsibilities?
- Specific suggestions to strengthen weak sections

**Industry-Specific Advice** . (2-3 sentences).
Based on the resume content, provide tailored advice for their specific industry/role.

**Action Plan** (Prioritized list) (1-2 sentences per changes).
List 4-7 changes in order of priority that will have the biggest impact.

Here is the resume/CV to analyze:

{resume_text}

Remember: Be direct, specific, and actionable. Use examples from their actual resume. Don't just say "improve your bullet points" - show them exactly how."""

        # Combine system and user prompts
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        def generate():
            print(f"[RESUME-STREAM] Calling Gemini streaming API...")
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse',
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'contents': [{
                        'parts': [{
                            'text': combined_prompt
                        }]
                    }],
                    'generationConfig': {
                        'temperature': 0.7,
                        'maxOutputTokens': 4000,
                    }
                },
                stream=True,
                timeout=120
            )
            
            print(f"[RESUME-STREAM] Response status: {response.status_code}")
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        # Parse Gemini's streaming response
                        try:
                            gemini_data = json.loads(decoded_line[6:])  # Remove 'data: ' prefix
                            
                            # Extract text from Gemini response
                            if 'candidates' in gemini_data:
                                text_delta = gemini_data['candidates'][0]['content']['parts'][0].get('text', '')
                                
                                # Convert to standard streaming format
                                standard_format = {
                                    'type': 'content_block_delta',
                                    'index': 0,
                                    'delta': {
                                        'type': 'text_delta',
                                        'text': text_delta
                                    }
                                }
                                
                                yield f"data: {json.dumps(standard_format)}\n\n"
                        except json.JSONDecodeError:
                            continue
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        print(f"[ERROR] Resume streaming exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini', methods=['POST'])
def gemini_proxy():
    """Proxy requests to Gemini API (non-streaming)"""
    try:
        data = request.json
        
        # Extract messages from request
        messages = data.get('messages', [])
        system_prompt = data.get('system', '')
        
        # Combine system prompt with messages
        combined_parts = []
        if system_prompt:
            combined_parts.append({'text': system_prompt + '\n\n'})
        
        # Convert messages to Gemini format
        for msg in messages:
            if isinstance(msg.get('content'), str):
                combined_parts.append({'text': msg['content']})
            elif isinstance(msg.get('content'), list):
                for content_block in msg['content']:
                    if content_block.get('type') == 'text':
                        combined_parts.append({'text': content_block['text']})
        
        # Non-streaming request
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'contents': [{
                    'parts': combined_parts
                }],
                'generationConfig': {
                    'temperature': data.get('temperature', 0.7),
                    'maxOutputTokens': data.get('max_tokens', 4000),
                }
            },
            timeout=30
        )
        
        if not response.ok:
            return jsonify({'error': response.text}), response.status_code
        
        # Convert Gemini response format to standard format
        gemini_response = response.json()
        
        # Extract text from Gemini response
        text_content = gemini_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # Format response in standard structure
        formatted_response = {
            'id': gemini_response.get('candidates', [{}])[0].get('content', {}).get('role', 'model'),
            'type': 'message',
            'role': 'assistant',
            'content': [{
                'type': 'text',
                'text': text_content
            }],
            'model': 'gemini-2.0-flash-exp',
            'stop_reason': gemini_response.get('candidates', [{}])[0].get('finishReason', 'end_turn'),
            'usage': {
                'input_tokens': gemini_response.get('usageMetadata', {}).get('promptTokenCount', 0),
                'output_tokens': gemini_response.get('usageMetadata', {}).get('candidatesTokenCount', 0)
            }
        }
        
        return jsonify(formatted_response), response.status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini/stream', methods=['POST'])
def gemini_stream():
    """Proxy requests to Gemini API with streaming support"""
    try:
        data = request.json
        
        # Extract messages from request
        messages = data.get('messages', [])
        system_prompt = data.get('system', '')
        
        # Combine system prompt with messages
        combined_parts = []
        if system_prompt:
            combined_parts.append({'text': system_prompt + '\n\n'})
        
        # Convert messages to Gemini format
        for msg in messages:
            if isinstance(msg.get('content'), str):
                combined_parts.append({'text': msg['content']})
            elif isinstance(msg.get('content'), list):
                for content_block in msg['content']:
                    if content_block.get('type') == 'text':
                        combined_parts.append({'text': content_block['text']})
        
        def generate():
            print(f"[GEMINI-STREAM] Starting stream...")
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse',
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'contents': [{
                        'parts': combined_parts
                    }],
                    'generationConfig': {
                        'temperature': data.get('temperature', 0.7),
                        'maxOutputTokens': data.get('max_tokens', 4000),
                    }
                },
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        # Parse Gemini's streaming response
                        try:
                            gemini_data = json.loads(decoded_line[6:])  # Remove 'data: ' prefix
                            
                            # Extract text from Gemini response
                            if 'candidates' in gemini_data:
                                text_delta = gemini_data['candidates'][0]['content']['parts'][0].get('text', '')
                                
                                # Convert to standard streaming format
                                standard_format = {
                                    'type': 'content_block_delta',
                                    'index': 0,
                                    'delta': {
                                        'type': 'text_delta',
                                        'text': text_delta
                                    }
                                }
                                
                                yield f"data: {json.dumps(standard_format)}\n\n"
                        except json.JSONDecodeError:
                            continue
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        print(f"[ERROR] Gemini stream error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elevenlabs/tts', methods=['POST'])
def elevenlabs_tts_proxy():
    """Proxy requests to ElevenLabs Text-to-Speech API"""
    try:
        if not ELEVENLABS_API_KEY:
            print("[ERROR] ElevenLabs API key not configured!")
            return jsonify({'error': 'ElevenLabs API key not configured on server'}), 500
        
        data = request.json
        voice_id = data.get('voice_id', '1SM7GgM6IMuvQlz2BwM3')
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        print(f"[TTS] Processing text ({language}): {text[:50]}...")
        
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVENLABS_API_KEY
        }
        
        # Use eleven_multilingual_v2 for automatic language detection
        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        
        response = requests.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if not response.ok:
            print(f"[ERROR] ElevenLabs TTS failed: {response.status_code} - {response.text}")
            return jsonify({'error': f'TTS API error: {response.status_code}'}), response.status_code
        
        print(f"[TTS] Success - Generated {len(response.content)} bytes of audio")
        return response.content, response.status_code, {'Content-Type': 'audio/mpeg'}
        
    except Exception as e:
        print(f"[ERROR] TTS exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/elevenlabs/tts/stream', methods=['POST'])
def elevenlabs_tts_stream():
    """Stream text-to-speech from ElevenLabs with WebSocket support"""
    try:
        data = request.json
        voice_id = data.get('voice_id', '1SM7GgM6IMuvQlz2BwM3')
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVENLABS_API_KEY
        }
        
        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        
        # Stream the audio response
        response = requests.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream',
            headers=headers,
            json=payload,
            stream=True,
            timeout=30
        )
        
        def generate():
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk
        
        return Response(
            stream_with_context(generate()),
            mimetype='audio/mpeg',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/elevenlabs/stt', methods=['POST'])
def elevenlabs_stt_proxy():
    """Proxy requests to ElevenLabs Speech-to-Text API - Uses scribe_v2 model with language support"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'en')  # Get language from request
        
        if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == 'YOUR_ELEVENLABS_API_KEY_HERE':
            print("[ERROR] ElevenLabs API key not configured!")
            return jsonify({'error': 'ElevenLabs API key not configured in server.py'}), 500
        
        headers = {
            'xi-api-key': ELEVENLABS_API_KEY
        }
        
        audio_data = audio_file.read()
        
        files = {
            'file': (audio_file.filename, audio_data, audio_file.content_type)
        }
        
        # Add language parameter - ElevenLabs supports 'en' and 'fr' language codes
        data = {
            'model_id': 'scribe_v2',
            'language': 'fr' if language == 'fr' else 'en'  # Specify the language
        }
        
        print(f"[STT] Transcribing audio file: {audio_file.filename} (Language: {data['language']})")
        response = requests.post(
            'https://api.elevenlabs.io/v1/speech-to-text',
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"[STT] Response status: {response.status_code}")
        
        if not response.ok:
            print(f"[ERROR] STT error: {response.text}")
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        print(f"[ERROR] STT exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    
    # Production settings
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Local development vs Production
    is_production = os.environ.get('RENDER') == 'True' or os.environ.get('PORT') != '5000'
    
    if is_production:
        print("🚀 Starting Intervue AI - PRODUCTION MODE")
        print("🌐 Server running on 0.0.0.0:" + str(port))
        app.run(host=host, port=port, debug=False)
    else:
        # Original development startup screen
        print("🚀 Starting AI Interview Trainer Server...")
        print("=" * 60)
        print("✅ FEATURES ENABLED:")
        print("   - Interview Mode with Real-time Streaming")
        print("   - Resume Analysis with Streaming TTS")
        print("   - Cold Email Review with Streaming TTS")
        print("   - Speech-to-Text (ElevenLabs Scribe)")
        print("   - Text-to-Speech (ElevenLabs)")
        print("   - Bilingual Support (English & French)")
        print("=" * 60)
        print("⚙️  API Configuration:")
        print(f"   - Gemini API: {'✅ Configured' if GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Not Configured'}")
        print(f"   - ElevenLabs API: {'✅ Configured' if ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != 'YOUR_ELEVENLABS_API_KEY_HERE' else '❌ Not Configured'}")
        print("=" * 60)
        print("🌐 Server running at: http://localhost:5000")
        print("📖 Open http://localhost:5000 in your browser")
        print("=" * 60)
        print("⚡ Powered by Google Gemini 2.0 Flash")
        print("=" * 60)
        app.run(debug=True, port=5000)