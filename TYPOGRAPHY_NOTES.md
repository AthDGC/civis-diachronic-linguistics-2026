# Typography Choices

## Fonts Used

This website uses professional academic fonts with emphasis on Greek typography heritage:

### Primary Font: Roboto
- **Type:** Sans-serif
- **Usage:** Body text, navigation, interface elements
- **Designer:** Christian Robertson (Google)
- **License:** Apache License 2.0 (free and open-source)
- **Characteristics:** Clean, modern, professional, excellent readability
- **Greek Support:** Full Greek character set including polytonic Greek

### Heading & Accent Font: Katsoulidis
- **Type:** Serif (Greek academic typeface)
- **Usage:** All headings, titles, emphasis, academic content
- **Designer:** Takis Katsoulidis
- **Foundry:** Fonts.GR (Greek Digital Type Library)
- **License:** Commercial font (used via CDN)
- **Characteristics:** Evolution of Didot where curves dominate straight lines, enhanced x-height for excellent legibility, specifically designed for Greek typography
- **Greek Support:** Designed with Greek characters as primary focus, full Latin support
- **Background:** Created 1986-1989 as part of university research programs in Greece, represents modern Greek typographic excellence

## Why Katsoulidis?

Katsoulidis is the perfect choice for this University of Athens programme because:

1. **Greek Heritage:** Designed by renowned Greek type designer Takis Katsoulidis, specifically for Greek academic publishing
2. **University Research Origins:** Created as part of research programs in Greek universities (TEI), making it ideal for academic contexts
3. **Modern Evolution:** An evolution of Didot typefaces with improved readability through increased x-height
4. **Bilingual Excellence:** Designed with equal attention to both Greek and Latin alphabets
5. **Academic Prestige:** Used in Greek academic and cultural publications

## Design Rationale

The typography choices reflect:

1. **Greek Academic Identity:** Katsoulidis represents the highest standard of modern Greek typography
2. **University of Athens Connection:** Font designed in Greek university context, perfect for NKUA
3. **Professional Readability:** Roboto ensures excellent screen legibility for international audience
4. **Cultural Authenticity:** Using a font by Greek Font Society (Fonts.GR) honors Greek typographic tradition
5. **Didot Legacy:** Katsoulidis builds on the Didot tradition which has deep roots in Greek printing history

## About the Designer

**Takis Katsoulidis** is a renowned Greek painter-engraver and type designer who has made significant contributions to Greek typography. His work includes:
- Katsoulidis font family (1986-1989)
- GFS Artemisia (with George D. Matthiopoulos)
- Numerous typefaces for Greek Font Society
- Author of "To Schedio tou Grammatos" (The Design of the Letter) - a seminal work in Greek typography

His designs are known for their sensitivity to the unique characteristics of Greek letters (ζ, ξ, σ, ς, φ, ω, ψ) and for breathing life into letterforms.

## Font Hierarchy

- **Hero Titles:** Katsoulidis, 2.5-4rem, bold
- **Section Headings:** Katsoulidis, 1.75-2.5rem, bold  
- **Body Text:** Roboto, 1rem, regular
- **Navigation:** Roboto, 0.875-1rem, medium
- **Special Emphasis:** Katsoulidis for Greek academic context

## Technical Implementation

Fonts are loaded via CDN:
```html
<!-- Roboto for body text -->
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- Katsoulidis for headings -->
<link href="https://db.onlinewebfonts.com/c/d34d370b9537835d2b01df73f3394c92?family=Katsoulidis+W01+Regular" rel="stylesheet" type="text/css">
```

CSS Variables:
```css
--font-primary: 'Roboto', sans-serif;
--font-heading: 'Katsoulidis W01 Regular', Georgia, serif;
--font-accent: 'Katsoulidis W01 Regular', Georgia, serif;
```

## References

- Katsoulidis Font Family: https://www.fonts.gr/fonts/katsoulidis
- Takis Katsoulidis: http://katsoulidistakis.gr/
- Greek Font Society (Fonts.GR): https://www.fonts.gr/
- MyFonts Katsoulidis: https://www.myfonts.com/collections/katsoulidis-font-fonts-gr
