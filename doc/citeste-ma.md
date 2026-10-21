[🇷🇴 Versiunea în limba română](citeste-ma.md) | [🇬🇧 English Version](../README.md)

---

⚠️ **Notă:**  
✨ Proiect **100% AI‑powered 🪄** — concept, analiză, cod, testare, documentație — cu **omul** 👨‍💻 în buclă ca **big boss** 👨‍💼 pentru **control**, **fine‑tuning** și **decizii** 🤔😉🤫.  

---

# Fossil SCM - Server MCP

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.3.0+-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![GitHub Release](https://img.shields.io/github/v/release/ReluPercan/FossilSoloMCP?logo=github&logoColor=white)](https://github.com/ReluPercan/FossilSoloMCP/releases)
[![PyPI](https://img.shields.io/pypi/v/fossil-scm-mcp.svg?logo=pypi&logoColor=white)](https://pypi.org/project/fossil-scm-mcp/)
[![Licență: MIT](https://img.shields.io/badge/Licență-MIT-brightgreen.svg)](../LICENSE)
[![Fossil SCM](https://img.shields.io/badge/Fossil_SCM-Compatibil-blue.svg)](https://fossil-scm.org/)

Un server robust bazat pe protocolul Model Context Protocol (MCP) ce oferă acces programatic complet și non-interactiv (headless) la depozitele **Fossil SCM**. Acesta expune **31 de unelte dedicate** care acoperă Controlul Versiunilor, Administrarea & Setările Depozitului, Sistemul de Tichete (Bug Tracking) și Documentația Wiki, concepute special pentru agenți AI (Google Antigravity, Claude Desktop, Cursor etc.).

## Cerințe preliminare

> [!IMPORTANT]
> **AVERTISMENT CRITIC:** Acest pachet NU instalează executabilul Fossil propriu-zis.  
> Pentru ca acest server MCP să funcționeze, TREBUIE să aveți utilitarul în linie de comandă `fossil` instalat și adăugat în variabila de mediu `PATH` a sistemului dumneavoastră.

1. Descărcați Fossil de pe site-ul oficial: [https://fossil-scm.org/](https://fossil-scm.org/)
2. Dezarhivați și plasați executabilul (`fossil.exe` pe Windows, `fossil` pe Linux/macOS) într-un director la alegere.
3. Adăugați directorul respectiv în `PATH`-ul sistemului.

## Instalare & Configurare

Pentru a integra acest server MCP cu Claude Desktop, Google Antigravity sau alți clienți compatibili MCP, adăugați următoarea configurație în fișierul de setări MCP (de exemplu `claude_desktop_config.json` sau `mcp_config.json`):

### Utilizând `uv` (Recomandat)

```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/cale/catre/fossil-scm-mcp",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

*Înlocuiți `/cale/catre/fossil-scm-mcp` cu calea reală către directorul repozitoriului de pe sistemul dumneavoastră (de exemplu `C:/Tools/FossilSCM` sau `/home/utilizator/FossilSCM`).*

> [!IMPORTANT]
> **Regula de Aur pentru Agenți AI (`cwd` dinamic):**  
> Serverul rulează complet decuplat și dinamic. Pentru a gestiona corect depozite multiple fără conflicte, **instruiți întotdeauna asistentul AI să furnizeze parametrul `cwd`** (calea absolută a proiectului curent) la fiecare apel de unealtă.  
> 
> *Regulă recomandată pentru Agentul AI (System Prompt / Instrucțiuni personalizate):*
> ```text
> La apelarea oricărui tool din serverul MCP fossil-scm, furnizează întotdeauna parametrul 'cwd' setat explicit la calea directorului de lucru curent.
> ```

> [!TIP]
> Parametrul CLI `--repository` poate fi utilizat opțional pentru a specifica un director de lucru prestabilit de rezervă în cazul apelurilor fără `cwd`. Totuși, transmiterea dinamică a parametrului `cwd` la fiecare apel reprezintă practica recomandată.

## Caracteristici și Funcționalități Cheie

- **31 de Unelte Specializate:**
  - **Controlul Versiunilor (20 de unelte):** Starea spațiului de lucru (`fossil_status`), diferențe cu suport pentru revizii și ramuri (`fossil_diff`), vizualizare istorică a fișierelor fără checkout (`fossil_cat`), istoric per fișier (`fossil_finfo`), restaurare granulară a fișierelor (`fossil_revert`), redenumire fișiere cu conservarea istoricului în graful DAG (`fossil_mv`), igienizarea spațiului de lucru (`fossil_clean`), fuzionarea ramurilor cu închidere automată (`fossil_merge`), depozitare temporară/stash (`fossil_stash`), etichete simbolice/taguri (`fossil_tag`), adăugare/eliminare granulară (`fossil_add`, `fossil_rm`, `fossil_addremove`, `fossil_extras`), gestionarea ramurilor (`fossil_branch`), comitere cu creare directă de ramură (`fossil_commit`), cronologie/timeline cu filtre pe cale și tip (`fossil_timeline`), precum și operațiuni sigure de anulare și actualizare (`fossil_undo`, `fossil_update`).
  - **Tichete & Urmărire Erori (3 unelte):** Listare (`fossil_ticket_list`), creare (`fossil_ticket_create`) și actualizare tichete (`fossil_ticket_update`), stocate direct în baza de date a depozitului.
  - **Documentație Wiki (3 unelte):** Listare (`fossil_wiki_ls`), export/citire (`fossil_wiki_read`) și comitere/scriere (`fossil_wiki_write`) pagini wiki în format Markdown.
  - **Administrare & Configurare Depozit (5 unelte):** Inițializare depozite noi (`fossil_init`), deschidere depozite (`fossil_open`), închidere checkout activ (`fossil_close`), clonare depozite la distanță sau locale (`fossil_clone`) și inspectare/modificare setări (`fossil_settings`).
- **Reziliență Non-Interactivă & Anti-Hang:**
  - Redirecționează automat `stdin` către `DEVNULL` pentru a eșua imediat prompturile interactive CLI (`y/N`) în loc să blocheze execuția.
  - Mecanism integrat de timeout la 30 de secunde cu raportare clară a erorilor.
  - Flag `--no-warnings` implicit și tratare automată la comitere pentru fișiere binare și terminații de rând CRLF/LF.
  - `fossil_add` folosește `force=True` în mod implicit, ocolind curat prompturile de confirmare pentru tiparele `ignore-glob` atunci când fișierele sunt specificate nominal.
- **Depozite Centralizate:** Organizează automat depozitele într-un director `.fossil_repositories/` situat în afara spațiului de lucru activ.
- **Siguranță Înainte de Toate:** Operațiunile destructive (`undo`, `update`) sunt marcate explicit cu avertismente, determinând agenții AI să ceară confirmarea utilizatorului înainte de execuție.

---

## 📚 Documentație Completă

Pentru detalii arhitecturale avansate, ghiduri de fluxuri AI și referința completă a tuturor celor 31 de instrumente, consultați [Manualul de Utilizare și Referință Tehnică](MANUAL_UTILIZARE.md).

---

## 📄 Licență

Acest proiect este licențiat sub termenii licenței **MIT**. Consultă fișierul [LICENSE](../LICENSE) pentru detalii complete.

---

## 📝 Garanție

Nu se oferă absolut niciun fel de garanție!

