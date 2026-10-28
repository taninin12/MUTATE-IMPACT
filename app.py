
import re
import requests
import streamlit as st

# 1. Configure the website
st.set_page_config(
    page_title="Mutation Impact Explorer",
    page_icon="🧬",
    layout="wide"
)

# 2. Website heading
st.title("🧬 Mutation Impact Explorer")

st.write(
    "Explore how an amino acid mutation changes "
    "a protein sequence."
)

st.caption(
    "A simple bioinformatics tool for exploring "
    "protein variants."
)

# 3. Collect user input
accession = st.text_input(
    "Enter UniProt accession",
    value="P68871"
).strip()

mutation = st.text_input(
    "Enter mutation (example: E7V)",
    value="E7V"
).strip().upper()

# 4. Analyze when the button is clicked
if st.button("Analyze Mutation", type="primary"):

    # Check accession format
    if not re.fullmatch(r"[A-Za-z0-9]+", accession):
        st.error("Please enter a valid-looking accession.")
        st.stop()

    # Check mutation format
    pattern = r"([ACDEFGHIKLMNPQRSTVWY])(\d+)([ACDEFGHIKLMNPQRSTVWY])"

    match = re.fullmatch(pattern, mutation)

    if not match:
        st.error(
            "Invalid mutation format. Use an example "
            "like E7V: original amino acid, position, "
            "new amino acid."
        )
        st.stop()

    original_aa = match.group(1)
    position = int(match.group(2))
    new_aa = match.group(3)

    if position < 1:
        st.error("Position must be at least 1.")
        st.stop()

    if original_aa == new_aa:
        st.error(
            "The original and new amino acids must differ."
        )
        st.stop()

    # 5. Retrieve the protein from UniProt
    url = (
        "https://rest.uniprot.org/uniprotkb/"
        + accession + ".fasta"
    )

    try:
        with st.spinner("Fetching protein sequence..."):
            response = requests.get(url, timeout=20)
            response.raise_for_status()

        # FASTA format: first line is the header.
        lines = response.text.splitlines()

        sequence = "".join(
            line.strip()
            for line in lines
            if line and not line.startswith(">")
        ).upper()

        if not sequence:
            st.error("No protein sequence was returned.")
            st.stop()

    except requests.RequestException:
        st.error(
            "Could not retrieve the protein. Check your "
            "internet connection and UniProt accession."
        )
        st.stop()

    # 6. Validate the selected position
    if position > len(sequence):
        st.error(
            f"The protein contains {len(sequence)} "
            "amino acids. Your position is too large."
        )
        st.stop()

    actual_aa = sequence[position - 1]

    if actual_aa != original_aa:
        st.error(
            f"Mutation mismatch! Position {position} "
            f"contains {actual_aa}, not {original_aa}. "
            "Check the reference sequence and numbering."
        )
        st.stop()

    # 7. Create the mutated protein sequence
    mutated_sequence = (
        sequence[:position - 1]
        + new_aa
        + sequence[position:]
    )

    st.success("Mutation analyzed successfully!")

    # 8. Display basic results
    col1, col2, col3 = st.columns(3)

    col1.metric("Protein length", f"{len(sequence)} aa")
    col2.metric("Mutation position", position)
    col3.metric(
        "Amino acid change",
        f"{original_aa} → {new_aa}"
    )

    st.subheader("Mutation details")

    st.write(f"**UniProt accession:** {accession}")
    st.write(f"**Mutation:** {mutation}")
    st.write(f"**Reference amino acid:** {actual_aa}")
    st.write(f"**New amino acid:** {new_aa}")

    # 9. Display a small region around the mutation
    start = max(0, position - 11)
    end = min(len(sequence), position + 10)

    ref_region = sequence[start:end]
    mut_region = mutated_sequence[start:end]

    offset = position - 1 - start

    ref_display = (
        ref_region[:offset]
        + "[" + ref_region[offset] + "]"
        + ref_region[offset + 1:]
    )

    mut_display = (
        mut_region[:offset]
        + "[" + mut_region[offset] + "]"
        + mut_region[offset + 1:]
    )

    st.subheader("Reference vs mutated sequence")

    st.write(
        f"Showing residues {start + 1} to {end}. "
        "Square brackets mark the changed position."
    )

    st.code(
        f"Reference: {ref_display}\n"
        f"Mutated:   {mut_display}"
    )

    # 10. Show the complete sequences
    with st.expander("View complete reference sequence"):
        st.code(sequence)

    with st.expander("View complete mutated sequence"):
        st.code(mutated_sequence)

    # 11. Provide database links
    st.subheader("Explore biological evidence")

    st.markdown(
        f"[Open protein record in UniProt]"
        f"(https://www.uniprot.org/uniprotkb/{accession})"
    )

    st.markdown(
        f"[Search ClinVar for {mutation}]"
        f"(https://www.ncbi.nlm.nih.gov/clinvar/"
        f"?term={mutation})"
    )

    st.warning(
        "A sequence change does not by itself prove that "
        "a variant causes disease. Clinical evidence, "
        "conservation and structural information are "
        "needed for further interpretation."
    )
