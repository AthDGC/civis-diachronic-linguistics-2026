#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAVIDAS EVALUATOR - Complete Working Version
Professor Nikolaos Lavidas
AI Essay Grading System
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from PyPDF2 import PdfReader
from docx import Document

# CONFIGURATION
class Config:
    GEMINI_API_KEY = "AIzaSyFYmEijPBbZr5J7lw4teB794MIiRQ9o"
    MISTRAL_API_KEY = "SyFYmEijPBbZr5J7lw4teB794MIiRQ9o"
    CLAUDE_API_KEY = "YOUR_CLAUDE_API_KEY_HERE"
    PERPLEXITY_API_KEY = "YOUR_PERPLEXITY_API_KEY_HERE"
    
    DEFAULT_MODEL = "gemini-flash"
    DEFAULT_LANGUAGE = "Greek"
    DEFAULT_TONE = "supportive"
    DEFAULT_LENGTH = "detailed"
    DEFAULT_PERSON = "singular"  # "singular" or "impersonal"
    DEFAULT_EVAL_TYPE = "standard"  # "standard", "formal", "future_work"
    
    STYLE_FILE = "lavidas_style.txt"
    
    GRADING_SCALE = {
        "FAIL": (0.0, 4.9, "ΑΝΕΠΑΡΚΗΣ"),
        "PASS": (5.0, 6.4, "ΚΑΛΩΣ"),
        "VERY_GOOD": (6.5, 8.4, "ΛΙΑΝ ΚΑΛΩΣ"),
        "EXCELLENT": (8.5, 10.0, "ΑΡΙΣΤΑ")
    }
    
    DEFAULT_SECTIONS = []

# UTILITIES
def print_header(text: str):
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")

def print_status(text: str, status: str = "info"):
    symbols = {
        "info": "[INFO]",
        "success": "[OK]",
        "error": "[ERROR]",
        "warning": "[WARN]",
        "processing": "[...]"
    }
    print(f"{symbols.get(status, '[INFO]')} {text}")

