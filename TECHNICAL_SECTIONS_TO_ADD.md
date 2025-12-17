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

REFERENCES

Greek Argument Structure Diachrony:
- Luraghi, S. (2003). On the Meaning of Prepositions and Cases. Amsterdam: Benjamins.
- Conti, L. & Luraghi, S. (2014). "The Ancient Greek partitive genitive in typological perspective." Acta Linguistica Hafniensia 46.2.
- Horrocks, G. (2010). Greek: A History of the Language and its Speakers. 2nd ed. Wiley-Blackwell.

Valency Theory:
- Herbst, T. & Schüller, S. (2008). Introduction to Syntactic Analysis. Göttingen: Vandenhoeck & Ruprecht.
- Malchukov, A. & Comrie, B. (eds.) (2015). Valency Classes in the World's Languages. Berlin: De Gruyter.

Case System Change:
- Blake, B. (2001). Case. 2nd ed. Cambridge: CUP.
- Bauer, B. (2000). Archaic Syntax in Indo-European. Berlin: Mouton de Gruyter.

Corpora:
- PROIEL: https://proiel.github.io/
- Universal Dependencies: https://universaldependencies.org/
- Penn Parsed Corpora: https://www.ling.upenn.edu/hist-corpora/
