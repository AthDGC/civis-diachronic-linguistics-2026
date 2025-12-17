DIACHRONIC VALENCY LEXICON PILOT STUDY

THE 6 TARGET VERBS (Reduced List)

Give-verbs (2):

1. δίδωμι (Ancient) → δίνω (Modern) | English: gifan → give
2. παρέχω (Ancient) → παρέχω (Modern, formal) | English: giefen → provide

Say-verbs (2):

3. λέγω (Ancient) → λέω (Modern) | English: secgan → say
4. ἀγγέλλω (Ancient) → αγγέλλω (Modern, formal) | English: cyþan → tell

Psych-verbs (2):

5. φοβέομαι (Ancient) → φοβάμαι (Modern) | English: ondrædan → fear
6. θαυμάζω (Ancient) → θαυμάζω (Modern) | English: wundrian → wonder

SETUP: CREATE YOUR PROJECT FOLDER

Everyone does this first!

For Windows:

1. Go to Desktop
2. Right-click → New → Folder
3. Name it: valency_project
4. Open Command Prompt (Windows key + R, type cmd, press Enter)
5. Type: cd Desktop\valency_project

For Mac:

1. Go to Desktop
2. Right-click → New Folder
3. Name it: valency_project
4. Open Terminal (Command + Space, type terminal)
5. Type: cd Desktop/valency_project

Your folder path: Desktop/valency_project

STEP 1: SETUP & DATA EXTRACTION

Download Corpora & Install Python

EVERYONE: Download Greek Corpora

Windows (Command Prompt):

cd Desktop\valency_project
mkdir corpora
cd corpora

curl -L -o proiel.zip https://github.com/proiel/proiel-treebank/archive/refs/heads/master.zip
curl -L -o greek-ud.zip https://github.com/UniversalDependencies/UD_Greek-GDT/archive/refs/heads/master.zip

tar -xf proiel.zip
tar -xf greek-ud.zip

move proiel-treebank-master proiel-treebank
move UD_Greek-GDT-master UD_Greek-GDT

Mac (Terminal):

cd Desktop/valency_project
mkdir corpora
cd corpora

curl -L -o proiel.zip https://github.com/proiel/proiel-treebank/archive/refs/heads/master.zip
curl -L -o greek-ud.zip https://github.com/UniversalDependencies/UD_Greek-GDT/archive/refs/heads/master.zip

unzip proiel.zip
unzip greek-ud.zip

mv proiel-treebank-master proiel-treebank
mv UD_Greek-GDT-master UD_Greek-GDT

CORPUS ACCESS INFORMATION

PROIEL Greek:
- Access: Free
- Format: PROIEL XML
- Download: https://github.com/proiel/proiel-treebank
- License: CC BY-NC-SA 4.0

UD Greek GDT:
- Access: Free
- Format: CoNLL-U
- Download: https://github.com/UniversalDependencies/UD_Greek-GDT
- License: CC BY-SA 4.0

YCOE:
- Access: Free
- Format: Penn .psd
- Download: https://www-users.york.ac.uk/~lang22/YCOE/
- License: Free for research

PPCME2:
- Access: License required
- Format: Penn .psd
- Source: https://www.ldc.upenn.edu/ (LDC2006T23)
- License: LDC license

PPCEME:
- Access: License required
- Format: Penn .psd
- Source: https://www.ldc.upenn.edu/ (LDC2004T07)
- License: LDC license

EVERYONE: Install Python

1. Go to: https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. Run installer
4. CRITICAL (Windows): Check "Add Python to PATH"
5. Click "Install Now"
6. Test: Open new terminal, type python --version
7. Install pandas: pip install pandas

SOFIA: Download YCOE (Old English)

1. Go to: https://www-users.york.ac.uk/~lang22/YCOE/YcoeHome.htm
2. Download YCOE corpus (free registration required)
3. Extract to: Desktop/valency_project/corpora/ycoe

ALTERNATIVE: NL can provide access to a shared Google Drive folder with YCOE

Create Extraction Script

VASSILIS: Create the Extraction Script

Create file: Desktop/valency_project/extract_verbs.py

[you create a text file with the above name --- not .txt but .py, you have to be careful that you will rename it into .py without .txt --- you will open it in Notepad: right click and open it "with Notepad". There you will copy-paste exactly the following script:]

