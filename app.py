import re
import requests
import streamlit as st

st.set_page_config(
    page_title="Mutation Impact Explorer",
    page_icon="🧬",
    layout="wide"
)

# ---------- THEME SWITCH ----------

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

st.sidebar.markdown("## ⚙️ Appearance")

theme_choice = st.sidebar.toggle(
    "Dark biotech theme",
    value=st.session_state.theme_mode == "Dark",
    key="theme_switch"
)

st.session_state.theme_mode = "Dark" if theme_choice else "Light"
is_dark = st.session_state.theme_mode == "Dark"

if is_dark:
    bg = "#0B1120"
    panel = "#131E32"
    text = "#E6EDF7"
    muted = "#9AAAC1"
    accent = "#2B8696"
    border = "#263650"
else:
    bg = "#F3F7FC"
    panel = "#FFFFFF"
    text = "#15243B"
    muted = "#62728A"
    accent = "#087FAD"
    border = "#D8E2EF"

# ---------- GLOBAL CSS ----------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700;900&family=Roboto:ital,wght@0,400;0,700;1,400;1,700&display=swap');

    :root {{
        --app-bg: {bg};
        --panel-bg: {panel};
        --app-text: {text};
        --muted-text: {muted};
        --accent: {accent};
        --app-border: {border};

        --field-bg: #DCEBFA;
        --field-text: #15243B;
        --field-border: #BFD7F0;
    }}

    /* Main background */
    [data-testid="stAppViewContainer"] {{
        background: var(--app-bg);
        color: var(--app-text);
    }}

    [data-testid="stHeader"] {{
        background: var(--app-bg);
    }}

    /* Main content font */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] button,
    [data-testid="stMarkdownContainer"],
    .stMarkdown {{
        font-family: 'Merriweather', Georgia, serif;
    }}

    h1, h2, h3 {{
        color: var(--app-text) !important;
        font-family: 'Merriweather', Georgia, serif !important;
        letter-spacing: -0.4px;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        color: var(--app-text);
    }}

    [data-testid="stCaptionContainer"] {{
        color: var(--muted-text);
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: var(--panel-bg);
        border-right: 1px solid var(--app-border);
    }}

    /* Text inputs and number inputs */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        background-color: var(--field-bg) !important;
        color: var(--field-text) !important;
        -webkit-text-fill-color: var(--field-text) !important;
        border: 1px solid var(--field-border) !important;
        border-radius: 10px !important;
        caret-color: var(--field-text) !important;
    }}

    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: #536B86 !important;
        -webkit-text-fill-color: #536B86 !important;
        opacity: 1;
    }}

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {{
        border-color: #8CBCEB !important;
        box-shadow: 0 0 0 2px rgba(140, 188, 235, 0.25);
    }}

    /* Dropdown controls */
    [data-baseweb="select"] > div {{
        background-color: var(--field-bg) !important;
        border-color: var(--field-border) !important;
        color: var(--field-text) !important;
        border-radius: 10px !important;
    }}

    [data-baseweb="select"] input,
    [data-baseweb="select"] span,
    [data-baseweb="select"] div {{
        color: var(--field-text);
    }}

    /* Dropdown options */
    [data-baseweb="popover"],
    [data-baseweb="menu"] {{
        background-color: #DCEBFA !important;
        color: #15243B !important;
    }}

    [role="option"] {{
        background-color: #DCEBFA !important;
        color: #15243B !important;
    }}

    [role="option"]:hover {{
        background-color: #BFD7F0 !important;
    }}

    /* Radio buttons and checkboxes */
    [data-testid="stCheckbox"],
    [data-testid="stRadio"] {{
        color: var(--app-text);
    }}

    /* Result cards */
    [data-testid="stMetric"] {{
        background: var(--panel-bg);
        border: 1px solid var(--app-border);
        padding: 18px;
        border-radius: 14px;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--accent);
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: var(--app-border);
        border-radius: 16px;
    }}

    [data-testid="stExpander"] {{
        background: var(--panel-bg);
        border: 1px solid var(--app-border);
        border-radius: 12px;
    }}

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {{
        background: var(--accent);
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.2rem;
        font-weight: 700;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        filter: brightness(1.12);
        transform: translateY(-1px);
    }}

    hr {{
        border-color: var(--app-border);
    }}

    /* Keep Material icons readable */
    [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded',
                     'Material Icons', sans-serif !important;
    }}

    /* Custom page heading */
    .hero-eyebrow {{
        color: var(--accent);
        font-family: 'Merriweather', Georgia, serif;
        font-size: 12px;
        letter-spacing: 3px;
        font-weight: bold;
        margin-bottom: 14px;
    }}

    .hero-title {{
        color: var(--app-text) !important;
        font-family: 'Roboto', Arial, sans-serif !important;
        font-size: 2.6rem;
        font-weight: 700;
        font-style: italic;
        line-height: 1.4;
        margin: 0 0 14px 0;
        text-shadow:
            0 0 7px rgba(80, 221, 245, 0.65),
            0 0 18px rgba(80, 221, 245, 0.30);
    }}

    .hero-description {{
        color: var(--muted-text) !important;
        font-family: 'Merriweather', Georgia, serif;
        font-size: 1rem;
        max-width: 780px;
        line-height: 1.9;
        margin: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------- PAGE HEADING ----------

st.markdown(
    "<p style='color:#2B8696; font-size:12px; "
    "letter-spacing:3px; font-weight:bold;'>"
    "BIOINFORMATICS · PROTEIN VARIANT ANALYSIS</p>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style="
        font-family: Roboto, Arial, sans-serif;
        font-style: italic;
        font-size: 42px;
        color: var(--app-text);
        text-shadow: 0 0 12px rgba(80,221,245,0.45);
    ">
        MUTEX
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "Exploring the unseen in every mutation"
)

# ---------- MUTATION INPUTS ----------

st.subheader("1. Enter your protein and mutation")

accession = st.text_input(
    "UniProt accession",
    value="P05067"
).strip()

mutation = st.text_input(
    "Mutation",
    value="L7V"
).strip().upper()

# Continue with your existing mutation-analysis code below.


st.subheader("2. Paste your Clustal Omega alignment")

st.write(
    "Paste the complete aligned sequences in FASTA format. "
    "Include the reference protein and related proteins."
)

alignment_text = st.text_area(
    "Aligned FASTA sequences",
    height=180,
    placeholder=(
        ">Reference_protein\n"
        "PASTE_REFERENCE_ALIGNMENT_HERE\n"
        ">Related_protein_1\n"
        "PASTE_RELATED_ALIGNMENT_HERE"
    )
)

st.caption(
    "Conservation analysis is optional. Leave this box "
    "empty to analyze the mutation without conservation."
)


def parse_fasta(text):
    records = {}
    name = None
    chunks = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            if name is not None:
                records[name] = "".join(chunks).upper()

            name = line[1:].strip()
            chunks = []

        else:
            if name is None:
                raise ValueError(
                    "Sequence data must follow a FASTA header."
                )

            chunks.append(line.replace(" ", ""))

    if name is not None:
        records[name] = "".join(chunks).upper()

    if not records:
        raise ValueError("No FASTA sequences were found.")

    return records


if st.button("Analyze Mutation", type="primary"):

    pattern = (
        r"([ACDEFGHIKLMNPQRSTVWY])"
        r"(\d+)"
        r"([ACDEFGHIKLMNPQRSTVWY])"
    )

    match = re.fullmatch(pattern, mutation)

    if not re.fullmatch(r"[A-Za-z0-9]+", accession):
        st.error("Enter a valid-looking UniProt accession.")
        st.stop()

    if not match:
        st.error(
            "Use mutation notation such as E7V."
        )
        st.stop()

    original_aa = match.group(1)
    position = int(match.group(2))
    new_aa = match.group(3)

    if position < 1:
        st.error("Position must be at least 1.")
        st.stop()

    if original_aa == new_aa:
        st.error("The two amino acids must be different.")
        st.stop()

    # Retrieve reference protein
    url = (
        "https://rest.uniprot.org/uniprotkb/"
        + accession + ".fasta"
    )

    try:
        with st.spinner("Retrieving protein sequence..."):
            response = requests.get(url, timeout=25)
            response.raise_for_status()

        lines = response.text.splitlines()

        sequence = "".join(
            line.strip()
            for line in lines
            if line and not line.startswith(">")
        ).upper()

        if not sequence:
            st.error("UniProt returned no sequence.")
            st.stop()

    except requests.RequestException:
        st.error(
            "Unable to retrieve the protein. "
            "Check the accession and internet connection."
        )
        st.stop()

    if position > len(sequence):
        st.error(
            f"The protein contains {len(sequence)} residues."
        )
        st.stop()

    actual_aa = sequence[position - 1]

    if actual_aa != original_aa:
        st.error(
            f"At position {position}, the reference contains "
            f"{actual_aa}, not {original_aa}. "
            "Check the mutation numbering."
        )
        st.stop()

    # Create mutant sequence
    mutated_sequence = (
        sequence[:position - 1]
        + new_aa
        + sequence[position:]
    )

    st.success("Mutation validated successfully!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Protein length", f"{len(sequence)} aa")
    col2.metric("Position", position)
    col3.metric(
        "Amino acid change",
        f"{original_aa} → {new_aa}"
    )

    st.subheader("3. Sequence comparison")

    start = max(0, position - 11)
    end = min(len(sequence), position + 10)
    offset = position - 1 - start

    ref_window = sequence[start:end]
    mut_window = mutated_sequence[start:end]

    ref_display = (
        ref_window[:offset]
        + "[" + ref_window[offset] + "]"
        + ref_window[offset + 1:]
    )

    mut_display = (
        mut_window[:offset]
        + "[" + mut_window[offset] + "]"
        + mut_window[offset + 1:]
    )

    st.code(
        f"Reference: {ref_display}\n"
        f"Mutated:   {mut_display}"
    )

    # Conservation analysis
    st.subheader("4. Conservation analysis")

    if not alignment_text.strip():

        st.info(
            "No alignment provided. To calculate conservation, "
            "paste an alignment from Clustal Omega above."
        )

    else:
        try:
            records = parse_fasta(alignment_text)

            if len(records) < 2:
                st.error(
                    "Provide the reference and at least one "
                    "related protein sequence."
                )
                st.stop()

            lengths = {len(seq) for seq in records.values()}

            if len(lengths) != 1:
                st.error(
                    "Aligned sequences must all have the "
                    "same length. Paste the aligned FASTA "
                    "output, not the original unaligned sequences."
                )
                st.stop()

            # Identify reference by exact sequence match
            reference_name = None

            for name, aligned_seq in records.items():
                ungapped = aligned_seq.replace("-", "")

                if ungapped == sequence:
                    reference_name = name
                    break

            if reference_name is None:
                st.error(
                    "The reference sequence in the alignment "
                    "does not exactly match the UniProt sequence. "
                    "Include the complete reference protein and "
                    "check its accession and sequence version."
                )
                st.stop()

            aligned_reference = records[reference_name]

            # Map the protein position to its alignment column
            residue_count = 0
            alignment_column = None

            for i, residue in enumerate(aligned_reference):
                if residue != "-":
                    residue_count += 1

                if residue_count == position and residue != "-":
                    alignment_column = i
                    break

            if alignment_column is None:
                st.error("Could not map the residue to the alignment.")
                st.stop()

            # Compare the original residue across sequences
            observed = []

            for name, aligned_seq in records.items():
                residue = aligned_seq[alignment_column]

                if residue != "-":
                    observed.append(residue)

            same_count = sum(
                residue == original_aa
                for residue in observed
            )

            total_count = len(observed)

            conservation = (
                100 * same_count / total_count
                if total_count else 0
            )

            st.metric(
                "Reference-residue conservation",
                f"{conservation:.1f}%"
            )

            st.write(
                f"Alignment column: {alignment_column + 1}"
            )

            st.write(
                f"Sequences with a residue at this position: "
                f"{total_count}"
            )

            st.write(
                f"Sequences containing {original_aa} at this "
                f"column: {same_count}"
            )

            st.write(
                "Residues at the aligned position:"
            )

            st.code(
                "\n".join(
                    f"{name}: {seq[alignment_column]}"
                    for name, seq in records.items()
                )
            )

            st.caption(
                "This is the percentage retaining the original "
                "amino acid at the aligned position, excluding "
                "gaps. It is a simple conservation measure, not "
                "a validated pathogenicity prediction."
            )

        except ValueError as error:
            st.error(str(error))

    st.subheader("5. Biological references")

    st.markdown(
        f"[View protein in UniProt]"
        f"(https://www.uniprot.org/uniprotkb/{accession})"
    )

    st.markdown(
        "[Search ClinVar]"
        f"(https://www.ncbi.nlm.nih.gov/clinvar/?term={mutation})"
    )

    st.warning(
        "Conservation can suggest biological importance, "
        "but does not by itself establish whether a mutation "
        "causes disease."
    )

# STEP 12: Protein Structure Explorer

st.header("🧬 Protein Structure Explorer")

st.write(
    "Search for available 3D protein structures "
    "using the UniProt accession entered above."
)

if st.button("Find Protein Structures"):

    search_url = (
        "https://search.rcsb.org/rcsbsearch/v2/query"
    )

    query = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute":
                    "rcsb_polymer_entity_container_identifiers."
                    "reference_sequence_identifiers.database_accession",
                "operator": "exact_match",
                "value": accession
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 10
            }
        }
    }

    try:
        response = requests.post(
            search_url,
            json=query,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("result_set", [])

        if results:
            st.success(
                f"Found {len(results)} matching structure "
                "entries in the first search results."
            )

            for item in results:
                pdb_id = item["identifier"]

                st.markdown(
                    f"**PDB ID: {pdb_id}**"
                )

                st.markdown(
                    f"[View structure on RCSB PDB]"
                    f"(https://www.rcsb.org/structure/{pdb_id})"
                )

                st.markdown(
                    f"[Open 3D structure viewer]"
                    f"(https://molstar.org/viewer/?pdb={pdb_id})"
                )

                st.divider()

        else:
            st.warning(
                "No matching PDB entries were found. "
                "This does not necessarily mean that no "
                "predicted structure exists."
            )

    except requests.exceptions.RequestException as error:
        st.error(
            "Unable to retrieve structure information. "
            "Please check your internet connection and try again."
        )


# STEP 13: Clinical Evidence Explorer

from urllib.parse import quote

st.header("🔬 Clinical Evidence Explorer")

st.write(
    "Search ClinVar for clinical records related to "
    "your protein or gene."
)

if st.button("Search Clinical Evidence"):

    search_url = "https://www.ncbi.nlm.nih.gov/clinvar/"

    # Open a valid ClinVar search page
    clinvar_url = (
        search_url + "?term=" + quote(accession, safe="")
    )

    st.success("Your ClinVar search link is ready.")

    st.markdown(
        f"[Open ClinVar search results for {accession}]"
        f"({clinvar_url})"
    )

    st.info(
        "This searches using the protein accession. "
        "The results may not represent your exact mutation."
    )


# STEP 14: Mutation Impact Summary

st.header("📊 Mutation Impact Summary")

st.write(
    "Review your mutation details and supporting evidence."
)

if st.button("Generate Mutation Report"):

    # Recalculate mutation details when the report button is clicked
    match = re.fullmatch(
        r"([ACDEFGHIKLMNPQRSTVWY])(\d+)([ACDEFGHIKLMNPQRSTVWY])",
        mutation.strip().upper()
    )

    if not match:
        st.error(
            "Enter a mutation in the format E7V, "
            "with a reference amino acid, position, "
            "and substituted amino acid."
        )

    else:
        original_aa = match.group(1)
        position = int(match.group(2))
        new_aa = match.group(3)

        # Retrieve the reference protein sequence
        try:
            response = requests.get(
                f"https://rest.uniprot.org/uniprotkb/{accession}.fasta",
                timeout=20
            )
            response.raise_for_status()

            sequence = "".join(
                line.strip()
                for line in response.text.splitlines()
                if not line.startswith(">")
            )

            if position < 1 or position > len(sequence):
                st.error(
                    f"Position {position} is outside the "
                    f"protein sequence length of {len(sequence)}."
                )

            elif sequence[position - 1] != original_aa:
                st.error(
                    f"Reference mismatch: position {position} "
                    f"contains {sequence[position - 1]}, "
                    f"not {original_aa}. Check the accession "
                    "and mutation."
                )

            else:
                st.subheader("Mutation Details")

                col1, col2, col3 = st.columns(3)

                col1.metric("Position", position)
                col2.metric("Reference amino acid", original_aa)
                col3.metric("Substituted amino acid", new_aa)

                st.write(
                    f"**Mutation:** {original_aa}{position}{new_aa}"
                )
                st.write(f"**UniProt accession:** {accession}")

                st.subheader("Evidence Links")

                st.markdown(
                    f"[View protein on UniProt]"
                    f"(https://www.uniprot.org/uniprotkb/{accession}/entry)"
                )

                st.markdown(
                    f"[Search structures on RCSB PDB]"
                    f"(https://www.rcsb.org/search?query={accession})"
                )

                st.markdown(
                    f"[Search ClinVar]"
                    f"(https://www.ncbi.nlm.nih.gov/clinvar/?term={accession})"
                )

                st.info(
                    "This report validates the sequence substitution "
                    "and provides evidence links. It does not establish "
                    "whether the mutation causes disease."
                )

        except requests.exceptions.RequestException:
            st.error(
                "Could not retrieve the protein sequence. "
                "Check your internet connection and accession."
            )
