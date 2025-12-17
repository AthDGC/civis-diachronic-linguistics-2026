# DIACHRONIC VALENCY LEXICON PILOT STUDY
## Complete Implementation Guide with Researcher Assignments

**Timeline:** 4 weeks (less than 1 month)  
**Team:** NL (PI), Eleni, Natasa, Sofia, Vassilis  
**Verbs:** 6 verbs (reduced from 12 for time constraints)  
**Periods:** Classical → Koine → Byzantine → Modern Greek + Old English  

---

## 🎯 TEAM ASSIGNMENTS AT A GLANCE

| Researcher | Primary Responsibility | Time/Week | Key Deliverables |
|------------|------------------------|-----------|------------------|
| **Eleni** | Classical + Koine + Byzantine Greek | 10-12 hrs | 3 annotated CSV files (400 tokens) |
| **Natasa** | Modern Greek | 6-8 hrs | 1 annotated CSV file (100 tokens) |
| **Sofia** | Old English | 6-8 hrs | 1 annotated CSV file (100 tokens) |
| **Vassilis** | Quality control + Statistics | 4-5 hrs | QC report + statistical analysis |
| **NL (PI)** | Coordination + Final report | Variable | 3-page preliminary findings |

**Total tokens to annotate:** 600-700 tokens  
**Protection for Eleni:** If workload >12 hrs/week → Vassilis takes Byzantine immediately

---

## 📋 THE 6 TARGET VERBS (Reduced List)

### **Give-verbs (2):**
1. **δίδωμι** (Ancient) → **δίνω** (Modern) | English: *gifan* → *give*
2. **παρέχω** (Ancient) → **παρέχω** (Modern, formal) | English: *giefen* → *provide*

### **Say-verbs (2):**
3. **λέγω** (Ancient) → **λέω** (Modern) | English: *secgan* → *say*
4. **ἀγγέλλω** (Ancient) → **αγγέλλω** (Modern, formal) | English: *cyþan* → *tell*

### **Psych-verbs (2):**
5. **φοβέομαι** (Ancient) → **φοβάμαι** (Modern) | English: *ondrædan* → *fear*
6. **θαυμάζω** (Ancient) → **θαυμάζω** (Modern) | English: *wundrian* → *wonder*

**NOTE:** φημί dropped (obsolete in Modern Greek). Motion verbs dropped for time constraints.

---

## 📁 SETUP: CREATE YOUR PROJECT FOLDER

**Everyone does this first!** Takes 10 minutes.

### For Windows:
1. Go to Desktop
2. Right-click → New → Folder
3. Name it: `valency_project`
4. Open Command Prompt (Windows key + R, type `cmd`, press Enter)
5. Type: `cd Desktop\valency_project`

### For Mac:
1. Go to Desktop
2. Right-click → New Folder
3. Name it: `valency_project`
4. Open Terminal (Command + Space, type `terminal`)
5. Type: `cd Desktop/valency_project`

**Your folder path:** `Desktop/valency_project`

---

## 📥 STEP 1: SETUP & DATA EXTRACTION

### DAY 1-2: Download Corpora & Install Python

#### **EVERYONE: Download Greek Corpora**

**Windows (Command Prompt):**
```cmd
cd Desktop\valency_project
mkdir corpora
cd corpora

curl -L -o proiel.zip https://github.com/proiel/proiel-treebank/archive/refs/heads/master.zip
curl -L -o greek-ud.zip https://github.com/UniversalDependencies/UD_Greek-GDT/archive/refs/heads/master.zip

tar -xf proiel.zip
tar -xf greek-ud.zip

move proiel-treebank-master proiel-treebank
move UD_Greek-GDT-master UD_Greek-GDT
```

**Mac (Terminal):**
```bash
cd Desktop/valency_project
mkdir corpora
cd corpora

curl -L -o proiel.zip https://github.com/proiel/proiel-treebank/archive/refs/heads/master.zip
curl -L -o greek-ud.zip https://github.com/UniversalDependencies/UD_Greek-GDT/archive/refs/heads/master.zip

unzip proiel.zip
unzip greek-ud.zip

mv proiel-treebank-master proiel-treebank
mv UD_Greek-GDT-master UD_Greek-GDT
```