import xml.etree.ElementTree as ET
import csv
import os

# ===========================================================================
# VALENCY PILOT PROJECT - 6 VERBS EXTRACTION
# TEAM: Eleni (Greek), Natasa (Modern), Sofia (English), Vassilis (QC)
# ===========================================================================

# 6 Target verbs (Ancient/Koine/Byzantine)
TARGET_VERBS_ANCIENT = [
    'δίδωμι', 'παρέχω',         # Give-verbs
    'λέγω', 'ἀγγέλλω',          # Say-verbs
    'φοβέομαι', 'θαυμάζω'       # Psych-verbs
]

# Modern Greek equivalents
TARGET_VERBS_MODERN = [
    'δίνω', 'παρέχω',           # Give-verbs
    'λέω', 'αγγέλλω',           # Say-verbs
    'φοβάμαι', 'θαυμάζω'        # Psych-verbs
]

def extract_case(morphology):
    """Extract case from PROIEL morphology string"""
    if morphology and len(morphology) > 7:
        case_char = morphology[7]
        case_map = {'n': 'NOM', 'g': 'GEN', 'd': 'DAT', 'a': 'ACC', 'v': 'VOC', 'l': 'LOC', '-': None}
        return case_map.get(case_char, 'UNKNOWN')
    return None

def extract_from_proiel(xml_file, output_csv, period_name, researcher):
    """Extract verbs from PROIEL XML (Ancient/Koine/Byzantine Greek)"""
    print(f"\n{'='*60}")
    print(f"Processing: {xml_file}")
    print(f"Period: {period_name} | Researcher: {researcher}")
    print(f"{'='*60}")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    results = []
    
    for sentence in root.findall('.//sentence'):
        sent_id = sentence.get('id')
        for token in sentence.findall('.//token'):
            lemma = token.get('lemma')
            if lemma in TARGET_VERBS_ANCIENT:
                verb_id = token.get('id')
                arguments = []
                
                for dep in sentence.findall('.//token'):
                    if dep.get('head-id') == verb_id:
                        arg_case = extract_case(dep.get('morphology'))
                        arguments.append({
                            'relation': dep.get('relation'),
                            'form': dep.get('form'),
                            'lemma': dep.get('lemma'),
                            'case': arg_case
                        })
                
                arg_string = '; '.join([f"{a['relation']}:{a['form']}[{a['case']}]" for a in arguments])
                
                results.append({
                    'period': period_name,
                    'researcher': researcher,
                    'sentence_id': sent_id,
                    'verb_form': token.get('form'),
                    'verb_lemma': lemma,
                    'morphology': token.get('morphology'),
                    'arguments': arg_string,
                    'source_file': os.path.basename(xml_file)
                })
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'researcher', 'sentence_id', 'verb_form', 'verb_lemma', 
                     'morphology', 'arguments', 'source_file']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Found {len(results)} instances")
    print(f"✓ Saved to: {output_csv}")
    return results

def extract_from_conllu(conllu_file, output_csv, period_name, researcher):
    """Extract verbs from CoNLL-U (Modern Greek)"""
    print(f"\n{'='*60}")
    print(f"Processing: {conllu_file}")
    print(f"Period: {period_name} | Researcher: {researcher}")
    print(f"{'='*60}")
    
    results = []
    current_sent = []
    sent_id = ""
    
    with open(conllu_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# sent_id ='):
                sent_id = line.replace('# sent_id = ', '')
            elif line.startswith('#'):
                continue
            elif not line:
                if current_sent:
                    for token in current_sent:
                        if token['lemma'] in TARGET_VERBS_MODERN:
                            args = [t for t in current_sent if t['head'] == token['id']]
                            arg_string = '; '.join([f"{a['deprel']}:{a['form']}" for a in args])
                            
                            results.append({
                                'period': period_name,
                                'researcher': researcher,
                                'sentence_id': sent_id,
                                'verb_form': token['form'],
                                'verb_lemma': token['lemma'],
                                'morphology': token['feats'],
                                'arguments': arg_string,
                                'source_file': os.path.basename(conllu_file)
                            })
                    current_sent = []
            else:
                fields = line.split('\t')
                if len(fields) >= 10 and '-' not in fields[0] and '.' not in fields[0]:
                    current_sent.append({
                        'id': fields[0],
                        'form': fields[1],
                        'lemma': fields[2],
                        'feats': fields[5],
                        'head': fields[6],
                        'deprel': fields[7]
                    })
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'researcher', 'sentence_id', 'verb_form', 'verb_lemma',
                     'morphology', 'arguments', 'source_file']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Found {len(results)} instances")
    print(f"✓ Saved to: {output_csv}")
    return results

