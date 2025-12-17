#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAVIDAS EVALUATOR - Final Working Version with Full API Support

Professor Nikolaos Lavidas
AI Essay Grading System

FEATURES:
- Support for ALL free and paid AI models
- Ollama local support (free, no API key)
- Multi-model fallback strategy
- Interactive API key configuration
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


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    # API Keys from environment or will be set interactively
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "").strip()
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()

    # Ollama local server
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    DEFAULT_MODEL = "ollama-llama2"
    DEFAULT_LANGUAGE = "Greek"
    DEFAULT_TONE = "supportive"
    DEFAULT_LENGTH = "detailed"
    DEFAULT_PERSON = "singular"
    DEFAULT_EVAL_TYPE = "standard"

    STYLE_FILE = "lavidas_style.txt"

    GRADING_SCALE = {
        "FAIL": (0.0, 4.9, "ΑΝΕΠΑΡΚΗΣ"),
        "PASS": (5.0, 6.4, "ΚΑΛΩΣ"),
        "VERY_GOOD": (6.5, 8.4, "ΛΙΑΝ ΚΑΛΩΣ"),
        "EXCELLENT": (8.5, 10.0, "ΑΡΙΣΤΑ"),
    }

    DEFAULT_SECTIONS: List[str] = []


# ============================================================================
# UTILITIES
# ============================================================================

def print_header(text: str):
    print(f"\n{'=' * 80}")
    print(f" {text}")
    print(f"{'=' * 80}\n")


def print_status(text: str, status: str = "info"):
    symbols = {
        "info": "[INFO]",
        "success": "[OK]",
        "error": "[ERROR]",
        "warning": "[WARN]",
        "processing": "[...]",
    }
    print(f"{symbols.get(status, '[INFO]')} {text}")