#### **EVERYONE: Install Python**

1. Go to: https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. Run installer
4. **⚠️ CRITICAL (Windows):** Check "Add Python to PATH"
5. Click "Install Now"
6. Test: Open new terminal, type `python --version`
7. Install pandas: `pip install pandas`

---

#### **SOFIA: Download YCOE (Old English)**

1. Go to: https://www-users.york.ac.uk/~lang22/YCOE/YcoeHome.htm
2. Download YCOE corpus (free registration required)
3. Extract to: `Desktop/valency_project/corpora/ycoe`

**ALTERNATIVE:** NL can provide access to a shared Google Drive folder with YCOE

---

### DAY 3: Create Extraction Script

#### **VASSILIS: Create the Extraction Script** (1 hour)

Create file: `Desktop/valency_project/extract_verbs.py`

```python
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
```

#### **VASSILIS: Test the Script** (30 minutes)

```bash
cd Desktop/valency_project
python extract_verbs.py
```

Verify files appear in `extracted_data/` folder.

---

### DAY 4-7: Run Extraction & Initial Exploration

#### **EVERYONE: Run Full Extraction**

```bash
cd Desktop/valency_project
python extract_verbs.py
```

**Expected output:**
```
extracted_data/
  ├── classical_plato.csv       (Eleni - ~60 tokens)
  ├── classical_herodotus.csv   (Eleni - ~50 tokens)
  ├── koine_nt.csv              (Eleni - ~80 tokens)
  └── modern_greek.csv          (Natasa - ~100 tokens)
```

#### **ELENI: Verify Greek Data** (2 hours)
- [ ] Open each CSV in Excel
- [ ] Check all 6 verbs present
- [ ] Verify argument structure looks correct
- [ ] Note any missing/problematic data

#### **NATASA: Explore Modern Greek** (2 hours)
- [ ] Open modern_greek.csv in Excel
- [ ] Practice identifying prepositional phrases (σε+ACC)
- [ ] Note differences from Ancient Greek patterns
- [ ] Flag any confusing cases for team meeting

#### **SOFIA: Extract Old English** (4 hours)

**Manual extraction from YCOE:**
1. Open YCOE corpus files
2. Search for target verbs: *gifan*, *secgan*, *ondrædan*, *wundrian*, *giefen*, *cyþan*
3. Create spreadsheet: `english_oe.csv`
4. Columns: period, researcher, verb_form, verb_lemma, arguments, source_file
5. Target: ~100 tokens total

**Or if using CorpusSearch:**
Create query files for each verb and run searches

#### **VASSILIS: QC Check** (1 hour)
- [ ] Verify all extraction files created
- [ ] Check token counts reasonable
- [ ] Test opening CSVs in Excel
- [ ] Prepare for STEP 1 team meeting

---

### **STEP 1 TEAM MEETING** (1 hour - Friday)

**Agenda:**
- Everyone reports: data downloaded successfully?
- Review extraction results
- Discuss any problems
- **NL:** Train team on coding scheme

**Coding scheme overview:**
- Frame types: NOM-DAT-ACC, NOM-ACC, NOM-PP-ACC, etc.
- How to identify arguments from PROIEL relations
- How to code ambiguous cases

**Deliverables by end of STEP 1:**
- ✅ All corpora downloaded
- ✅ Python installed on all machines
- ✅ Extraction complete for Greek (Eleni + Natasa)
- ✅ Extraction complete for English (Sofia)
- ✅ Team trained on coding scheme

---

## 📝 STEP 2: ANNOTATION - CLASSICAL & KOINE

### **ELENI: Annotate Classical Greek** (10 hours)

**Files to annotate:**
- `classical_plato.csv` (~60 tokens)
- `classical_herodotus.csv` (~50 tokens)
- **Total: ~110 tokens**

**Process:**
1. Open CSV in Excel/Google Sheets
2. Add new columns: `frame_type`, `subject_case`, `object_case`, `indirect_obj`, `notes`
3. For each row:
   - Look at `arguments` column
   - Determine frame type (e.g., NOM-DAT-ACC)
   - Note subject case, object case, etc.
   - Add any special notes