# ===========================================================================
# MAIN EXECUTION
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("VALENCY PILOT - 6 VERBS EXTRACTION")
    print("="*60)
    
    os.makedirs('extracted_data', exist_ok=True)
    
    # ELENI's assignments
    print("\n--- ELENI'S DATA ---")
    extract_from_proiel('corpora/proiel-treebank/plato-rep.xml', 
                       'extracted_data/classical_plato.csv', 'Classical', 'Eleni')
    extract_from_proiel('corpora/proiel-treebank/herodotus.xml', 
                       'extracted_data/classical_herodotus.csv', 'Classical', 'Eleni')
    extract_from_proiel('corpora/proiel-treebank/greek-nt.xml', 
                       'extracted_data/koine_nt.csv', 'Koine', 'Eleni')
    
    # Byzantine - uncomment if Sphrantzes file available
    # extract_from_proiel('corpora/sphrantzes.xml', 
    #                    'extracted_data/byzantine_sphrantzes.csv', 'Byzantine', 'Eleni')
    
    # NATASA's assignment
    print("\n--- NATASA'S DATA ---")
    extract_from_conllu('corpora/UD_Greek-GDT/el_gdt-ud-train.conllu', 
                       'extracted_data/modern_greek.csv', 'Modern', 'Natasa')
    
    print("\n" + "="*60)
    print("✓ EXTRACTION COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print("- extracted_data/classical_plato.csv (Eleni)")
    print("- extracted_data/classical_herodotus.csv (Eleni)")
    print("- extracted_data/koine_nt.csv (Eleni)")
    print("- extracted_data/modern_greek.csv (Natasa)")
    print("\nNOTE: Sofia will extract English data separately using YCOE")

VASSILIS: Test the Script

[in a terminal of your laptop]

cd Desktop/valency_project
python extract_verbs.py

Verify files appear in extracted_data/ folder.

PROIEL DEPENDENCY RELATIONS

Core Argument Relations:
- SUB = Subject
- OBJ = Direct object
- XOBJ = Open predicative/clausal complement
- OBL = Oblique argument (typically dative/genitive/prepositional)
- XADV = Predicative complement, secondary predication
- ADV = Adverbial (may include locational/directional arguments)

Other Relevant Relations:
- AUX = Auxiliary verb
- COMP = Complementizer (ὅτι, ἵνα, etc.)
- ATR = Attribute/modifier (for prepositional phrases)

Run Extraction & Initial Exploration

EVERYONE: Run Full Extraction

[in a Terminal of your laptop]

cd Desktop/valency_project
python extract_verbs.py

Expected output:

extracted_data/
  ├── classical_plato.csv       (Eleni - ~60 tokens)
  ├── classical_herodotus.csv   (Eleni - ~50 tokens)
  ├── koine_nt.csv              (Eleni - ~80 tokens)
  └── modern_greek.csv          (Natasa - ~100 tokens)

ELENI: Verify Greek Data

- [ ] Open each CSV in Excel
- [ ] Check all 6 verbs present
- [ ] Verify argument structure looks correct
- [ ] Note any missing/problematic data

NATASA: Explore Modern Greek

- [ ] Open modern_greek.csv in Excel
- [ ] Practice identifying prepositional phrases (σε+ACC)
- [ ] Note differences from Ancient Greek patterns
- [ ] Flag any confusing cases for team meeting

SOFIA: Extract Old English

Manual extraction from YCOE:

1. Open YCOE corpus files
2. Search for target verbs: gifan, secgan, ondrædan, wundrian, giefen, cyþan
3. Create spreadsheet: english_oe.csv
4. Columns: period, researcher, verb_form, verb_lemma, arguments, source_file
5. Target: ~100 tokens total

VASSILIS: QC Check

- [ ] Verify all extraction files created
- [ ] Check token counts reasonable
- [ ] Test opening CSVs in Excel
- [ ] Prepare for STEP 1 team meeting

STEP 1 TEAM MEETING

Agenda:

- Everyone reports: data downloaded successfully?
- Review extraction results
- Discuss any problems
- NL: Train team on coding scheme

Coding scheme overview:

- Frame types: NOM-DAT-ACC, NOM-ACC, NOM-PP-ACC, etc.
- How to identify arguments from PROIEL relations
- How to code ambiguous cases

VALENCY FRAME CODING SCHEME

For each verb token, code the realized argument structure using this notation:

Basic Frame Notation:
- NOM = Nominative subject
- ACC = Accusative object
- GEN = Genitive argument
- DAT = Dative argument
- PP[prep] = Prepositional phrase (specify preposition)
- CLAUSE = Clausal complement (ὅτι, ἵνα, infinitive, etc.)
- Ø = Omitted/null argument

Frame Examples:

Ditransitive δίδωμι:
- NOM-DAT-ACC = "He gives [NOM] the book [ACC] to her [DAT]"
- NOM-PP[εἰς]-ACC = "He gives [NOM] the book [ACC] into her hands [PP]"
- NOM-ACC = "He gives [NOM] the book [ACC]" (dative omitted)

Say-verb λέγω:
- NOM-ACC-DAT = "He says [NOM] words [ACC] to them [DAT]"
- NOM-CLAUSE = "He says [NOM] that... [CLAUSE]"
- NOM-ACC-CLAUSE = "He tells [NOM] them [ACC] that... [CLAUSE]"

Psych-verb θαυμάζω:
- NOM-ACC = "He admires [NOM-experiencer] the statue [ACC-stimulus]"
- NOM-GEN = "He wonders at [NOM-experiencer] the event [GEN-stimulus]"
- NOM-ἐπί+DAT = "He marvels at [NOM-exp] the wisdom [ἐπί+DAT-stimulus]"

Deliverables by end of STEP 1:

- All corpora downloaded
- Python installed on all machines
- Extraction complete for Greek (Eleni + Natasa)
- Extraction complete for English (Sofia)
- Team trained on coding scheme

STEP 2: ANNOTATION - CLASSICAL & KOINE

ELENI: Annotate Classical Greek

Files to annotate:

- classical_plato.csv (~60 tokens)
- classical_herodotus.csv (~50 tokens)
- Total: ~110 tokens

ANNOTATION SPREADSHEET TEMPLATE

Create a spreadsheet with the following columns:

Column: corpus_id
Description: Source corpus identifier
Example: PROIEL_Plato_Rep_1.234

Column: period
Description: Time period
Example: Classical / Koine / Byzantine / Modern

Column: lemma
Description: Verb lemma
Example: δίδωμι

Column: form
Description: Inflected form
Example: δίδωσιν

Column: morphology
Description: Full morphological tag
Example: 3spia---

Column: frame_type
Description: Realized argument structure
Example: NOM-DAT-ACC

Column: subject
Description: Subject (lemma + case)
Example: ἄνθρωπος[NOM]

Column: object
Description: Direct object (lemma + case)
Example: βιβλίον[ACC]

Column: indirect_obj
Description: Indirect object/dative
Example: γυνή[DAT]

Column: oblique
Description: Other oblique arguments
Example: εἰς+οἶκος[ACC]

Column: complement
Description: Clausal complements
Example: ὅτι-clause / INF

Column: voice
Description: Active/Middle/Passive
Example: ACT / MID / PASS

Column: notes
Description: Special observations
Example: Case variation; argument omitted

Process:

1. Open CSV in Excel/Google Sheets
2. Add new columns: frame_type, subject_case, object_case, indirect_obj, notes
3. For each row:
   - Look at arguments column
   - Determine frame type (e.g., NOM-DAT-ACC)
   - Note subject case, object case, etc.
   - Add any special notes

Example:

Row: δίδωσιν | Arguments: SUB:ὁ[NOM]; OBL:παιδί[DAT]; OBJ:βιβλίον[ACC]
→ Frame type: NOM-DAT-ACC
→ Subject: ὁ[NOM]
→ Object: βιβλίον[ACC]
→ Indirect_obj: παιδί[DAT]

CODING GUIDELINES

Argument Identification:
1. Use PROIEL dependency relations as starting point
2. SUB → always code as subject
3. OBJ → code as direct object
4. OBL → examine case/preposition to classify (indirect object vs. other oblique)
5. XOBJ / COMP → code as clausal complement

Ambiguous Cases:
- Dative arguments: Distinguish indirect objects (recipient/beneficiary) from other datives (location, instrument)
- Prepositional phrases: Code preposition explicitly; distinguish arguments from adjuncts
- Middle voice: Note whether middle is reflexive, reciprocal, or "true middle" (subject-affected)

Omitted Arguments:
- Mark expected but unrealized arguments as Ø
- Note whether omission is anaphoric (discourse-given) or generic/indefinite

Deliverable: classical_annotated.xlsx (110 tokens coded as soon as possible)

ELENI: Create Coding Manual

While annotating, document decisions:

File: coding_manual.md

Contents:

- Frame type definitions
- Examples of each frame
- How to handle:
  - Omitted arguments
  - Prepositional phrases
  - Clausal complements
  - Middle voice
  - Ambiguous cases

Share with team as soon as possible

NATASA: Start Modern Greek Annotation

File: modern_greek.csv (~100 tokens)

Focus areas:

1. Identify σε+ACC replacing old dative
2. Note prepositional marking vs. case marking
3. Compare with Classical patterns (ask Eleni for help)

Deliverable: 50% complete as soon as possible (50 tokens)

SOFIA: Annotate Old English

File: english_oe.csv (~100 tokens)

Process:

1. Identify subject, object, indirect object
2. Note case marking (if visible)
3. Compare give-verbs vs. say-verbs vs. psych-verbs
4. Document any interesting patterns

Deliverable: 50% complete as soon as possible (50 tokens)

VASSILIS: Quality Control

Tasks:

1. Review Eleni's first 20 coded tokens
2. Code same 20 tokens independently
3. Calculate inter-coder agreement
4. Discuss differences with Eleni
5. Update coding manual based on issues found

Deliverable: QC report noting agreement rate

STEP 2 TEAM MEETING

Agenda:

- Eleni presents Classical findings so far
- Natasa discusses Modern Greek challenges
- Sofia shares Old English patterns
- Vassilis reports on QC results
- NL: Resolve any ambiguous cases

Deliverables by end of STEP 2:

- Classical Greek 100% annotated (Eleni)
- Coding manual v1.0 (Eleni)
- Modern Greek 50% annotated (Natasa)
- Old English 50% annotated (Sofia)
- QC report (Vassilis)

STEP 3: COMPLETE ANNOTATION & ANALYSIS

ELENI: Annotate Koine & Byzantine

Files:

- koine_nt.csv (~80 tokens)
- byzantine_sphrantzes.csv (~50 tokens, if available)
- Total: ~130 tokens

Deliverable: All Greek periods annotated as soon as possible

NATASA: Complete Modern Greek

File: modern_greek.csv (remaining 50 tokens)

Additional tasks:

- Create frequency table: How many of each frame type?
- Create simple bar chart showing frame distribution
- Write 1-page summary of Modern Greek findings

Deliverable: Modern Greek 100% complete + frequency table + summary

SOFIA: Complete Old English

File: english_oe.csv (remaining 50 tokens)

Additional tasks:

- Create frequency table for English
- Compare with Greek patterns (with Eleni's help)
- Write 1-page summary of English findings

Deliverable: Old English 100% complete + frequency table + summary

VASSILIS: Statistical Analysis

Tasks:

1. Collect all annotated data
2. Create master frequency table:
   - Rows: Each verb
   - Columns: Frame types
   - Sub-columns: Classical, Koine, Byzantine, Modern
3. Run chi-square tests:
   - Is frame distribution different across periods?
   - Which changes are statistically significant?
4. Create visualizations:
   - Stacked bar charts (frame types per period)
   - Line graphs (dative usage over time)

Deliverable: Statistical analysis report (2 pages)

ELENI: Merge All Data

Tasks:

1. Combine all Greek annotated files into one master spreadsheet
2. Verify consistency across periods
3. Generate summary statistics:
   - Total tokens per period
   - Total tokens per verb
   - Frame type frequencies

Deliverable: master_greek_dataset.xlsx

STEP 3 TEAM MEETING

Agenda:

- Verify all annotation complete
- Review Vassilis's statistical results
- Discuss key findings
- NL: Assign final report sections

Report section assignments:

- Introduction & Methods: NL
- Classical Greek findings: Eleni (1 page)
- Koine Greek findings: Eleni (1 page)
- Byzantine Greek findings: Eleni (1 page)
- Modern Greek findings: Natasa (1 page)
- English comparative: Sofia (1 page)
- Statistical analysis: Vassilis (1 page)
- Discussion: Vassilis + NL (1 page)
- Conclusion: NL (0.5 pages)

Deliverables by end of STEP 3:

- All annotation 100% complete
- Master Greek dataset (Eleni)
- Statistical analysis (Vassilis)
- Frequency tables (Everyone)
- Individual summaries (Everyone)

STEP 4: WRITE-UP & FINAL REPORT

Individual Writing

ELENI: Write Greek Sections

- Classical Greek findings (1 page)
- Koine Greek findings (1 page)
- Byzantine Greek findings (1 page)
- Focus on: diachronic changes, dative loss, prepositional increase

NATASA: Write Modern Greek Section

- Modern Greek findings (1 page)
- Focus on: complete loss of dative, prepositional marking dominant

SOFIA: Write English Section

- English comparative data (1 page)
- Focus on: parallel changes in Greek vs. English

VASSILIS: Write Analysis & Discussion

- Statistical analysis results (1 page)
- Discussion with theoretical implications (1 page)
- Focus on: grammaticalization pathways, case system simplification

NL: Write Frame Sections

- Introduction (0.5 pages)
- Methods (1 page)
- Conclusion (0.5 pages)

Synthesis & Revision

NL: Combine All Sections

Tasks:

1. Merge all individual sections
2. Edit for consistency
3. Add transitions between sections
4. Create unified reference list
5. Format final document

Target: 8-10 page preliminary report

ELENI: Proofread

- Read entire draft
- Check for errors
- Verify all data cited correctly

VASSILIS: Create Final Visualizations

- Polish all charts/graphs
- Ensure publication quality
- Add figure captions

EVERYONE: Final Review

- Read full draft
- Suggest revisions
- Approve final version

FINAL DELIVERY

NL: Final Polish & Submit

Deliverables:

1. Preliminary Findings Report (8-10 pages)
   - Introduction
   - Methods
   - Results (Greek + English)
   - Statistical Analysis
   - Discussion
   - Conclusion
   - References

2. Dataset Package:
   - Master annotated spreadsheet
   - Frequency tables
   - Coding manual
   - Raw extraction files

3. Visualizations:
   - 3-5 publication-quality figures

STEP 4 TEAM MEETING

Final presentation:

- Each person presents their findings (5 min each)
- Discuss next steps
- Plan for publication/conference abstract
- Celebrate completion!

EXPECTED FINDINGS

Hypothesis 1: Dative Loss

- Classical: 60-70% of ditransitives use DAT
- Koine: 40-50% use DAT
- Byzantine: 10-20% use DAT
- Modern: 0% use DAT (all prepositional)

Hypothesis 2: Prepositional Rise

- Classical: 10-15% use PP (εἰς, πρός)
- Koine: 30-40% use PP
- Byzantine: 60-70% use PP
- Modern: 100% use PP (σε+ACC)

Hypothesis 3: Voice Merger

- Classical: Clear ACT/MID/PASS distinction
- Koine: MID/PASS beginning to merge
- Byzantine: MID/PASS largely merged
- Modern: ACT vs. NON-ACT only

PROIEL MORPHOLOGY TAG REFERENCE

PROIEL morphological tags use a 9-character string:

Position-by-position breakdown:
1. POS (Part of Speech): V=Verb, N=Noun, A=Adjective, etc.
2. Person: 1/2/3/-
3. Number: s=singular, p=plural, d=dual, -
4. Tense: p=present, i=imperfect, r=perfect, l=pluperfect, t=future, a=aorist, -
5. Mood: i=indicative, s=subjunctive, o=optative, m=imperative, n=infinitive, p=participle, -
6. Voice: a=active, p=passive, m=middle, -
7. Gender: m=masculine, f=feminine, n=neuter, - (for participles/nouns)
8. Case: n=nominative, g=genitive, d=dative, a=accusative, v=vocative, l=locative, -
9. Degree: p=positive, c=comparative, s=superlative, - (for adjectives)

Example: 3spia--- = 3rd person, singular, present, indicative, active