def check_ollama_available() -> bool:
    """Check if Ollama is running locally."""
    try:
        response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> List[str]:
    """List available models from Ollama."""
    try:
        response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [m.get("name", "").split(":")[0] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def setup_api_keys():
    """Interactive setup for all API keys."""
    print_header("⚙️ API KEYS CONFIGURATION")
    
    print("This tool supports multiple AI models. Configure as many as you want:\n")
    
    # Gemini
    print("1️⃣  GEMINI (Free tier available)")
    print("   Get key: https://aistudio.google.com/apikey")
    current_gemini = Config.GEMINI_API_KEY
    if current_gemini:
        print(f"   Current: {current_gemini[:20]}...")
        use_current = input("   Keep current? (y/n) [y]: ").strip().lower() or "y"
        if use_current != "y":
            Config.GEMINI_API_KEY = input("   Enter Gemini API Key: ").strip()
    else:
        Config.GEMINI_API_KEY = input("   Enter Gemini API Key (or press Enter to skip): ").strip()
    
    print()
    
    # Mistral
    print("2️⃣  MISTRAL (Free tier available)")
    print("   Get key: https://console.mistral.ai/api-keys/")
    current_mistral = Config.MISTRAL_API_KEY
    if current_mistral:
        print(f"   Current: {current_mistral[:20]}...")
        use_current = input("   Keep current? (y/n) [y]: ").strip().lower() or "y"
        if use_current != "y":
            Config.MISTRAL_API_KEY = input("   Enter Mistral API Key: ").strip()
    else:
        Config.MISTRAL_API_KEY = input("   Enter Mistral API Key (or press Enter to skip): ").strip()
    
    print()
    
    # Claude
    print("3️⃣  CLAUDE (Paid)")
    print("   Get key: https://console.anthropic.com/")
    current_claude = Config.CLAUDE_API_KEY
    if current_claude:
        print(f"   Current: {current_claude[:20]}...")
        use_current = input("   Keep current? (y/n) [y]: ").strip().lower() or "y"
        if use_current != "y":
            Config.CLAUDE_API_KEY = input("   Enter Claude API Key: ").strip()
    else:
        Config.CLAUDE_API_KEY = input("   Enter Claude API Key (or press Enter to skip): ").strip()
    
    print()
    
    # Perplexity
    print("4️⃣  PERPLEXITY (Paid)")
    print("   Get key: https://www.perplexity.ai/api/")
    current_perplexity = Config.PERPLEXITY_API_KEY
    if current_perplexity:
        print(f"   Current: {current_perplexity[:20]}...")
        use_current = input("   Keep current? (y/n) [y]: ").strip().lower() or "y"
        if use_current != "y":
            Config.PERPLEXITY_API_KEY = input("   Enter Perplexity API Key: ").strip()
    else:
        Config.PERPLEXITY_API_KEY = input("   Enter Perplexity API Key (or press Enter to skip): ").strip()
    
    print()


def check_api_keys():
    """Check available API keys and models."""
    print_header("📡 MODEL AVAILABILITY CHECK")
    
    available = []
    
    # Check Ollama
    if check_ollama_available():
        models = get_available_models()
        if models:
            print_status(f"✓ Ollama (Local - FREE). Models: {', '.join(models[:3])}", "success")
            available.append("ollama")
        else:
            print_status("⚠ Ollama running but no models installed", "warning")
    else:
        print_status("✗ Ollama not available (install from https://ollama.ai)", "warning")
    
    # Check Gemini
    if Config.GEMINI_API_KEY:
        print_status("✓ Gemini Flash (Free tier / Paid)", "success")
        available.append("gemini")
    else:
        print_status("✗ Gemini API key not set", "warning")
    
    # Check Mistral
    if Config.MISTRAL_API_KEY:
        print_status("✓ Mistral Large (Free tier / Paid)", "success")
        available.append("mistral")
    else:
        print_status("✗ Mistral API key not set", "warning")
    
    # Check Claude
    if Config.CLAUDE_API_KEY:
        print_status("✓ Claude Sonnet 3.5 (Paid)", "success")
        available.append("claude")
    else:
        print_status("✗ Claude API key not set", "warning")
    
    # Check Perplexity
    if Config.PERPLEXITY_API_KEY:
        print_status("✓ Perplexity Sonar (Paid)", "success")
        available.append("perplexity")
    else:
        print_status("✗ Perplexity API key not set", "warning")
    
    if not available:
        print_status("No models available!", "error")
        return False
    
    print(f"\nAvailable: {', '.join(available).upper()}")
    print()
    return True


# ============================================================================
# FILE EXTRACTION
# ============================================================================

class FileExtractor:
    @staticmethod
    def extract_from_pdf(file_path: Path) -> str:
        try:
            reader = PdfReader(str(file_path))
            text = "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
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
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"TXT extraction failed: {e}")

    @classmethod
    def extract(cls, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return cls.extract_from_pdf(file_path)
        elif suffix in [".docx", ".doc"]:
            return cls.extract_from_docx(file_path)
        elif suffix == ".txt":
            return cls.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")


# ============================================================================
# AI MODELS
# ============================================================================

class AIModel:
    @staticmethod
    def call_ollama(prompt: str, model: str = "llama2", temperature: float = 0.4) -> str:
        """Call local Ollama model (FREE, NO API KEY NEEDED)."""
        url = f"{Config.OLLAMA_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out (>300s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama network error: {e}")

    @staticmethod
    def call_gemini(
        api_key: str,
        prompt: str,
        temperature: float = 0.4,
        model: str = "flash",
    ) -> str:
        if model == "flash":
            model_name = "gemini-2.0-flash"
        else:
            model_name = "gemini-1.5-pro"

        url = (
            f"https://generativelanguage.googleapis.com/v1/models/"
            f"{model_name}:generateContent?key={api_key}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 8000,
                "topP": 0.95,
                "topK": 40,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,
            )
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", str(error_data))
                raise Exception(f"Gemini API Error: {error_msg}")

            data = response.json()
            if not data.get("candidates"):
                raise Exception("Empty response from Gemini")

            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.Timeout:
            raise Exception("Gemini API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini network error: {e}")

    @staticmethod
    def call_claude(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 8000,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=120
            )
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(
                    "Claude API Error: "
                    f"{error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            data = response.json()
            if not data.get("content"):
                raise Exception("Empty response from Claude")
            return data["content"][0].get("text", "")
        except requests.exceptions.Timeout:
            raise Exception("Claude API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude network error: {e}")

    @staticmethod
    def call_mistral(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.mistral.ai/v1/chat/completions"
        payload = {
            "model": "mistral-large-latest",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 8000,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=120
            )
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(
                    f"Mistral API Error: {error_data.get('message', 'Unknown error')}"
                )
            data = response.json()
            if not data.get("choices"):
                raise Exception("Empty response from Mistral")
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise Exception("Mistral API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mistral network error: {e}")

    @staticmethod
    def call_perplexity(api_key: str, prompt: str, temperature: float = 0.4) -> str:
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 8000,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=120
            )
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(
                    f"Perplexity API Error: {error_data.get('message', 'Unknown error')}"
                )
            data = response.json()
            if not data.get("choices"):
                raise Exception("Empty response from Perplexity")
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise Exception("Perplexity API request timed out (>120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Perplexity network error: {e}")

    @classmethod
    def call_ai(
        cls,
        prompt: str,
        model: str = "ollama-llama2",
        temperature: float = 0.4,
    ) -> str:
        """Call AI with automatic fallback strategy."""
        
        # Ollama models (local, free)
        if model.startswith("ollama-"):
            ollama_model = model.replace("ollama-", "")
            try:
                return cls.call_ollama(prompt, ollama_model, temperature)
            except Exception as e:
                print_status(f"Ollama failed: {e}. Trying fallback...", "warning")
                # Fall back to other models
                if Config.CLAUDE_API_KEY:
                    return cls.call_claude(Config.CLAUDE_API_KEY, prompt, temperature)
                elif Config.MISTRAL_API_KEY:
                    return cls.call_mistral(Config.MISTRAL_API_KEY, prompt, temperature)
                elif Config.PERPLEXITY_API_KEY:
                    return cls.call_perplexity(Config.PERPLEXITY_API_KEY, prompt, temperature)
                elif Config.GEMINI_API_KEY:
                    return cls.call_gemini(Config.GEMINI_API_KEY, prompt, temperature)
                else:
                    raise Exception("All models failed. Check configuration.")

        elif model == "gemini-flash":
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key not configured")
            return cls.call_gemini(Config.GEMINI_API_KEY, prompt, temperature, "flash")

        elif model == "gemini-pro":
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key not configured")
            return cls.call_gemini(Config.GEMINI_API_KEY, prompt, temperature, "pro")

        elif model == "claude":
            if not Config.CLAUDE_API_KEY:
                raise ValueError("Claude API key not configured")
            return cls.call_claude(Config.CLAUDE_API_KEY, prompt, temperature)

        elif model == "mistral":
            if not Config.MISTRAL_API_KEY:
                raise ValueError("Mistral API key not configured")
            return cls.call_mistral(Config.MISTRAL_API_KEY, prompt, temperature)

        elif model == "perplexity":
            if not Config.PERPLEXITY_API_KEY:
                raise ValueError("Perplexity API key not configured")
            return cls.call_perplexity(Config.PERPLEXITY_API_KEY, prompt, temperature)

        else:
            raise ValueError(f"Unknown model: {model}")


# ============================================================================
# STYLE TRAINER
# ============================================================================

class StyleTrainer:
    @staticmethod
    def train_from_folder(
        folder_path: Path,
        max_files: int = 5,
        model: str = "ollama-llama2",
    ) -> str:
        print_status("Analyzing your publications...", "processing")

        files: List[Path] = []
        for pattern in ["**/*.pdf", "**/*.docx", "**/*.txt"]:
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
1. Tone & Voice (e.g., Socratic, encouraging, rigorous, mentoring)
2. Greek Academic Vocabulary (characteristic phrases and terminology)
3. Feedback Philosophy (balance of criticism and encouragement)
4. Sentence Structures (typical patterns)
5. Pedagogical Approach (teaching and evaluation philosophy)

SAMPLE TEXTS:

{combined_text[:15000]}

Provide ONLY the style profile, no preamble.
"""

        print_status("Training AI on your style...", "processing")
        style = AIModel.call_ai(prompt, model=model, temperature=0.3)

        with open(Config.STYLE_FILE, "w", encoding="utf-8") as f:
            f.write(style)

        print_status("Style saved successfully!", "success")
        return style

    @staticmethod
    def load_style() -> Optional[str]:
        if Path(Config.STYLE_FILE).exists():
            with open(Config.STYLE_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @staticmethod
    def clear_style():
        if Path(Config.STYLE_FILE).exists():
            Path(Config.STYLE_FILE).unlink()
            print_status("Style cleared", "info")


# ============================================================================
# ESSAY GRADER
# ============================================================================

class EssayGrader:
    @staticmethod
    def grade_essay(
        essay_text: str,
        topic: str = "Essay Evaluation",
        language: str = "Greek",
        tone: str = "balanced",
        length: str = "detailed",
        person: str = "singular",
        eval_type: str = "standard",
        sections: Optional[List[str]] = None,
        model: str = "ollama-llama2",
    ) -> Dict:
        if sections is None:
            sections = Config.DEFAULT_SECTIONS

        style = (
            StyleTrainer.load_style()
            or "Standard academic style: constructive, evidence-based feedback."
        )

        lang_inst = (
            "OUTPUT LANGUAGE: Greek (Academic)"
            if language == "Greek"
            else "OUTPUT LANGUAGE: English (Academic)"
        )

        if person == "singular":
            person_inst = """PERSON/VOICE: Singular, direct address (Greek: second person singular)
- Use: "Η εργασία σου", "Συγχαρητήρια!", "Θα μπορούσες να βελτιώσεις..."
- Personal, encouraging, direct connection with student"""
        else:
            person_inst = """PERSON/VOICE: Impersonal, third person (Greek: third person)
- Use: "Η εργασία", "Ο φοιτητής/Η φοιτήτρια", "Θα μπορούσε να βελτιωθεί..."
- Formal, objective, professional distance"""

        if eval_type == "formal":
            eval_type_inst = """EVALUATION TYPE: Formal Academic Evaluation
- Focus on: Methodology, theoretical framework, academic rigor
- Include: Detailed analysis of sources, argumentation structure, scholarly contribution
- Tone: Professional, objective, comprehensive"""
        elif eval_type == "future_work":
            eval_type_inst = """EVALUATION TYPE: Future Work & Development Focus
- Focus on: Potential for expansion, areas for deeper exploration
- Include: Specific suggestions for further research, additional sources to consider"""
        else:
            eval_type_inst = """EVALUATION TYPE: Standard Essay Evaluation
- Focus on: Content, argumentation, clarity, evidence
- Balanced assessment of strengths and areas for improvement"""

        tone_map = {
            "supportive": "TONE: Very Supportive - Focus on potential and progress",
            "strict": "TONE: Strict Academic - High expectations with detailed critique",
            "balanced": "TONE: Balanced - Professional feedback with constructive approach",
        }

        length_map = {
            "brief": "EVALUATION LENGTH: Brief (200-400 words)",
            "detailed": "EVALUATION LENGTH: Detailed (500-700 words)",
            "extensive": "EVALUATION LENGTH: Extensive (800-1200 words)",
        }

        prompt = f"""
EVALUATOR: Professor Nikolaos Lavidas

YOUR WRITING STYLE:
{style}

{tone_map.get(tone, tone_map["balanced"])}
{length_map.get(length, length_map["detailed"])}

EVALUATION TASK:
Topic: "{topic}"

GREEK UNIVERSITY GRADING SCALE (0-10):
- 0.0-4.9: FAIL (ΑΝΕΠΑΡΚΗΣ)
- 5.0-6.4: PASS (ΚΑΛΩΣ)
- 6.5-8.4: VERY GOOD (ΛΙΑΝ ΚΑΛΩΣ)
- 8.5-10.0: EXCELLENT (ΑΡΙΣΤΑ)

EVALUATION REQUIREMENTS:
1. Give specific grade (e.g., 7.5)
2. {eval_type_inst}
3. Evidence: Quote passages from student text
4. Actionable feedback for improvement
5. {lang_inst}
6. {person_inst}

OUTPUT FORMAT:
First line - valid JSON:
{{"grade": "X.X", "verdict": "EXCELLENT/VERY_GOOD/PASS/FAIL"}}

Then your detailed evaluation in natural prose.

STUDENT ESSAY:
{essay_text[:12000]}
"""

        response = AIModel.call_ai(prompt, model=model, temperature=0.35)

        grade = "Draft"
        verdict = ""
        evaluation = response

        try:
            first_line = response.splitlines()[0].strip()
            json_str = None
            if first_line.startswith("{") and first_line.endswith("}"):
                json_str = first_line
            else:
                if "{" in response:
                    json_start = response.index("{")
                    json_end = response.index("}", json_start) + 1
                    json_str = response[json_start:json_end]

            if json_str:
                data = json.loads(json_str)
                grade = data.get("grade", "Draft")
                verdict = data.get("verdict", "")
                evaluation = response[len(json_str):].strip()
        except Exception:
            pass

        return {
            "grade": grade,
            "verdict": verdict,
            "evaluation": evaluation,
        }


# ============================================================================
# EMAIL GENERATOR
# ============================================================================

class EmailGenerator:
    ADE_TEMPLATE = """Agapites foitites kai agapitoi foitites,
kalispera sas! Elpizo na eiste oles kai oloi poli kala.

Molis tha echete lavei tin anatrofodotisi gia ti deyteri, mikri ypochreotiki ergasia sas. Simfona me ti diadikasia pou echei kathoristei apo to Metaptychiako Programma tou EAP, anakoinonetai o vathmos sinodoymenos apo mia sintomi, stochevmeni anatrofodotisi.

An epithymeite mia peraitero ekatomikevmeni sizitisi gia tin ergasia sas, eimai sti diathesi sas.

An echete opoiadipote erotisi, min distasete na epikoinonisete mazi mou.

Me thermous chairetismous,
Nikos Lavidas"""

    @classmethod
    def generate_ade_email(
        cls,
        course_details: str,
        model: str = "ollama-llama2",
    ) -> str:
        style = StyleTrainer.load_style() or "Professional, warm academic tone"
        prompt = f"""TASK: Adapt this email template for specific course details.

COURSE DETAILS: {course_details}

ORIGINAL TEMPLATE:
{cls.ADE_TEMPLATE}

INSTRUCTIONS:
- Keep the warm, professional tone
- Update details specific to this course
- Use Greek (formal academic, but personal)
- Keep signature 'Nikos Lavidas'
- Use this style: {style}

Provide ONLY the adapted email, no preamble.
"""
        return AIModel.call_ai(prompt, model=model, temperature=0.6)

    @staticmethod
    def generate_custom_email(
        course_details: str,
        custom_prompt: str,
        model: str = "ollama-llama2",
    ) -> str:
        style = StyleTrainer.load_style() or "Professional, warm academic tone"
        prompt = f"""TASK: Write a new email to students.

CONTEXT: {course_details}
USER INSTRUCTIONS: {custom_prompt}

STYLE: {style}
LANGUAGE: Greek (formal academic, but warm)
SIGNATURE: Nikos Lavidas

Write the email now:
"""
        return AIModel.call_ai(prompt, model=model, temperature=0.6)


# ============================================================================
# BATCH PROCESSOR
# ============================================================================

class BatchProcessor:
    @staticmethod
    def process_folder(
        folder_path: Path,
        topic: str = "Essay Evaluation",
        language: str = "Greek",
        tone: str = "balanced",
        length: str = "detailed",
        person: str = "singular",
        eval_type: str = "standard",
        sections: Optional[List[str]] = None,
        model: str = "ollama-llama2",
        output_file: str = "results.txt",
    ) -> List[Dict]:
        print_header("LAVIDAS EVALUATOR - Batch Processing")

        files: List[Path] = []
        for pattern in ["**/*.pdf", "**/*.docx", "**/*.doc", "**/*.txt"]:
            files.extend(list(folder_path.glob(pattern)))

        if not files:
            raise ValueError(f"No files found in {folder_path} or its subfolders")

        print_status(f"Folder: {folder_path}", "info")
        print_status(f"Found {len(files)} essays", "info")
        print_status(f"Model: {model}", "info")
        print_status(f"Length: {length}", "info")
        print_status(f"Tone: {tone}\n", "info")

        results: List[Dict] = []
        start_time = time.time()

        for i, file in enumerate(files, 1):
            try:
                try:
                    relative_path = file.relative_to(folder_path)
                except Exception:
                    relative_path = file.name

                print("\n" + "-" * 80)
                print(f"[{i}/{len(files)}] Processing: {relative_path}")
                print("-" * 80)

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
                    model=model,
                )

                result["filename"] = str(relative_path)
                result["full_path"] = str(file)
                results.append(result)

                print_status(
                    f"Grade: {result['grade']}/10 ({result['verdict']})",
                    "success",
                )
            except Exception as e:
                print_status(f"Error: {e}", "error")
                results.append(
                    {
                        "filename": str(relative_path),
                        "full_path": str(file),
                        "grade": "Error",
                        "verdict": "",
                        "evaluation": f"Error: {e}",
                    }
                )

        elapsed = time.time() - start_time

        print("\n" + "=" * 80)
        print_status("Saving results...", "processing")

        BatchProcessor.save_results(results, output_file, topic)

        print_header("COMPLETE")
        print_status(f"Processed: {len(files)} files", "success")
        print_status(
            f"Successful: {len([r for r in results if r['grade'] != 'Error'])}",
            "success",
        )
        print_status(
            f"Time: {int(elapsed // 60)}m {int(elapsed % 60)}s",
            "success",
        )
        print_status(f"Results: {output_file}\n", "success")

        return results

    @staticmethod
    def save_results(
        results: List[Dict],
        output_file: str,
        topic: str,
    ):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("LAVIDAS EVALUATOR - RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Topic: {topic}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Students: {len(results)}\n")
            f.write("=" * 80 + "\n\n")

            for result in results:
                f.write("\n" + "-" * 80 + "\n")
                f.write(f"STUDENT: {result['filename']}\n")
                f.write(f"GRADE: {result['grade']}/10")
                if result.get("verdict"):
                    f.write(f" ({result['verdict']})")
                f.write("\n" + "-" * 80 + "\n\n")
                f.write(result.get("evaluation", ""))
                f.write("\n\n")


# ============================================================================
# INTERACTIVE CLI
# ============================================================================

class InteractiveCLI:
    @staticmethod
    def main_menu() -> str:
        print_header("LAVIDAS EVALUATOR - Main Menu")
        print("1. Grade Essays (Batch Processing)")
        print("2. Train AI on Your Writing Style")
        print("3. Generate Email (ADE 52 Template)")
        print("4. Generate Custom Email")
        print("5. Configure API Keys")
        print("6. Check Model Availability")
        print("7. Exit\n")
        choice = input("Choice (1-7): ").strip()
        return choice

    @staticmethod
    def select_model() -> str:
        """Let user select from available models."""
        print("\nAvailable Models:")
        models = []
        
        if check_ollama_available():
            local_models = get_available_models()
            if local_models:
                for i, m in enumerate(local_models[:3], 1):
                    print(f"{i}. {m} (Local - FREE)")
                    models.append(f"ollama-{m}")
        
        next_idx = len(models) + 1
        
        if Config.GEMINI_API_KEY:
            print(f"{next_idx}. Gemini Flash (Free/Paid)")
            models.append("gemini-flash")
            next_idx += 1
        
        if Config.MISTRAL_API_KEY:
            print(f"{next_idx}. Mistral Large (Free/Paid)")
            models.append("mistral")
            next_idx += 1
        
        if Config.CLAUDE_API_KEY:
            print(f"{next_idx}. Claude Sonnet (Paid)")
            models.append("claude")
            next_idx += 1
        
        if Config.PERPLEXITY_API_KEY:
            print(f"{next_idx}. Perplexity Sonar (Paid)")
            models.append("perplexity")
            next_idx += 1
        
        if not models:
            print("No models available!")
            return None
        
        choice = input(f"Choice (1-{len(models)}) [1]: ").strip() or "1"
        try:
            return models[int(choice) - 1]
        except:
            return models[0]

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

        topic = input("Essay topic: ").strip() or "Essay evaluation"

        print("\nLanguage:")
        print("1. Greek")
        print("2. English")
        lang_choice = input("Choice (1-2) [1]: ").strip() or "1"
        language = "Greek" if lang_choice == "1" else "English"

        model = InteractiveCLI.select_model()
        if not model:
            return

        print("\n" + "-" * 80)
        print(f"Starting grading with model: {model}")
        print("-" * 80)

        try:
            BatchProcessor.process_folder(
                folder_path=folder,
                topic=topic,
                language=language,
                model=model,
                output_file="lavidas_results.txt",
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

        model = InteractiveCLI.select_model()
        if not model:
            return

        try:
            StyleTrainer.train_from_folder(folder, model=model)
        except Exception as e:
            print_status(f"Error: {e}", "error")

    @staticmethod
    def generate_ade_email_menu():
        print_header("Generate ADE 52 Email")
        course_details = input(
            "Course details (e.g., 'ADE 52 - Second Assignment'): "
        ).strip()
        if not course_details:
            print_status("Cancelled", "warning")
            return

        model = InteractiveCLI.select_model()
        if not model:
            return

        try:
            email = EmailGenerator.generate_ade_email(course_details, model=model)
            print("\n" + "=" * 80)
            print("EMAIL DRAFT")
            print("=" * 80 + "\n")
            print(email)
            print("\n" + "=" * 80)
            save = (
                input("\nSave to file? (y/n) [y]: ").strip().lower() or "y"
            )
            if save == "y":
                filename = (
                    f"email_draft_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                with open(filename, "w", encoding="utf-8") as f:
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

        lines: List[str] = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        custom_prompt = "\n".join(lines).strip()
        if not custom_prompt:
            print_status("Cancelled", "warning")
            return

        model = InteractiveCLI.select_model()
        if not model:
            return

        try:
            email = EmailGenerator.generate_custom_email(
                course_details, custom_prompt, model=model
            )
            print("\n" + "=" * 80)
            print("EMAIL DRAFT")
            print("=" * 80 + "\n")
            print(email)
            print("\n" + "=" * 80)
            save = (
                input("\nSave to file? (y/n) [y]: ").strip().lower() or "y"
            )
            if save == "y":
                filename = (
                    f"email_custom_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(email)
                print_status(f"Saved to: {filename}", "success")
        except Exception as e:
            print_status(f"Error: {e}", "error")

    @staticmethod
    def run():
        setup_api_keys()
        
        if not check_api_keys():
            print_status("Please configure at least one model", "error")
            return

        while True:
            choice = InteractiveCLI.main_menu()
            if choice == "1":
                InteractiveCLI.grade_essays_menu()
            elif choice == "2":
                InteractiveCLI.train_style_menu()
            elif choice == "3":
                InteractiveCLI.generate_ade_email_menu()
            elif choice == "4":
                InteractiveCLI.generate_custom_email_menu()
            elif choice == "5":
                setup_api_keys()
            elif choice == "6":
                check_api_keys()
                input("\nPress Enter to continue...")
            elif choice == "7":
                print_status("Goodbye!", "info")
                break
            else:
                print_status("Invalid choice", "warning")
                input("\nPress Enter to continue...")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    if len(sys.argv) == 1:
        InteractiveCLI.run()
        return

    if sys.argv[1] in ("--help", "-h"):
        print("""
LAVIDAS EVALUATOR - Full Multi-Model Support

AVAILABLE MODELS:
  1. Ollama (Local, FREE) - https://ollama.ai
     Models: llama2, mistral, neural-chat, etc.
  
  2. Gemini Flash (Free tier + Paid)
     https://aistudio.google.com/apikey
  
  3. Mistral Large (Free tier + Paid)
     https://console.mistral.ai/api-keys/
  
  4. Claude Sonnet 3.5 (Paid)
     https://console.anthropic.com/
  
  5. Perplexity Sonar (Paid)
     https://www.perplexity.ai/api/

QUICK START:
  python lavidas_evaluator_FINAL.py
  
  Then follow the prompts to configure your API keys.
""")
        return

    InteractiveCLI.run()


if __name__ == "__main__":
    main()