**Example:**
```
Row: δίδωσιν | Arguments: SUB:ὁ[NOM]; OBL:παιδί[DAT]; OBJ:βιβλίον[ACC]
→ Frame type: NOM-DAT-ACC
→ Subject: ὁ[NOM]
→ Object: βιβλίον[ACC]
→ Indirect_obj: παιδί[DAT]
```

**Deliverable:** `classical_annotated.xlsx` (110 tokens coded by Friday)

---

### **ELENI: Create Coding Manual** (2 hours)

While annotating, document decisions:

**File:** `coding_manual.md`

**Contents:**
- Frame type definitions
- Examples of each frame
- How to handle:
  - Omitted arguments
  - Prepositional phrases
  - Clausal complements
  - Middle voice
  - Ambiguous cases

**Share with team by Wednesday**

---

### **NATASA: Start Modern Greek Annotation** (6 hours)

**File:** `modern_greek.csv` (~100 tokens)

**Focus areas:**
1. Identify σε+ACC replacing old dative
2. Note prepositional marking vs. case marking
3. Compare with Classical patterns (ask Eleni for help)

**Deliverable:** 50% complete by Friday (50 tokens)

---

### **SOFIA: Annotate Old English** (6 hours)

**File:** `english_oe.csv` (~100 tokens)

**Process:**
1. Identify subject, object, indirect object
2. Note case marking (if visible)
3. Compare give-verbs vs. say-verbs vs. psych-verbs
4. Document any interesting patterns

**Deliverable:** 50% complete by Friday (50 tokens)

---

### **VASSILIS: Quality Control** (3 hours)

**Tasks:**
1. Review Eleni's first 20 coded tokens (Tuesday)
2. Code same 20 tokens independently
3. Calculate inter-coder agreement
4. Discuss differences with Eleni
5. Update coding manual based on issues found

**Deliverable:** QC report noting agreement rate

---

### **STEP 2 TEAM MEETING** (1 hour - Friday)

**Agenda:**
- Eleni presents Classical findings so far
- Natasa discusses Modern Greek challenges
- Sofia shares Old English patterns
- Vassilis reports on QC results
- **NL:** Resolve any ambiguous cases

**Deliverables by end of STEP 2:**
- ✅ Classical Greek 100% annotated (Eleni)
- ✅ Coding manual v1.0 (Eleni)
- ✅ Modern Greek 50% annotated (Natasa)
- ✅ Old English 50% annotated (Sofia)
- ✅ QC report (Vassilis)

---

## 📊 STEP 3: COMPLETE ANNOTATION & ANALYSIS

### **ELENI: Annotate Koine & Byzantine** (10 hours)

**Files:**
- `koine_nt.csv` (~80 tokens)
- `byzantine_sphrantzes.csv` (~50 tokens, if available)
- **Total: ~130 tokens**

**Deliverable:** All Greek periods annotated by Wednesday

---

### **NATASA: Complete Modern Greek** (6 hours)

**File:** `modern_greek.csv` (remaining 50 tokens)

**Additional tasks:**
- Create frequency table: How many of each frame type?
- Create simple bar chart showing frame distribution
- Write 1-page summary of Modern Greek findings

**Deliverable:** Modern Greek 100% complete + frequency table + summary

---

### **SOFIA: Complete Old English** (6 hours)

**File:** `english_oe.csv` (remaining 50 tokens)

