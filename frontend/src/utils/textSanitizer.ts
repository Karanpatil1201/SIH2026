/**
 * Sanitizes raw LaTeX mathematical notation, arrow codes, and residual markup
 * into clean, standard Unicode symbols.
 *
 * Examples:
 *   "$\rightarrow$" -> "→"
 *   "$\leftarrow$"  -> "←"
 *   "$\pm$"         -> "±"
 *   "^\circ"        -> "°"
 *   "$\text{Goa} \rightarrow \text{Mumbai}$" -> "Goa → Mumbai"
 */
export const cleanLatexSymbols = (text: string): string => {
  if (!text) return '';
  let out = text;

  // 1. Unwrap \text{...} wrappers
  out = out.replace(/\\text\{([^}]*)\}/g, '$1');

  // 2. Multi-token dollar expressions containing arrows or math (e.g. $A \rightarrow B$)
  out = out.replace(/\$([^$]+)\$/g, (match, inner) => {
    if (/\\(?:rightarrow|to|leftarrow|leftrightarrow|Rightarrow|Leftarrow|pm|times|approx|le|ge|degree)|[→←↔⇒⇐⇔]/.test(inner)) {
      return ' ' + inner + ' ';
    }
    return match;
  });

  // 3. Arrow replacements (dollar-wrapped or bare)
  out = out
    .replace(/\$?\s*\\(?:rightarrow|longrightarrow|to)\s*\$?|\$\s*->\s*\$/gi, ' → ')
    .replace(/\$?\s*\\(?:leftarrow|longleftarrow|gets)\s*\$?|\$\s*<-\s*\$/gi, ' ← ')
    .replace(/\$?\s*\\(?:leftrightarrow|longleftrightarrow)\s*\$?|\$\s*<->\s*\$/gi, ' ↔ ')
    .replace(/\$?\s*\\(?:Rightarrow|Longrightarrow|implies)\s*\$?|\$\s*=>\s*\$/gi, ' ⇒ ')
    .replace(/\$?\s*\\(?:Leftarrow|Longleftarrow)\s*\$?|\$\s*<=\s*\$/gi, ' ⇐ ')
    .replace(/\$?\s*\\(?:Leftrightarrow|Longleftrightarrow|iff)\s*\$?|\$\s*<=>\s*\$/gi, ' ⇔ ');

  // 4. Common mathematical & scientific notations
  out = out
    .replace(/\$?\s*\\(?:pm|plusminus)\s*\$?|\$\s*\+-\s*\$/gi, ' ± ')
    .replace(/\$?\s*\\times\s*\$?|\$\s*\*\s*\$/gi, ' × ')
    .replace(/\$?\s*\\div\s*\$/gi, ' ÷ ')
    .replace(/\$?\s*\\(?:approx|sim)\s*\$?|\$\s*~\s*\$/gi, ' ≈ ')
    .replace(/\$?\s*\\(?:neq|ne)\s*\$?|\$\s*!=\s*\$/gi, ' ≠ ')
    .replace(/\$?\s*\\(?:leq|le)\s*\$?|\$\s*<=\s*\$/gi, ' ≤ ')
    .replace(/\$?\s*\\(?:geq|ge)\s*\$?|\$\s*>=\s*\$/gi, ' ≥ ')
    .replace(/\$?\s*\\(?:degree|deg)\s*\$?|\^\{?\\circ\}?/gi, '°')
    .replace(/\$?\s*\\cdot\s*\$?|\$\s*\.\s*\$/gi, ' · ')
    .replace(/\$?\s*\\bullet\s*\$?|\$\s*\\\*\s*\$/gi, ' • ')
    .replace(/\$?\s*\\(?:dots|ldots)\s*\$?|\$\s*\.\.\.\s*\$/gi, '…')
    .replace(/\$?\s*\\infty\s*\$?|\$\s*oo\s*\$/gi, ' ∞ ')
    .replace(/\$?\s*\\(?:checkmark|cmark)\s*\$?/gi, '✓')
    .replace(/\$?\s*\\Delta\s*\$?|\$\s*Delta\s*\$/gi, 'Δ')
    .replace(/\$?\s*\\(?:mu|micro)\s*\$?|\$\s*mu\s*\$/gi, 'µ');

  // 5. Clean any residual dollar signs around arrows/symbols: e.g. $ → $ or $28°C$
  out = out.replace(/\$\s*([→←↔⇒⇐⇔±×÷≈≠≤≥°·•…∞✓Δµ])\s*\$/g, ' $1 ');
  out = out.replace(/\$\s*([^$]*[→←↔⇒⇐⇔±×÷≈≠≤≥°✓Δµ][^$]*)\s*\$/g, ' $1 ');

  // 6. Clean orphan dollars around single words or arrows
  out = out.replace(/\$\s*([→←↔⇒⇐⇔])\s*/g, ' $1 ');
  out = out.replace(/\s*([→←↔⇒⇐⇔])\s*\$/g, ' $1 ');

  // 7. Normalize punctuation spacing & double spaces
  out = out.replace(/\s+([।,.:;!?])/g, '$1');
  out = out.replace(/[ \t]{2,}/g, ' ');
  return out.trim();
};