# FILE EXTRACTION
class FileExtractor:
    @staticmethod
    def extract_from_pdf(file_path: Path) -> str:
        try:
            reader = PdfReader(str(file_path))
            text = "\n".join([page.extract_text() for page in reader.pages])
            return text
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {e}")
    
    @staticmethod
    def extract_from_docx(file_path: Path) -> str:
        try:
            doc = Document(str(file_path))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {e}")
    
    @staticmethod
    def extract_from_txt(file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"TXT extraction failed: {e}")
    
    @classmethod
    def extract(cls, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return cls.extract_from_docx(file_path)
        elif suffix == '.txt':
            return cls.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

# AI MODELS
class AIModel:
    @staticmethod
    def call_gemini(api_key: str, prompt: str, temperature: float = 0.4, 
                   model: str = 'flash') -> str:
        if model == 'flash':
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 8000,
                "topP": 0.95,
                "topK": 40
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        try:
            response = requests.post(url, json=payload, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=120)
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', str(error_data))
                raise Exception(f"Gemini API Error: {error_msg}")
            
            data = response.json()
            
            if not data.get('candidates') or len(data['candidates']) == 0:
                raise Exception("Empty response from Gemini")
            
            return data['candidates'][0]['content']['parts'][0]['text']
            
        except requests.exceptions.Timeout:
            raise Exception("API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
    
    @staticmethod
    def call_mistral(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.mistral.ai/v1/chat/completions"
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": temperature,
            "max_tokens": 8000
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(f"Mistral API Error: {error_data.get('message', 'Unknown error')}")
            
            data = response.json()
            
            if not data.get('choices') or len(data['choices']) == 0:
                raise Exception("Empty response from Mistral")
            
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception("Mistral API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mistral network error: {e}")
    
    @staticmethod
    def call_claude(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.anthropic.com/v1/messages"
        
        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8000,
            "temperature": temperature,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(f"Claude API Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            
            data = response.json()
            
            if not data.get('content') or len(data['content']) == 0:
                raise Exception("Empty response from Claude")
            
            return data['content'][0]['text']
            
        except requests.exceptions.Timeout:
            raise Exception("Claude API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude network error: {e}")
    
    @staticmethod
    def call_perplexity(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": temperature,
            "max_tokens": 8000
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(f"Perplexity API Error: {error_data.get('message', 'Unknown error')}")
            
            data = response.json()
            
            if not data.get('choices') or len(data['choices']) == 0:
                raise Exception("Empty response from Perplexity")
            
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception("Perplexity API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Perplexity network error: {e}")
    
    @classmethod
    def call_ai(cls, prompt: str, model: str = "gemini-flash", 
               temperature: float = 0.4) -> str:
        if model == "gemini-flash":
            return cls.call_gemini(Config.GEMINI_API_KEY, prompt, temperature, 'flash')
        elif model == "gemini-pro":
            return cls.call_gemini(Config.GEMINI_API_KEY, prompt, temperature, 'pro')
        elif model == "mistral":
            if not Config.MISTRAL_API_KEY or Config.MISTRAL_API_KEY == "YOUR_MISTRAL_API_KEY_HERE":
                raise ValueError("Mistral API key not configured")
            return cls.call_mistral(Config.MISTRAL_API_KEY, prompt, temperature)
        elif model == "claude":
            if not Config.CLAUDE_API_KEY or Config.CLAUDE_API_KEY == "YOUR_CLAUDE_API_KEY_HERE":
                raise ValueError("Claude API key not configured")
            return cls.call_claude(Config.CLAUDE_API_KEY, prompt, temperature)
        elif model == "perplexity":
            if not Config.PERPLEXITY_API_KEY or Config.PERPLEXITY_API_KEY == "YOUR_PERPLEXITY_API_KEY_HERE":
                raise ValueError("Perplexity API key not configured")
            return cls.call_perplexity(Config.PERPLEXITY_API_KEY, prompt, temperature)
        else:
            raise ValueError(f"Unknown model: {model}")

# STYLE TRAINER
class StyleTrainer:
    @staticmethod
    def train_from_folder(folder_path: Path, max_files: int = 5, 
                         model: str = "gemini-flash") -> str:
        print_status("Analyzing your publications...", "processing")
        
        files = []
        for pattern in ['**/*.pdf', '**/*.docx', '**/*.txt']:
            files.extend(list(folder_path.glob(pattern)))
        
        if not files:
            raise ValueError(f"No readable files found in {folder_path}")
        
        combined_text = ""
        count = 0
        
        for file in files[:max_files]:
            try:
                text = FileExtractor.extract(file)
                combined_text += f"\n----- {file.name} -----\n{text[:5000]}\n"
                count += 1
                print_status(f"Read: {file.name}", "success")
            except Exception as e:
                print_status(f"Skipped {file.name}: {e}", "warning")
        
        if not combined_text:
            raise ValueError("Could not extract text from any files")
        
        prompt = f"""TASK: Analyze the academic writing style of Professor Nikolaos Lavidas.

OUTPUT: Create a concise "Style Profile" (max 400 words) that captures:

1. Tone & Voice: (e.g., Socratic, encouraging, rigorous, mentoring)
2. Greek Academic Vocabulary: Characteristic phrases and terminology
3. Feedback Philosophy: How he balances criticism with encouragement
4. Sentence Structures: Typical patterns
5. Pedagogical Approach: Teaching and evaluation philosophy

SAMPLE TEXTS:
{combined_text[:15000]}

Provide ONLY the style profile, no preamble."""
        
        print_status("Training AI on your style...", "processing")
        style = AIModel.call_ai(prompt, model=model, temperature=0.3)
        
        with open(Config.STYLE_FILE, 'w', encoding='utf-8') as f:
            f.write(style)
        
        print_status("Style saved successfully!", "success")
        return style
    
    @staticmethod
    def load_style() -> Optional[str]:
        if Path(Config.STYLE_FILE).exists():
            with open(Config.STYLE_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    @staticmethod
    def clear_style():
        if Path(Config.STYLE_FILE).exists():
            Path(Config.STYLE_FILE).unlink()
            print_status("Style cleared", "info")

# ESSAY GRADER
class EssayGrader:
    @staticmethod
    def grade_essay(essay_text: str, 
                   topic: str = "Essay Evaluation",
                   language: str = "Greek",
                   tone: str = "balanced",
                   length: str = "detailed",
                   person: str = "singular",
                   eval_type: str = "standard",
                   sections: List[str] = None,
                   model: str = "gemini-flash") -> Dict:
        
        if sections is None:
            sections = Config.DEFAULT_SECTIONS
        
        style = StyleTrainer.load_style() or \
                "Standard academic style: constructive, evidence-based feedback."
        
        lang_inst = "OUTPUT LANGUAGE: Greek (Academic)" if language == "Greek" \
                    else "OUTPUT LANGUAGE: English (Academic)"
        
        person_inst = ""
        if person == "singular":
            person_inst = """PERSON/VOICE: Singular, direct address (Greek: second person singular)
- Use: "Η εργασία σου", "Συγχαρητήρια!", "Θα μπορούσες να βελτιώσεις..."
- Example: "Η εργασία σου παρουσιάζει ενδιαφέροντα στοιχεία. Συγχαρητήρια για την προσπάθειά σου!"
- Personal, encouraging, direct connection with student"""
        else:
            person_inst = """PERSON/VOICE: Impersonal, third person (Greek: third person)
- Use: "Η εργασία", "Ο φοιτητής/Η φοιτήτρια", "Θα μπορούσε να βελτιωθεί..."
- Example: "Η εργασία παρουσιάζει ενδιαφέροντα στοιχεία. Η προσπάθεια είναι εμφανής."
- Formal, objective, professional distance"""
        
        eval_type_inst = ""
        if eval_type == "formal":
            eval_type_inst = """EVALUATION TYPE: Formal Academic Evaluation
- Focus on: Methodology, theoretical framework, academic rigor
- Include: Detailed analysis of sources, argumentation structure, scholarly contribution
- Tone: Professional, objective, comprehensive
- Suitable for: Thesis chapters, journal submissions, formal research papers"""
        elif eval_type == "future_work":
            eval_type_inst = """EVALUATION TYPE: Future Work & Development Focus
- Focus on: Potential for expansion, areas for deeper exploration
- Include: Specific suggestions for further research, additional sources to consider
- Highlight: Promising directions, unexplored angles, connections to broader field
- End with: Concrete next steps for developing this work further
- Tone: Forward-looking, developmental, encouraging growth"""
        else:
            eval_type_inst = """EVALUATION TYPE: Standard Essay Evaluation
- Focus on: Content, argumentation, clarity, evidence
- Balanced assessment of strengths and areas for improvement
- Practical feedback for current assignment"""
        
        tone_map = {
            "supportive": """TONE: Very Supportive (10/10)
- Focus on potential and progress
- Use encouraging phrases
- Gentle, constructive criticism""",
            
            "strict": """TONE: Strict Academic (9/10)
- High expectations with detailed critique
- Point out every weakness clearly
- Demand accuracy and depth""",
            
            "balanced": """TONE: Balanced (7/10)
- Professional feedback
- Highlight both strengths and areas for improvement
- Constructive approach"""
        }
        
        length_map = {
            "brief": "EVALUATION LENGTH: Brief (200-400 words)",
            "detailed": "EVALUATION LENGTH: Detailed (500-700 words)",
            "extensive": "EVALUATION LENGTH: Extensive (800-1200 words)"
        }
        
        sections_text = ""
        if sections:
            sections_text = "Structure your evaluation with these sections:\n" + \
                          "\n".join([f"   ### {s}" for s in sections])
        else:
            sections_text = "Structure your evaluation naturally - no required sections"
        
        prompt = f"""
EVALUATOR: Professor Nikolaos Lavidas

YOUR ESTABLISHED WRITING STYLE:
{style}

{tone_map[tone]}

{length_map[length]}

EVALUATION TASK:
Topic: "{topic}"

GREEK UNIVERSITY GRADING SCALE (0-10):
- 0.0 - 4.9: FAIL
- 5.0 - 6.4: PASS/GOOD
- 6.5 - 8.4: VERY GOOD
- 8.5 - 10.0: EXCELLENT

EVALUATION REQUIREMENTS:
1. Precise Grade: Give specific grade (e.g., 7.5, 8.8)
2. {sections_text}
3. {eval_type_inst}
4. Evidence: Quote specific passages from student text where relevant
5. Actionable Feedback: Specific suggestions for improvement
6. {lang_inst}
7. {person_inst}
8. Write in a natural, flowing academic style - avoid mechanical formatting

OUTPUT FORMAT (EXACTLY THIS FORMAT):
First line - valid JSON:
{{"grade": "X.X", "verdict": "EXCELLENT/VERY GOOD/GOOD/FAIL"}}

Then, your detailed evaluation in natural prose.

STUDENT ESSAY:
{essay_text[:15000]}
"""
        
        response = AIModel.call_ai(prompt, model=model, temperature=0.35)
        
        grade = "Draft"
        verdict = ""
        evaluation = response
        
        try:
            if '{' in response:
                json_start = response.index('{')
                json_end = response.index('}', json_start) + 1
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                grade = data.get('grade', 'Draft')
                verdict = data.get('verdict', '')
                evaluation = response[json_end:].strip()
        except:
            pass
        
        return {
            'grade': grade,
            'verdict': verdict,
            'evaluation': evaluation
        }

# EMAIL GENERATOR
class EmailGenerator:
    ADE_TEMPLATE = """Agapites foitities kai agapitoi foitites,

kalispera sas! Elpizo na eiste oles kai oloi poli kala.

Molis tha echete lavei tin anatrofodotisi gia ti deyteri, mikri ypochreotiki ergasia sas. Simfona me ti diadikasia pou echei kathoristei apo to Metaptychiako Programma tou EAP gia oles tis thematikes enotites, anakoinonetai o vathmos sinodoymenos apo mia sintomi, stochevmeni anatrofodotisi. I anatrofodotisi ayti parechetai meta tin oloklirosi tis prothesmias ypovolis, oste na diasfalistei i antikeimenikotita kai i omoiogeneia tis aksiologisis.

I anatrofodotisi echei schediasei oste na sas prosferei mia proti, oysiasti eikona gia ta simeia pou petychate kai ayta pou chreazontai peraitero prosochi.

An epithymeite mia peraitero ekatomikevmeni, leptomeri sizitisi gia tin ergasia sas, eimai sti diathesi sas gia na tin pragmatopoiisoyme eite meso ilektronikon minimatom, eite tilefonika, eite meso Webex, eite kai kata tin omadiki symvoylevtiki synantisi.

An echete opoiadipote erotisi, aporia i chreazeste peraitero kathodighisi, min distasete na epikoinonisete mazi mou.

I epikoinonia mas paramenei anoichti kai synechis, eidika se ayto to stadio tis ekpaideftikis diadikasias.

Sas eychomai kali synecheia kai perimeno me chara tis skepseis kai ta scholia sas.

Me thermous chairetismous,

Nikos Lavidas"""
    
    @classmethod
    def generate_ade_email(cls, course_details: str, model: str = "gemini-flash") -> str:
        style = StyleTrainer.load_style() or "Professional, warm academic tone"
        
        prompt = f"""TASK: Adapt this email template for specific course details.

COURSE DETAILS: {course_details}

INSTRUCTIONS:
- KEEP: The warm, professional tone and structure
- UPDATE: Details specific to this course/assignment
- LANGUAGE: Greek (formal academic, but warm)
- SIGNATURE: Keep 'Nikos Lavidas'

WRITING STYLE:
{style}

ORIGINAL TEMPLATE:
{cls.ADE_TEMPLATE}
"""
        
        return AIModel.call_ai(prompt, model=model, temperature=0.6)
    
    @staticmethod
    def generate_custom_email(course_details: str, custom_prompt: str, 
                            model: str = "gemini-flash") -> str:
        style = StyleTrainer.load_style() or "Professional, warm academic tone"
        
        prompt = f"""TASK: Write a new email to students.

CONTEXT: {course_details}

USER INSTRUCTIONS: {custom_prompt}

WRITING STYLE (use this style):
{style}

LANGUAGE: Greek (formal academic, but personal and warm)
SIGNATURE: Nikos Lavidas

Write the email now:
"""
        
        return AIModel.call_ai(prompt, model=model, temperature=0.6)

# BATCH PROCESSOR
class BatchProcessor:
    @staticmethod
    def process_folder(folder_path: Path,
                      topic: str = "Essay Evaluation",
                      language: str = "Greek",
                      tone: str = "balanced",
                      length: str = "detailed",
                      person: str = "singular",
                      eval_type: str = "standard",
                      sections: List[str] = None,
                      model: str = "gemini-flash",
                      output_file: str = "results.txt") -> List[Dict]:
        
        print_header("LAVIDAS EVALUATOR - Batch Processing")
        
        files = []
        for pattern in ['**/*.pdf', '**/*.docx', '**/*.doc', '**/*.txt']:
            files.extend(list(folder_path.glob(pattern)))
        
        if not files:
            raise ValueError(f"No files found in {folder_path} or its subfolders")
        
        print_status(f"Folder: {folder_path}", "info")
        print_status(f"Found {len(files)} essays (including subfolders)", "info")
        print_status(f"Model: {model}", "info")
        print_status(f"Length: {length}", "info")
        print_status(f"Tone: {tone}\n", "info")
        
        results = []
        start_time = time.time()
        
        for i, file in enumerate(files, 1):
            try:
                relative_path = file.relative_to(folder_path)
            except:
                relative_path = file.name
            
            print(f"\n{'-' * 80}")
            print(f"[{i}/{len(files)}] Processing: {relative_path}")
            print(f"{'-' * 80}")
            
            try:
                print_status("Extracting text...", "processing")
                text = FileExtractor.extract(file)
                
                print_status("Grading...", "processing")
                result = EssayGrader.grade_essay(
                    essay_text=text,
                    topic=topic,
                    language=language,
                    tone=tone,
                    length=length,
                    person=person,
                    eval_type=eval_type,
                    sections=sections,
                    model=model
                )
                
                result['filename'] = str(relative_path)
                result['full_path'] = str(file)
                results.append(result)
                
                print_status(f"Grade: {result['grade']}/10 ({result['verdict']})", "success")
                
            except Exception as e:
                print_status(f"Error: {e}", "error")
                results.append({
                    'filename': str(relative_path),
                    'full_path': str(file),
                    'grade': 'Error',
                    'verdict': '',
                    'evaluation': f"Error: {e}"
                })
        
        elapsed = time.time() - start_time
        
        print(f"\n{'=' * 80}")
        print_status("Generating class analysis...", "processing")
        
        analytics = BatchProcessor.generate_analytics(results, topic, language, model)
        
        BatchProcessor.save_results(results, analytics, output_file, topic)
        
        print_header("COMPLETE")
        print_status(f"Processed: {len(files)} files", "success")
        print_status(f"Successful: {len([r for r in results if r['grade'] != 'Error'])}", "success")
        print_status(f"Time: {int(elapsed // 60)}m {int(elapsed % 60)}s", "success")
        print_status(f"Results: {output_file}\n", "success")
        
        return results
    
    @staticmethod
    def generate_analytics(results: List[Dict], topic: str, 
                          language: str, model: str) -> str:
        valid_results = [r for r in results if r['grade'] != 'Error']
        
        if not valid_results:
            return "No valid results to analyze."
        
        grades = []
        for r in valid_results:
            try:
                grades.append(float(r['grade']))
            except:
                pass
        
        avg_grade = sum(grades) / len(grades) if grades else 0
        
        distribution = {
            "FAIL": 0,
            "PASS": 0,
            "VERY_GOOD": 0,
            "EXCELLENT": 0
        }
        
        for g in grades:
            if g < 5.0:
                distribution["FAIL"] += 1
            elif g < 6.5:
                distribution["PASS"] += 1
            elif g < 8.5:
                distribution["VERY_GOOD"] += 1
            else:
                distribution["EXCELLENT"] += 1
        
        grade_list = "\n".join([
            f"{r['filename']}: {r['grade']}/10 ({r['verdict']})"
            for r in valid_results
        ])
        
        prompt = f"""TASK: Write comprehensive class performance analysis.

DATA:
- Total Students: {len(valid_results)}
- Assignment Topic: {topic}
- Average Grade: {avg_grade:.2f}/10
- Distribution:
  * FAIL (<5): {distribution['FAIL']}
  * PASS (5-6.4): {distribution['PASS']}
  * VERY GOOD (6.5-8.4): {distribution['VERY_GOOD']}
  * EXCELLENT (8.5-10): {distribution['EXCELLENT']}

Grades:
{grade_list}

REQUIREMENTS:
1. Grade Distribution (table with percentages)
2. Overall Performance Summary
3. Common Strengths
4. Common Weaknesses
5. Top 3 Students (with grades and brief justification)
6. Recommendations for Next Lecture

LANGUAGE: {"Greek (formal academic)" if language == "Greek" else "English (formal academic)"}
"""
        
        try:
            return AIModel.call_ai(prompt, model=model, temperature=0.5)
        except Exception as e:
            return f"Error generating analytics: {e}"
    
    @staticmethod
    def save_results(results: List[Dict], analytics: str, 
                    output_file: str, topic: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LAVIDAS EVALUATOR - RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Topic: {topic}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Students: {len(results)}\n")
            f.write("=" * 80 + "\n\n")
            
            for result in results:
                f.write(f"\n{'-' * 80}\n")
                f.write(f"STUDENT: {result['filename']}\n")
                f.write(f"GRADE: {result['grade']}/10")
                if result['verdict']:
                    f.write(f" ({result['verdict']})")
                f.write(f"\n{'-' * 80}\n\n")
                f.write(result['evaluation'])
                f.write(f"\n\n")
            
            f.write(f"\n{'=' * 80}\n")
            f.write("CLASS PERFORMANCE ANALYSIS\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(analytics)
            f.write("\n\n")

# INTERACTIVE CLI
class InteractiveCLI:
    @staticmethod
    def main_menu():
        print_header("LAVIDAS EVALUATOR - Main Menu")
        print("1. Grade Essays (Batch Processing)")
        print("2. Train AI on Your Writing Style")
        print("3. Generate Email (ADE 52 Template)")
        print("4. Generate Custom Email")
        print("5. Configure Settings")
        print("6. Exit")
        print()
        
        choice = input("Choice (1-6): ").strip()
        return choice
    
    @staticmethod
    def grade_essays_menu():
        print_header("Batch Essay Grading")
        
        folder_path = input("Essay folder path: ").strip()
        if not folder_path:
            print_status("Cancelled", "warning")
            return
        
        folder = Path(folder_path)
        if not folder.exists():
            print_status(f"Folder not found: {folder_path}", "error")
            return
        
        topic = input(f"Essay topic: ").strip() or "Essay evaluation"
        
        print("\nLanguage:")
        print("1. Greek")
        print("2. English")
        lang_choice = input("Choice (1-2) [1]: ").strip() or "1"
        language = "Greek" if lang_choice == "1" else "English"
        
        print("\nEvaluation Tone:")
        print("1. Balanced")
        print("2. Strict")
        print("3. Supportive")
        tone_choice = input("Choice (1-3) [3]: ").strip() or "3"
        tone = ["balanced", "strict", "supportive"][int(tone_choice) - 1]
        
        print("\nEvaluation Length:")
        print("1. Brief (200-400 words)")
        print("2. Detailed (500-700 words)")
        print("3. Extensive (800-1200 words)")
        length_choice = input("Choice (1-3) [2]: ").strip() or "2"
        length = ["brief", "detailed", "extensive"][int(length_choice) - 1]
        
        print("\nPerson/Voice:")
        print("1. Singular (Η εργασία σου, Συγχαρητήρια!)")
        print("2. Impersonal (Η εργασία, Ο φοιτητής)")
        person_choice = input("Choice (1-2) [1]: ").strip() or "1"
        person = "singular" if person_choice == "1" else "impersonal"
        
        print("\nEvaluation Type:")
        print("1. Standard (Regular essay evaluation)")
        print("2. Formal (Academic rigor, methodology, theoretical framework)")
        print("3. Future Work (Development focus, research directions)")
        eval_type_choice = input("Choice (1-3) [1]: ").strip() or "1"
        eval_type = ["standard", "formal", "future_work"][int(eval_type_choice) - 1]
        
        print("\nAI Model:")
        print("1. Gemini Flash (Fastest, Free)")
        print("2. Gemini Pro (Best Quality, Free)")
        print("3. Claude Sonnet 4 (Excellent, Paid)")
        print("4. Mistral Large (European, Paid)")
        print("5. Perplexity (Research-focused, Paid)")
        model_choice = input("Choice (1-5) [1]: ").strip() or "1"
        model = ["gemini-flash", "gemini-pro", "claude", "mistral", "perplexity"][int(model_choice) - 1]
        
        print("\n" + "-" * 80)
        print("Summary:")
        print(f"  Folder: {folder}")
        print(f"  Topic: {topic}")
        print(f"  Language: {language}")
        print(f"  Tone: {tone}")
        print(f"  Length: {length}")
        print(f"  Person: {person}")
        print(f"  Eval Type: {eval_type}")
        print(f"  Model: {model}")
        print("-" * 80)
        
        confirm = input("\nStart? (y/n) [y]: ").strip().lower() or "y"
        
        if confirm != 'y':
            print_status("Cancelled", "warning")
            return
        
        try:
            BatchProcessor.process_folder(
                folder_path=folder,
                topic=topic,
                language=language,
                tone=tone,
                length=length,
                person=person,
                eval_type=eval_type,
                model=model,
                output_file="lavidas_results.txt"
            )
        except Exception as e:
            print_status(f"Error: {e}", "error")
    
    @staticmethod
    def train_style_menu():
        print_header("Train AI on Your Writing Style")
        
        folder_path = input("Publications folder path: ").strip()
        if not folder_path:
            print_status("Cancelled", "warning")
            return
        
        folder = Path(folder_path)
        if not folder.exists():
            print_status(f"Folder not found: {folder_path}", "error")
            return
        
        print("\nModel for training:")
        print("1. Gemini Flash (Recommended)")
        print("2. Gemini Pro")
        model_choice = input("Choice (1-2) [1]: ").strip() or "1"
        model = "gemini-flash" if model_choice == "1" else "gemini-pro"
        
        try:
            StyleTrainer.train_from_folder(folder, model=model)
        except Exception as e:
            print_status(f"Error: {e}", "error")
    
    @staticmethod
    def generate_ade_email_menu():
        print_header("Generate ADE 52 Email")
        
        course_details = input("Course details (e.g., 'ADE 52 - Second Assignment'): ").strip()
        if not course_details:
            print_status("Cancelled", "warning")
            return
        
        print("\nAI Model:")
        print("1. Gemini Flash")
        print("2. Gemini Pro")
        model_choice = input("Choice (1-2) [1]: ").strip() or "1"
        model = "gemini-flash" if model_choice == "1" else "gemini-pro"
        
        try:
            email = EmailGenerator.generate_ade_email(course_details, model=model)
            
            print("\n" + "=" * 80)
            print("EMAIL DRAFT")
            print("=" * 80 + "\n")
            print(email)
            print("\n" + "=" * 80)
            
            save = input("\nSave to file? (y/n) [y]: ").strip().lower() or "y"
            if save == 'y':
                filename = f"email_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(email)
                print_status(f"Saved to: {filename}", "success")
        
        except Exception as e:
            print_status(f"Error: {e}", "error")
    
    @staticmethod
    def generate_custom_email_menu():
        print_header("Generate Custom Email")
        
        course_details = input("Course context: ").strip()
        if not course_details:
            print_status("Cancelled", "warning")
            return
        
        print("\nWhat should the email say?")
        print("(Type your instructions, press Enter twice when done)")
        
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        custom_prompt = "\n".join(lines).strip()
        
        if not custom_prompt:
            print_status("Cancelled", "warning")
            return
        
        print("\nAI Model:")
        print("1. Gemini Flash")
        print("2. Gemini Pro")
        model_choice = input("Choice (1-2) [1]: ").strip() or "1"
        model = "gemini-flash" if model_choice == "1" else "gemini-pro"
        
        try:
            email = EmailGenerator.generate_custom_email(course_details, custom_prompt, model=model)
            
            print("\n" + "=" * 80)
            print("EMAIL DRAFT")
            print("=" * 80 + "\n")
            print(email)
            print("\n" + "=" * 80)
            
            save = input("\nSave to file? (y/n) [y]: ").strip().lower() or "y"
            if save == 'y':
                filename = f"email_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(email)
                print_status(f"Saved to: {filename}", "success")
        
        except Exception as e:
            print_status(f"Error: {e}", "error")
    
    @staticmethod
    def configure_settings():
        print_header("Configure Settings")
        
        print("Current settings:")
        print(f"  Default Model: {Config.DEFAULT_MODEL}")
        print(f"  Default Language: {Config.DEFAULT_LANGUAGE}")
        print(f"  Default Tone: {Config.DEFAULT_TONE}")
        print(f"  Default Length: {Config.DEFAULT_LENGTH}")
        print()
        
        print("(This is read-only. Edit Config class in script to change defaults)")
        input("\nPress Enter to continue...")
    
    @staticmethod
    def run():
        if Config.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print_status("WARNING: Gemini API key not configured!", "error")
            print_status("Edit Config.GEMINI_API_KEY in the script", "info")
            print()
        
        while True:
            choice = InteractiveCLI.main_menu()
            
            if choice == '1':
                InteractiveCLI.grade_essays_menu()
            elif choice == '2':
                InteractiveCLI.train_style_menu()
            elif choice == '3':
                InteractiveCLI.generate_ade_email_menu()
            elif choice == '4':
                InteractiveCLI.generate_custom_email_menu()
            elif choice == '5':
                InteractiveCLI.configure_settings()
            elif choice == '6':
                print_status("Goodbye!", "info")
                break
            else:
                print_status("Invalid choice", "warning")
            
            input("\nPress Enter to continue...")

# MAIN ENTRY POINT
def main():
    if len(sys.argv) == 1:
        InteractiveCLI.run()
    else:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("""
LAVIDAS EVALUATOR - Command-Line Usage

INTERACTIVE MODE:
  python lavidas_evaluator.py

BATCH MODE:
  python lavidas_evaluator.py <folder_path> [options]

OPTIONS:
  --topic "Topic"           Essay topic
  --language greek|english  Output language
  --tone balanced|strict|supportive
  --length brief|detailed|extensive
  --person singular|impersonal        Voice (singular: "σου", impersonal: "η εργασία")
  --eval-type standard|formal|future_work   Evaluation focus
  --model flash|pro|claude|mistral|perplexity   AI model
  --output file.txt         Output filename

EVALUATION TYPES:
  standard     Regular essay evaluation (default)
  formal       Focus on methodology, theoretical framework, academic rigor
  future_work  Development focus with research directions and next steps

MODELS:
  flash        Gemini Flash (fastest, free)
  pro          Gemini Pro (best quality, free)
  claude       Claude Sonnet 4 (excellent, paid)
  mistral      Mistral Large (European, paid)
  perplexity   Perplexity (research-focused, paid)

EXAMPLES:
  python lavidas_evaluator.py ./essays
  python lavidas_evaluator.py ./essays --tone strict --length extensive
  python lavidas_evaluator.py ./essays --person singular --eval-type formal
  python lavidas_evaluator.py ./essays --eval-type future_work --model claude
""")
            return
        
        folder_path = sys.argv[1]
        folder = Path(folder_path)
        
        if not folder.exists():
            print_status(f"Folder not found: {folder_path}", "error")
            return
        
        topic = "Essay evaluation"
        language = Config.DEFAULT_LANGUAGE
        tone = Config.DEFAULT_TONE
        length = Config.DEFAULT_LENGTH
        person = Config.DEFAULT_PERSON
        eval_type = Config.DEFAULT_EVAL_TYPE
        model = Config.DEFAULT_MODEL
        output = "lavidas_results.txt"
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--topic' and i + 1 < len(sys.argv):
                topic = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--language' and i + 1 < len(sys.argv):
                language = "Greek" if sys.argv[i + 1].lower() == 'greek' else "English"
                i += 2
            elif sys.argv[i] == '--tone' and i + 1 < len(sys.argv):
                tone = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--length' and i + 1 < len(sys.argv):
                length = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--person' and i + 1 < len(sys.argv):
                person = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--eval-type' and i + 1 < len(sys.argv):
                eval_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--model' and i + 1 < len(sys.argv):
                m = sys.argv[i + 1]
                model = "gemini-flash" if m == "flash" else \
                        "gemini-pro" if m == "pro" else \
                        "claude" if m == "claude" else \
                        "perplexity" if m == "perplexity" else "mistral"
                i += 2
            elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
                output = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        try:
            BatchProcessor.process_folder(
                folder_path=folder,
                topic=topic,
                language=language,
                tone=tone,
                length=length,
                person=person,
                eval_type=eval_type,
                model=model,
                output_file=output
            )
        except Exception as e:
            print_status(f"Error: {e}", "error")

if __name__ == "__main__":
    main()