**Additional tasks:**
- Create frequency table for English
- Compare with Greek patterns (with Eleni's help)
- Write 1-page summary of English findings

**Deliverable:** Old English 100% complete + frequency table + summary

---

### **VASSILIS: Statistical Analysis** (4 hours)

**Tasks:**
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

**Deliverable:** Statistical analysis report (2 pages)

---

### **ELENI: Merge All Data** (2 hours)

**Tasks:**
1. Combine all Greek annotated files into one master spreadsheet
2. Verify consistency across periods
3. Generate summary statistics:
   - Total tokens per period
   - Total tokens per verb
   - Frame type frequencies

**Deliverable:** `master_greek_dataset.xlsx`

---

### **STEP 3 TEAM MEETING** (1 hour - Friday)

**Agenda:**
- Verify all annotation complete
- Review Vassilis's statistical results
- Discuss key findings
- **NL:** Assign final report sections

**Report section assignments:**
- Introduction & Methods: NL
- Classical Greek findings: Eleni (1 page)
- Koine Greek findings: Eleni (1 page)
- Byzantine Greek findings: Eleni (1 page)
- Modern Greek findings: Natasa (1 page)
- English comparative: Sofia (1 page)
- Statistical analysis: Vassilis (1 page)
- Discussion: Vassilis + NL (1 page)
- Conclusion: NL (0.5 pages)

**Deliverables by end of STEP 3:**
- ✅ All annotation 100% complete
- ✅ Master Greek dataset (Eleni)
- ✅ Statistical analysis (Vassilis)
- ✅ Frequency tables (Everyone)
- ✅ Individual summaries (Everyone)

---

## ✍️ STEP 4: WRITE-UP & FINAL REPORT

### **DAYS 22-24: Individual Writing**

#### **ELENI: Write Greek Sections** (8 hours)
- Classical Greek findings (1 page)
- Koine Greek findings (1 page)
- Byzantine Greek findings (1 page)
- Focus on: diachronic changes, dative loss, prepositional increase

#### **NATASA: Write Modern Greek Section** (4 hours)
- Modern Greek findings (1 page)
- Focus on: complete loss of dative, prepositional marking dominant

#### **SOFIA: Write English Section** (4 hours)
- English comparative data (1 page)
- Focus on: parallel changes in Greek vs. English

#### **VASSILIS: Write Analysis & Discussion** (4 hours)
- Statistical analysis results (1 page)
- Discussion with theoretical implications (1 page)
- Focus on: grammaticalization pathways, case system simplification

#### **NIKOS: Write Frame Sections** (4 hours)
- Introduction (0.5 pages)
- Methods (1 page)
- Conclusion (0.5 pages)

---

### **DAYS 25-27: Synthesis & Revision**

#### **NIKOS: Combine All Sections** (6 hours)

**Tasks:**
1. Merge all individual sections
2. Edit for consistency
3. Add transitions between sections
4. Create unified reference list
5. Format final document

**Target:** 8-10 page preliminary report

#### **ELENI: Proofread** (2 hours)
- Read entire draft
- Check for errors
- Verify all data cited correctly

#### **VASSILIS: Create Final Visualizations** (2 hours)
- Polish all charts/graphs
- Ensure publication quality
- Add figure captions

#### **EVERYONE: Final Review** (1 hour each)
- Read full draft
- Suggest revisions
- Approve final version

---

### **DAY 28: FINAL DELIVERY**

#### **NIKOS: Final Polish & Submit** (2 hours)

**Deliverables:**
1. **Preliminary Findings Report** (8-10 pages)
   - Introduction
   - Methods
   - Results (Greek + English)
   - Statistical Analysis
   - Discussion
   - Conclusion
   - References

2. **Dataset Package:**
   - Master annotated spreadsheet
   - Frequency tables
   - Coding manual
   - Raw extraction files

3. **Visualizations:**
   - 3-5 publication-quality figures

---

### **STEP 4 TEAM MEETING** (1 hour - Friday)

**Final presentation:**
- Each person presents their findings (5 min each)
- Discuss next steps
- Plan for publication/conference abstract
- Celebrate completion!

---

## 📊 DELIVERABLES CHECKLIST

### **STEP 1:**
- [ ] Corpora downloaded (All)
- [ ] Python installed (All)
- [ ] Extraction scripts working (Vassilis)
- [ ] All data extracted (Eleni, Natasa, Sofia)

### **STEP 2:**
- [ ] Classical Greek annotated (Eleni)
- [ ] Coding manual v1.0 (Eleni)
- [ ] Modern Greek 50% (Natasa)
- [ ] Old English 50% (Sofia)
- [ ] QC report (Vassilis)

### **STEP 3:**
- [ ] Koine + Byzantine annotated (Eleni)
- [ ] Modern Greek 100% (Natasa)
- [ ] Old English 100% (Sofia)
- [ ] Master dataset (Eleni)
- [ ] Statistical analysis (Vassilis)

### **STEP 4:**
- [ ] All report sections written (Everyone)
- [ ] Final report synthesized (NL)
- [ ] Final proofreading (Eleni)
- [ ] Visualizations complete (Vassilis)
- [ ] Final delivery (NL)

---

## 🛠️ TOOLS & RESOURCES

### **Required Software:**
- **Python 3.11+** (with pandas library)
- **Excel or Google Sheets** (for annotation)
- **Text editor** (Notepad++, VS Code, or built-in)

### **Corpora:**
- **PROIEL:** https://github.com/proiel/proiel-treebank
- **UD Greek:** https://github.com/UniversalDependencies/UD_Greek-GDT
- **YCOE:** https://www-users.york.ac.uk/~lang22/YCOE/ (or NL's Google Drive)

### **Documentation:**
- **PROIEL guidelines:** https://proiel.github.io/
- **UD guidelines:** https://universaldependencies.org/
- **Coding manual:** Created by Eleni in STEP 2

---

## 🆘 EMERGENCY CONTACTS

### **Technical Issues:**
- **Python/installation:** Vassilis
- **PROIEL XML format:** Eleni or NL
- **Modern Greek corpus:** Natasa or NL
- **English corpus:** Sofia or NL

### **Annotation Questions:**
- **Ambiguous cases:** NL (final arbiter)
- **Frame type confusion:** Eleni (after checking coding manual)
- **Modern Greek specifics:** Natasa (with Eleni backup)

### **If Someone Falls Behind:**
- **Eleni overwhelmed:** Vassilis takes Byzantine immediately
- **Natasa struggling:** Eleni provides 1-hour training session
- **Sofia blocked:** Reduce English to 75 tokens
- **Anyone stuck:** Contact NL ASAP, don't wait!

---

## 📈 EXPECTED FINDINGS

### **Hypothesis 1: Dative Loss**
- Classical: 60-70% of ditransitives use DAT
- Koine: 40-50% use DAT
- Byzantine: 10-20% use DAT
- Modern: 0% use DAT (all prepositional)

### **Hypothesis 2: Prepositional Rise**
- Classical: 10-15% use PP (εἰς, πρός)
- Koine: 30-40% use PP
- Byzantine: 60-70% use PP
- Modern: 100% use PP (σε+ACC)

### **Hypothesis 3: Voice Merger**
- Classical: Clear ACT/MID/PASS distinction
- Koine: MID/PASS beginning to merge
- Byzantine: MID/PASS largely merged
- Modern: ACT vs. NON-ACT only

---

## 🎯 SUCCESS CRITERIA

**Minimum viable product:**
- 600-700 annotated tokens
- All 4 Greek periods covered
- English comparative data
- Statistical significance demonstrated
- 8-10 page preliminary report

**Stretch goals (if time permits):**
- Conference abstract draft
- Additional visualizations
- Middle English data (50 tokens)
- Publication outline

---

## 💡 KEY PRINCIPLES

1. **"Good enough" > "Perfect"** - Don't get stuck on edge cases
2. **Communicate early** - Problems get worse if hidden
3. **Protect Eleni** - She has the most work; redistribute if needed
4. **Everyone contributes** - No one person does everything
5. **Meet deadlines** - This is a 4-week sprint, not a marathon
6. **Support each other** - Ask for help when needed
7. **Celebrate small wins** - Completed tasks deserve recognition!

---

## ✅ FINAL CHECKLIST

Before final submission, verify:
- [ ] All 600-700 tokens annotated
- [ ] Inter-coder reliability >80%
- [ ] Statistical tests run correctly
- [ ] All figures have captions
- [ ] All citations formatted correctly
- [ ] Report proofread by at least 2 people
- [ ] Dataset files organized and labeled
- [ ] Coding manual complete
- [ ] Team authorship order agreed
- [ ] NL approves final version

---

**END OF GUIDE**

*For questions or emergencies, contact NL immediately*

*Document version: 1.0 | Created: December 2024*
