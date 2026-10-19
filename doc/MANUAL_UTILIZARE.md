[🇷🇴 Versiunea în limba română](MANUAL_UTILIZARE.md) | [🇬🇧 English Version](../Manual.md)

---

⚠️ **Notă:**  
✨ Proiect **100% AI‑powered 🪄** — concept, analiză, cod, testare, documentație — cu **omul** 👨‍💻 în buclă ca **big boss** 👨‍💼 pentru **control**, **fine‑tuning** și **decizii** 🤔😉🤫.  

---

# Manual de Utilizare și Referință Tehnică: Fossil SCM MCP (FossilSoloMCP)

Server Model Context Protocol (MCP) de nivel profesional pentru integrarea completă a sistemului de control al versiunilor **Fossil SCM** cu asistenți AI și medii moderne de dezvoltare.

---

## 1. Introducere & Filosofia Proiectului

### Ce este Fossil SCM?
[Fossil](https://fossil-scm.org/) este un sistem distribuit de control al versiunilor creat de D. Richard Hipp (autorul bazei de date SQLite). Spre deosebire de alte sisteme (precum Git), Fossil include nativ într-un singur executabil compact și autonom:
* **Controlul versiunilor arborelui de fișiere** (Version Control).
* **Sistem integrat de urmărire a sarcinilor și erorilor** (Bug & Task Ticketing).
* **Enciclopedie de proiect distribuită** (Sistem Wiki încorporat).
* **Interfață web grafică completă** (`fossil ui` / `fossil server`), accesibilă instantaneu din browser.
* **Format unic de stocare:** Întregul depozit, istoricul complet, tichetele și paginile wiki sunt stocate fizic într-un singur fișier bază de date SQLite (`.fossil`).

### De ce Fossil pentru dezvoltarea solo Om + AI?
În mediile de lucru moderne în care un dezvoltator colaborează strâns cu asistenți AI (cum ar fi agenții din Google Antigravity, Claude Desktop, Cursor, Continue etc.), Fossil oferă avantaje decisive:
1. **Zero dependențe de infrastructură externă:** Nu este nevoie de conturi cloud, chei API pentru servicii terțe, token-uri externe sau servere de baze de date. Totul este 100% local, privat și autonom pe calculatorul tău.
2. **Memorie persistentă nativă pentru AI:** Sistemul Wiki și Ticketing-ul integrate direct în depozit permit agentului AI să citească și să consemneze starea proiectului, deciziile arhitecturale și istoricul problemelor fără a polua directorul de cod sursă.
3. **Integritate tranzacțională atomică:** Datorită motorului SQLite intern, tranzacțiile sunt atomice, consistente și sigure împotriva întreruperilor accidentale de alimentare sau crash-urilor de proces.

### Ideal și pentru Echipe Mici (Fără Complexitatea Git-ului)
Deși este optimizat pentru lucrul solo asistat de AI, Fossil este o alegere excepțională și pentru **echipe mici (2–10 colaboratori)** care își doresc simplitate, claritate și vor să evite birocrația și complexitatea adesea copleșitoare a Git-ului:
1. **Soluție completă „All-in-One”:** Într-o echipă mică, configurarea și întreținerea separată a unor servicii precum GitHub/GitLab, Jira/Trello (task tracking), Confluence/Notion (documentație wiki) sau servere de forum consumă timp și resurse nejustificate. Fossil include toate aceste unelte nativ, legate organic de fiecare commit și stocate în același depozit SQLite.
2. **Eliminarea „ceremoniilor” complexe din Git:** Concepte precum *detached HEAD*, zona de staging (index) separată, rezolvări confuze de *rebase* interactiv, comenzi periculoase de *force push* sau pierderea commit-urilor orfane sunt absente sau simplificate radical în Fossil. Istoricul în Fossil este conceput pentru a fi trasabil, curat și fără surprize.
3. **Mecanismul nativ de Autosync:** Fossil dispune de modul `autosync` activat implicit. La fiecare `commit` sau `update`, depozitul se sincronizează automat cu depozitul central dacă acesta este configurat, eliminând rutina clasică repetitivă de `git fetch -> git stash -> git rebase -> git stash pop -> git push`.
4. **Server Web încorporat fără configurare:** Orice membru al echipei poate lansa instantaneu `fossil server` pe o mașină din rețeaua locală sau pe un VPS modest. Întreaga echipă beneficiază pe loc de o interfață web completă și securizată (cu utilizatori, permisiuni pe roluri, code review, tichete și pagini wiki), fără să fie nevoie de Nginx, Docker sau baze de date externe.

### Rolul serverului FossilSoloMCP
Acest server MCP acționează ca o punte de comunicație de mare viteză între modelele LLM și depozitele Fossil, expunând **31 de unelte specializate** prin protocolul standardizat MCP (Model Context Protocol).

---

## 2. Istoric, Origine și Comparație cu `agent-vc-mcp`

### Punctul de Plecare: `agent-vc-mcp`
Dezvoltarea acestui server a pornit inițial de la explorarea proiectului open-source [agent-vc-mcp](https://github.com/ManbotHQ/agent-vc-mcp) (creat de ManBotHQ pe GitHub), o primă încercare de a oferi un server MCP pentru Fossil scris în **TypeScript / Node.js**.

Deși conceptul de a oferi asistenților AI control asupra unui sistem de versionare a fost excelent, analiza codului sursă a scos la iveală limitări arhitecturale majore:

### Limitări Majore ale `agent-vc-mcp`:
1. **Model Sandbox Forțat și Rigid:**
   - `agent-vc-mcp` impunea un spațiu de lucru unic fix în `~/.agent-vc/workspace/` și o singură bază de date `~/.agent-vc/version_control.fossil`.
   - Proiectele erau tratate forțat doar ca subfoldere (`workspace/proiect-1/`, `workspace/proiect-2/`) în interiorul aceluiași repository masiv. Nu exista posibilitatea de a gestiona depozite independente pentru proiectele reale deja existente pe disc.
2. **Duplicarea Inutilă a Operațiunilor pe Fișiere:**
   - `agent-vc-mcp` amesteca versionarea cu operațiuni elementare de sistem de fișiere (`write_file`, `read_file`, `list_files`). Acestea erau redundante și intrau adesea în conflict cu uneltele native și avansate de fișiere deja puse la dispoziție de IDE-uri și asistenți AI.
3. **Set Foarte Limitat de Unelte (Exact 10 unelte):**
   - Oferă doar funcționalități rudimentare: `vc_init_project`, `vc_commit`, `vc_status`, `vc_diff`, cele 3 unelte de fișiere și un modul simplist de task-uri (`task_create`, `task_update`, `task_list`).
   - **Lipsuri critice:** Fără suport de ramuri (`branch`), fără etichete (`tag`), fără `stash`, fără inspecție granulară a istoricului pe fișiere (`finfo`), fără posibilitatea de a citi conținut istoric (`cat`), fără anulare sigură (`undo`, `revert`), fără configurare depozit (`settings`) și fără niciun suport pentru sistemul **Wiki**!
4. **Instabilitate și Blocaje Frecvente pe Windows:**
   - Funcția de lansare a proceselor folosea `spawn` fără timeout și fără închiderea/redirecționarea intrării standard (`stdin`). Dacă `fossil.exe` solicita vreo confirmare interactivă (de exemplu pentru fișiere binare noi sau avertismente CRLF), procesul se bloca la infinit (hang).
   - Comanda de configurare a `crlf-glob *` eșua din cauza expandării wildcard-urilor de către runtime-ul Windows.
5. **Lipsa Flexibilității CWD Dinamic:**
   - Calea spațiului de lucru era determinată static la lansarea serverului (prin variabila de mediu `AGENT_VC_WORKSPACE`). Nicio unealtă nu accepta un parametru de cale, astfel încât serverul nu putea opera dinamic pe multiple proiecte.
6. **Ecosistemul Node.js / TypeScript:**
   - Necesita Node.js, `npx` și pachete `node_modules` voluminoase, complicând integrarea într-un mediu bazat pe Python și automatizări AI.

---

### Trecerea la `FossilSoloMCP`: Reproiectare și Rescriere

S-a luat decizia strategică de a rescrie serverul complet de la zero în **Python**, folosind framework-ul performant **FastMCP**.

| Caracteristică | `agent-vc-mcp` (Original) | `FossilSoloMCP` (Proiectul Curent) |
| :--- | :--- | :--- |
| **Limbaj & Runtime** | TypeScript / Node.js (`npx`) | **Python 3.14+ (FastMCP)** gestionat ultrarapid prin `uv` |
| **Număr Unelte Expuse** | Exact 10 unelte | **31 de unelte complete și specializate** |
| **Gestiune Directoare (CWD)** | Static, fixat la pornire via env vars | **Dinamic per apel (`cwd`)** pe toate cele 31 de unelte |
| **Organizare Depozite** | Un singur repo comun în `~/.agent-vc/` | **Repozitorii independente**, stocate curat în `.fossil_repositories/` |
| **Operațiuni pe Fișiere** | Forța wrapper-e rigide (`write_file`, etc.) | **Decuplat total:** se bazează pe uneltele native ale agentului |
| **Inspecție Istorică Avansată** | Niciuna (doar `vc_diff` global) | **`fossil_timeline` (cu filtre), `fossil_finfo`, `fossil_cat` istoric** |
| **Ramuri & Etichete** | Inexistente | **Suport complet (`fossil_branch`, `fossil_tag`)** |
| **Stashing & Revert** | Inexistente | **Gestiune completă (`fossil_stash`, `fossil_revert`, `fossil_undo`)** |
| **Sistem Wiki (Memorie AI)** | Inexistent | **Integrat (`fossil_wiki_ls`, `wiki_read`, `wiki_write`)** |
| **Sistem Ticketing** | Modul proprietar simplist | **Integrat nativ Fossil cu fallback inteligent SQL** |
| **Reziliență Windows & Anti-Hang** | Blocaje frecvente în consolă | **`stdin=DEVNULL`, auto-răspuns `a` la prompturi, timeout 30s** |
| **Gestiune CRLF / LF** | Erori la comanda de setare | **Injecție SQL directă în SQLite + auto-generare `.editorconfig`** |

---

## 3. Prerechizite și Instalare

### 1. Prerechizite Sistem
1. **Utilitarul Fossil SCM:**
   - Descărcați executabilul oficial pentru sistemul dvs. de operare (Windows, Linux sau macOS) de la [https://fossil-scm.org/](https://fossil-scm.org/).
   - Amplasați executabilul într-un director din sistem (de exemplu `C:\Program Files\Fossil\` pe Windows sau `/usr/local/bin/` pe Linux/macOS).
   - Asigurați-vă că directorul respectiv este inclus în variabila de mediu `PATH`.
   - Verificați disponibilitatea în consolă:
     ```bash
     fossil version
     ```
2. **Python & `uv`:**
   - Se recomandă **Python 3.14 sau mai nou**.
   - Managerul modern de medii și pachete `uv` instalat în sistem (sau mediul Python standard).

---

### 2. Configurare în Clienți MCP

Configurarea se realizează prin adăugarea definiției serverului în fișierul de configurare al clientului MCP dorit (`mcp_config.json`, `claude_desktop_config.json`, etc.).

#### Exemplu Universal pentru Windows:
```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:/Cale/Catre/FossilSoloMCP",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

#### Exemplu Universal pentru Linux / macOS:
```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/utilizator/proiecte/FossilSoloMCP",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

> [!TIP]
> **Înlocuiți calea:** Înlocuiți `"C:/Cale/Catre/FossilSoloMCP"` sau `"/home/utilizator/proiecte/FossilSoloMCP"` cu calea absolută reală unde ați clonat sau salvat proiectul pe calculatorul dvs.
> 
> **Despre argumentul `--repository`:** Serverul funcționează complet dinamic pe baza parametrului `cwd` transmis la fiecare apel de unealtă. Prin urmare, nu este necesar să specificați un depozit static la pornirea serverului.

---

## 4. Arhitectura și Organizarea Depozitelor

### Convenția `.fossil_repositories`
Pentru a păstra rădăcina proiectelor curată și pentru a evita stocarea de baze de date voluminoase în interiorul directorului de lucru, serverul implementează automat o convenție curată:

1. **Baza de Date a Depozitului (`.fossil`):**
   - Este salvată într-un director ascuns `.fossil_repositories/` creat automat în folderul părinte al spațiului de lucru (de exemplu: `../.fossil_repositories/NumeProiect.fossil`).
2. **Directorul de Lucru (Checkout):**
   - Conține codul sursă, documentația și fișierul ascuns de legătură al Fossil denumit `_FOSSIL_` (pe Windows) sau `.fslckout` (pe Linux/macOS).
   - Acest fișier conține calea către baza de date SQLite a depozitului asociat.

### Deschiderea Interfeței Grafice Web
Fossil include nativ un server HTTP și o interfață web completă. Pentru a explora depozitul vizual în browser, este suficient să rulați în terminalul deschis în directorul proiectului:
```bash
fossil ui
```
*(Opțional, pe Windows, puteți rula scriptul utilitar `open-ui-fossil.bat` inclus în rădăcină).*

Comanda deschide automat browserul implicit la adresa `http://localhost:8080`, oferind acces la:
- **Timeline:** Arborele grafic al tuturor ramurilor, tag-urilor și commit-urilor.
- **Files:** Navigare prin fișiere la orice revizie istorică, cu diff-uri și adnotare (blame).
- **Tickets:** Vizualizarea și editarea sarcinilor și bug-urilor.
- **Wiki:** Navigarea prin articolele și documentația proiectului.

---

## 5. Ghid de Lucru pentru Agenți AI (Fluxuri Universale Recomandate)

> [!IMPORTANT]
> **Regula de Aur pentru Agenți:**
> La apelarea oricărui tool din serverul `fossil-scm`, includeți **întotdeauna** parametrul `cwd` setat explicit la calea absolută a directorului pe care operați (de exemplu: `cwd="C:/Proiecte/AplicatiaMea"`).

---

### Regulă Recomandată pentru Agentul AI (System Prompt / Reguli de lucru)
Dacă doriți ca asistentul dvs. AI să folosească automat și corect serverul Fossil în orice client (Claude Desktop, Cursor, Antigravity etc.), puteți adăuga următoarea regulă în instrucțiunile de sistem:

```text
Pentru versionare, tichete și documentație internă, folosește uneltele serverului MCP fossil-scm.
La orice apel, transmite întotdeauna parametrul 'cwd' setat la calea directorului proiectului curent.
Înainte de a face modificări, verifică starea cu fossil_status. La finalul fiecărei sarcini rezolvate,
înregistrează fișierele cu fossil_add și comite modificările cu fossil_commit oferind un mesaj clar.
```

---

### Fluxul 1: Inițializarea unui Proiect Nou
Când utilizatorul cere începerea unui proiect nou cu versionare Fossil:
1. Agentul apelează `fossil_init`:
   ```json
   {
     "project_name": "AplicatiaMea",
     "cwd": "C:/Proiecte/AplicatiaMea"
   }
   ```
   *Ce face serverul automat:*
   - Creează directorul `.fossil_repositories/` în folderul părinte dacă nu există.
   - Inițializează `AplicatiaMea.fossil`.
   - Deschide depozitul în folderul de lucru (`fossil open`).
   - Aplică setările automate anti-CRLF direct în SQL (`crlf-glob = *`).
   - Generează automat fișierul `.editorconfig` (`end_of_line = lf`) și îl adaugă în versionare.

---

### Fluxul 2: Ciclul Standard de Modificare și Commit
Pe parcursul dezvoltării sau depanării, agentul urmează un ciclu standard:
1. **Verifică starea fișierelor:**
   `fossil_status(cwd="...")`
2. **Inspectează modificările concrete (diff):**
   `fossil_diff(cwd="...")`
3. **Înregistrează fișierele noi:**
   - Pentru fișiere punctuale: `fossil_add(files=["src/main.py"], cwd="...")`
   - Pentru sincronizare automată (fișiere noi și șterse): `fossil_addremove(cwd="...")`
4. **Comiterea în depozit:**
   `fossil_commit(message="Implementare modul autentificare", cwd="...")`
   *(Serverul rezolvă automat fără blocaje orice prompt de confirmare).*

---

### Fluxul 3: Explorare Istorică și Investigare Fără Risc
Spre deosebire de alte sisteme unde agentul riscă să suprascrie spațiul de lucru când vrea să consulte codul din trecut:
- **`fossil_timeline`:** Afișează istoricul recent al evenimentelor. Suportă filtrarea doar pe un anumit fișier (`path="src/main.py"`).
- **`fossil_finfo`:** Afișează toate modificările suferite de-a lungul timpului de un singur fișier specificat.
- **`fossil_cat` (Arma secretă):** Permite citirea conținutului unui fișier direct dintr-o revizie istorică sau tag, **fără a atinge sau deranja fișierele de pe disc din spațiul de lucru curent**:
  ```json
  {
    "file": "src/main.py",
    "revision": "f731ad3851",
    "cwd": "..."
  }
  ```

---

### Fluxul 4: Gestiunea Sarcinilor (Ticketing)
Fossil are un sistem complet de ticketing stocat în baza de date:
1. **Listare tichete existente:**
   `fossil_ticket_list(cwd="...")`
2. **Creare sarcină nouă / raport de bug:**
   ```json
   {
     "title": "Remediere eroare de timeout la apeluri asincrone",
     "status": "open",
     "additional_fields": {
       "type": "Code_Defect",
       "severity": "High"
     },
     "cwd": "..."
   }
   ```
3. **Închidere sau actualizare tichet:**
   ```json
   {
     "ticket_id": "a1b2c3d4",
     "field_name": "status",
     "field_value": "closed",
     "cwd": "..."
   }
   ```

---

### Fluxul 5: Documentație ca Memorie Persistentă (Wiki)
Paginile Wiki din Fossil sunt stocate direct în depozit și nu depind de fișiere de pe disc:
1. **Listare pagini existente:**
   `fossil_wiki_ls(cwd="...")`
2. **Citire documentație:**
   `fossil_wiki_read(page_name="ArhitecturaSistemului", cwd="...")`
3. **Salvare decizii tehnice pentru sesiunile viitoare:**
   `fossil_wiki_write(page_name="DeciziiDesign", content="# Decizii...", cwd="...")`

---

## 6. Referința Completă a Celor 31 de Instrumente MCP

### A. Version Control (20 Instrumente)

#### 1. `fossil_status`
- **Descriere:** Afișează starea curentă a fișierelor din spațiul de lucru (modificate, adăugate, lipsă, fișiere netrackuite).
- **Parametri:**
  - `cwd` *(string, opțional)*: Calea directorului de lucru.
  - `dotfiles` *(boolean, default: false)*: Dacă include fișierele/folderele ascunse (care încep cu punct).
  - `brief` *(boolean, default: false)*: Afișare concisă doar cu cuvinte cheie.
  - `ignore` *(string, opțional)*: Tipare glob separate prin virgulă pentru fișiere de ignorat.

#### 2. `fossil_diff`
- **Descriere:** Afișează diferențele de cod (diff) între modificările din spațiul de lucru și depozit sau între revizii istorice.
- **Parametri:**
  - `cwd` *(string, opțional)*: Directorul de lucru.
  - `files` *(array de string-uri, opțional)*: Listă specifică de fișiere de comparat.
  - `from_version` *(string, opțional)*: Revizia de pornire (`--from`).
  - `to_version` *(string, opțional)*: Revizia de destinație (`--to`).
  - `branch` *(string, opțional)*: Compară modificările ramurii specificate.
  - `brief` *(boolean, default: false)*: Listează doar numele fișierelor modificate fără diff-ul complet.
  - `ignore_whitespace` *(boolean, default: false)*: Ignoră modificările cauzate de spații/taburi (`-w`).

#### 3. `fossil_cat`
- **Descriere:** Extrage și returnează conținutul textual al unui fișier dintr-o revizie istorică specificată, fără a modifica spațiul de lucru local.
- **Parametri:**
  - `file` *(string, obligatoriu)*: Calea relativă a fișierului.
  - `revision` *(string, obligatoriu)*: Hash-ul, eticheta sau ramura reviziei dorite.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 4. `fossil_finfo`
- **Descriere:** Returnează istoricul detaliat de modificări pentru un singur fișier specificat. Traversează transparent evenimentele de redenumire efectuate cu `fossil_mv`.
- **Parametri:**
  - `file` *(string, obligatoriu)*: Calea fișierului.
  - `limit` *(integer, opțional)*: Numărul maxim de revizii afișate (`-n`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 5. `fossil_add`
- **Descriere:** Programează adăugarea unuia sau mai multor fișiere/directoare în versionare.
- **Parametri:**
  - `files` *(array de string-uri, obligatoriu)*: Lista de căi către fișiere sau directoare.
  - `force` *(boolean, default: true)*: Forțează adăugarea chiar dacă se potrivesc cu un tipar `ignore-glob`.
  - `dotfiles` *(boolean, default: false)*: Include fișiere ascunse la parcurgere recursivă.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 6. `fossil_rm`
- **Descriere:** Elimină fișiere din controlul versiunilor.
- **Parametri:**
  - `files` *(array de string-uri, obligatoriu)*: Lista fișierelor de eliminat.
  - `force` *(boolean, default: false)*: Forțează ștergerea fără avertismente.
  - `keep` *(boolean, default: false)*: Păstrează fișierele fizic pe disc, eliminându-le doar din versionare.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 7. `fossil_mv`
- **Descriere:** Redenumește sau mută un fișier ori director în depozit și pe disc. Înregistrează explicit evenimentul `RENAME` în graful de versiuni (DAG), asigurând trasabilitatea completă a istoricului prin `fossil_finfo`.
- **Parametri:**
  - `old_name` *(string, obligatoriu)*: Calea sursă a fișierului sau directorului.
  - `new_name` *(string, obligatoriu)*: Calea destinație a fișierului sau directorului.
  - `hard` *(boolean, default: true)*: Dacă mută/redenumește fișierul fizic pe disc (`--hard`). Dacă este False, înregistrează doar intenția în manifest (`--soft`).
  - `case_sensitive` *(boolean, opțional)*: Forțează respectarea majusculelor/minusculelor (`--case-sensitive 1/0`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 8. `fossil_addremove`
- **Descriere:** Scanează spațiul de lucru și adaugă automat fișierele noi, eliminându-le pe cele șterse de pe disc.
- **Parametri:**
  - `dotfiles` *(boolean, default: false)*: Include dotfiles.
  - `ignore` *(string, opțional)*: Tipare glob de ignorat.
  - `clean` *(boolean, default: false)*: Șterge fișierele suplimentare netrackuite.
  - `reset` *(boolean, default: false)*: Resetează starea add/remove.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 9. `fossil_extras`
- **Descriere:** Listează toate fișierele din directorul curent care nu sunt sub controlul versiunilor.
- **Parametri:**
  - `dotfiles` *(boolean, default: false)*: Include fișierele ascunse.
  - `ignore` *(string, opțional)*: Filtru glob suplimentar.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 10. `fossil_clean`
- **Descriere:** Șterge fișierele netrackate și temporare din arborele de lucru (`fossil clean`).
- **Parametri:**
  - `all_files` *(boolean, default: false)*: Forțează ștergerea fără confirmare interactivă (`-f`).
  - `dry_run` *(boolean, default: false)*: Simulare fără ștergere; afișează lista fișierelor care ar fi eliminate (`-n`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 11. `fossil_revert`
- **Descriere:** Anulează modificările nesalvate dintr-unul sau mai multe fișiere, readucându-le la starea din depozit.
- **Parametri:**
  - `files` *(array de string-uri, obligatoriu)*: Fișierele de readus la starea inițială.
  - `revision` *(string, opțional)*: Revizia la care să fie readuse (implicit checkout-ul curent).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 12. `fossil_stash`
- **Descriere:** Salvează temporar modificările locale nesalvate pentru a lăsa spațiul curat, permițând reaplicarea lor ulterioară.
- **Parametri:**
  - `action` *(string, default: "save")*: Acțiunea dorită: `"save"`, `"snapshot"`, `"list"`, `"pop"`, `"apply"`, `"drop"`, `"diff"`.
  - `comment` *(string, opțional)*: Notiță pentru stash.
  - `stash_id` *(integer, opțional)*: Numărul de identificare al stash-ului.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 13. `fossil_tag`
- **Descriere:** Gestionează etichete simbolice asociate anumitor revizii (check-in-uri).
- **Parametri:**
  - `action` *(string, default: "list")*: `"add"`, `"cancel"`, `"list"`.
  - `tag_name` *(string, opțional)*: Numele etichetei (ex: `"v1.0.0"`).
  - `checkin` *(string, opțional)*: Revizia căreia i se atașează tag-ul.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 14. `fossil_commit`
- **Descriere:** Înregistrează definitiv modificările într-un nou check-in în depozit.
- **Parametri:**
  - `message` *(string, obligatoriu)*: Mesajul de commit.
  - `files` *(array de string-uri, opțional)*: Fișiere specifice de inclus în commit.
  - `branch` *(string, opțional)*: Numele unei ramuri noi pe care să fie plasat commit-ul (`--branch`).
  - `no_warnings` *(boolean, default: true)*: Omite avertismentele de conținut și CRLF.
  - `allow_empty` *(boolean, default: false)*: Permite commit chiar dacă nu există modificări.
  - `user_override` *(string, opțional)*: Înregistrează un alt nume de autor.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 15. `fossil_timeline`
- **Descriere:** Afișează istoricul cronologic al acțiunilor și commit-urilor din proiect.
- **Parametri:**
  - `limit` *(integer, default: 20)*: Numărul de evenimente afișate.
  - `path` *(string, opțional)*: Filtrează timeline-ul doar pentru un anumit fișier/director (`-p`).
  - `type_filter` *(string, opțional)*: Filtru de tip: `"ci"` (checkins), `"w"` (wiki), `"t"` (tickets), `"e"` (events) (`-t`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 16. `fossil_info`
- **Descriere:** Afișează informații detaliate despre depozit, checkout-ul activ sau o revizie anume.
- **Parametri:**
  - `target` *(string, opțional)*: Hash-ul, eticheta sau fișierul de inspectat.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 17. `fossil_branch`
- **Descriere:** Gestionează ramurile de dezvoltare paralele.
- **Parametri:**
  - `action` *(string, default: "list")*: `"list"` sau `"new"`.
  - `branch_name` *(string, opțional)*: Numele noii ramuri la `action="new"`.
  - `basis` *(string, opțional)*: Punctul de plecare (check-in de bază).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 18. `fossil_merge`
- **Descriere:** Fuzionează o altă ramură sau un commit specific în spațiul de lucru curent (`fossil merge`).
- **Parametri:**
  - `branch_or_version` *(string, obligatoriu)*: Numele ramurii sau hash-ul commit-ului de integrat.
  - `integrate` *(boolean, default: false)*: Dacă este True (`--integrate`), închide automat ramura sursă după fuziune la următorul commit.
  - `dry_run` *(boolean, default: false)*: Simulează fuziunea fără a modifica fișierele locale (`-n`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 19. `fossil_update`
- **Descriere:** Actualizează fișierele din spațiul de lucru la cea mai recentă revizie sau comută pe o altă ramură/versiune.
- **Parametri:**
  - `target` *(string, opțional)*: Versiunea, ramura sau eticheta către care se comută.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 20. `fossil_undo`
- **Descriere:** Anulează ultima operațiune de `update`, `revert` sau `merge` efectuată în spațiul de lucru.
- **Parametri:**
  - `dry_run` *(boolean, default: false)*: Afișează ce ar fi anulat fără a executa operațiunea.
  - `cwd` *(string, opțional)*: Directorul de lucru.

---

### B. Administrare & Depozit (5 Instrumente)

#### 21. `fossil_init`
- **Descriere:** Creează și configurează o nouă bază de date Fossil și o deschide automat în directorul indicat.
- **Parametri:**
  - `db_name` *(string, opțional)*: Numele fișierului depozitului (implicit numele folderului curent).
  - `project_name` *(string, opțional)*: Numele logic al proiectului.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 22. `fossil_open`
- **Descriere:** Deschide un depozit Fossil existent în directorul specificat.
- **Parametri:**
  - `db_name` *(string, obligatoriu)*: Numele sau calea depozitului `.fossil`.
  - `force` *(boolean, default: false)*: Forțează deschiderea chiar dacă directorul nu e gol (`-f`).
  - `keep` *(boolean, default: false)*: Păstrează fișierele locale existente (`-k`).
  - `workdir` *(string, opțional)*: Directorul țintă în care se va deschide checkout-ul (implicit directorul părinte al depozitului).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 23. `fossil_close`
- **Descriere:** Închide checkout-ul Fossil activ din directorul specificat, decuplând spațiul de lucru de fișierul depozit.
- **Parametri:**
  - `force` *(boolean, default: false)*: Forțează închiderea chiar dacă există modificări locale necomise (`-f`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 24. `fossil_clone`
- **Descriere:** Clonează un depozit Fossil de la un URL la distanță (HTTP/HTTPS/SSH) sau dintr-o cale locală direct într-un fișier bază de date `.fossil`, fără a deschide checkout în directorul curent.
- **Parametri:**
  - `url_or_path` *(string, obligatoriu)*: URL-ul la distanță (HTTP/HTTPS/SSH) sau calea fișierului local sursă.
  - `repository_path` *(string, obligatoriu)*: Calea fișierului `.fossil` destinație.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 25. `fossil_settings`
- **Descriere:** Consultă sau modifică proprietățile și setările depozitului (`crlf-glob`, `binary-glob`, `ignore-glob`, `autosync` etc.).
- **Parametri:**
  - `name` *(string, opțional)*: Numele proprietății (dacă lipsește, listează toate setările).
  - `value` *(string, opțional)*: Noua valoare de configurat.
  - `cwd` *(string, opțional)*: Directorul de lucru.

---

### C. Sistemul de Ticketing (3 Instrumente)

#### 26. `fossil_ticket_list`
- **Descriere:** Listează tichetele existente în depozit (cu fallback automat pe interogare directă SQLite dacă rapoartele Fossil nu sunt configurate).
- **Parametri:**
  - `report` *(integer, default: 1)*: Numărul raportului standard Fossil.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 27. `fossil_ticket_create`
- **Descriere:** Deschide un tichet nou în sistemul de tracking al depozitului.
- **Parametri:**
  - `title` *(string, obligatoriu)*: Titlul sau rezumatul sarcinii/erorii.
  - `status` *(string, default: "open")*: Starea inițială (`"open"`, `"in_progress"`, `"closed"` etc.).
  - `additional_fields` *(dicționar / obiect JSON, opțional)*: Câmpuri adiționale (ex: `type`, `severity`, `subsystem`, `description`).
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 28. `fossil_ticket_update`
- **Descriere:** Modifică un câmp sau statusul unui tichet existent.
- **Parametri:**
  - `ticket_id` *(string, obligatoriu)*: Identificatorul UUID al tichetului (sau primele caractere).
  - `field_name` *(string, obligatoriu)*: Numele câmpului de modificat (ex: `"status"`, `"comment"`).
  - `field_value` *(string, obligatoriu)*: Noua valoare atribuită câmpului.
  - `cwd` *(string, opțional)*: Directorul de lucru.

---

### D. Sistemul Wiki (3 Instrumente)

#### 29. `fossil_wiki_ls`
- **Descriere:** Returnează lista tuturor paginilor wiki existente în depozit.
- **Parametri:**
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 30. `fossil_wiki_read`
- **Descriere:** Citește și returnează conținutul complet în format text/markdown al paginii wiki solicitate.
- **Parametri:**
  - `page_name` *(string, obligatoriu)*: Numele paginii wiki.
  - `cwd` *(string, opțional)*: Directorul de lucru.

#### 31. `fossil_wiki_write`
- **Descriere:** Creează o pagină wiki nouă sau actualizează conținutul unei pagini existente în depozit.
- **Parametri:**
  - `page_name` *(string, obligatoriu)*: Numele paginii wiki.
  - `content` *(string, obligatoriu)*: Conținutul Markdown sau text al paginii.
  - `cwd` *(string, opțional)*: Directorul de lucru.

---

## 7. Particularități Windows & Soluții Tehnice Încorporate

Dezvoltarea pe sisteme de operare Windows ridică provocări particulare pentru utilitare portate din lumea UNIX. Serverul `FossilSoloMCP` include măsuri de reziliență construite special:

### 1. Problema Expandării Wildcard-urilor la `crlf-glob "*"`
- **Fenomenul:** Pe Windows, runtime-ul MSVC/MinGW al `fossil.exe` expandează automat caracterele `*` înainte de funcția `main()`. Comanda `fossil settings crlf-glob "*"` ajungea la Fossil ca o listă cu toate fișierele din folder, declanșând erori de sintaxă.
- **Soluția:** Serverul aplică setarea direct în baza de date a depozitului prin SQL nativ:
  ```sql
  REPLACE INTO config(name,value) VALUES('crlf-glob','*')
  ```
  Ocolind complet CLI-ul, configurarea este 100% sigură și atomică.

### 2. Păstrarea Standardului LF prin `.editorconfig`
- Deși setarea `crlf-glob = *` dezactivează blocajele de commit, fișierele cu terminatori Windows (`CRLF`) pot genera diff-uri artificiale.
- Serverul generează automat la `fossil_open` un fișier `.editorconfig` cu regula `end_of_line = lf`, asigurând ca editoarele de cod să salveze curat cu terminatori standardizați UNIX.

### 3. Protecție Anti-Hang și Timeout de Siguranță
- Orice proces CLI apelat are `stdin` redirecționat către `subprocess.DEVNULL` când nu primește date explicite, prevenind blocarea la prompturi interactive.
- La `fossil_commit`, serverul trimite automat răspunsul `a\n` pe intrarea standard pentru a valida prompturile legate de fișiere binare sau avertismente.
- Toate apelurile de proces au timeout fixat la 30 de secunde, cu capturare completă de `stderr` și cod de retur pentru diagnosticare imediată.

---

## 8. Bune Practici & Sfaturi de Lucru

1. **Commit-uri Atomice și Explicite:**
   - Efectuați commit-uri frecvente și concentrate după fiecare pas funcțional sau eroare remediată. Astfel, prin `fossil_undo` sau `fossil_revert`, puteți reveni oricând la un punct de stabilitate verificat.
2. **Păstrarea Istoricului de Proiect în Wiki:**
   - Folosiți paginile Wiki (`fossil_wiki_write`) pentru a consemna concluzii de arhitectură sau instrucțiuni de deployment. Fiind stocate în baza `.fossil`, ele nu se pierd și sunt accesibile direct în browser prin `fossil ui`.
3. **Optimizare Avansată: Lucrul pe RAM Disk (Opțional):**
   - Pentru dezvoltatorii care efectuează teste de anduranță, generare masivă de fișiere temporare sau rulare intensivă de scripturi scratch automate cu AI, utilizarea unui RAM Disk temporar este o modalitate excelentă de a proteja ciclurile de scriere ale SSD-urilor și de a obține viteze maxime de I/O. La finalizarea sesiunilor de lucru, modificările de cod validate pot fi sincronizate în directorul permanent al proiectului și salvate în depozit.
4. **Automatizări Avansate cu Agenți AI:**
   - În funcție de clientul sau IDE-ul utilizat (de exemplu reguli de lucru în Google Antigravity, `.cursorrules` în Cursor sau System Prompts în Claude Desktop), puteți defini instrucțiuni standardizate pentru ca agentul să versioneze automat fiecare modificare importantă fără intervenție manuală repetată.

---

## 9. Licență & Declinarea Responsabilității (No Warranty)

### 📄 Licență

Acest proiect este licențiat sub termenii licenței **MIT**. Consultă fișierul [LICENSE](../LICENSE) pentru detalii complete.

---

### 📝 Garanție

Nu se oferă absolut niciun fel de garanție!

