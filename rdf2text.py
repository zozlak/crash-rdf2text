
# Tests to process RDF to text in preparation for CRASH hackaton in Graz 2026

# Naomi Nota 2026-10-27

# Use of collection etmira: https://arche.acdh.oeaw.ac.at/crash/
# Ontologie structure: https://arche.acdh.oeaw.ac.at/browser/api/rootTable/en?_format=html
# More information on package RDFlib: https://github.com/RDFLib/rdflib

# Etmira's .nt file contains:
# - URLs wrapped in Markdown
# - RDF resources as objects represented with quoted strings such as ^^<URI> instead of N-Triples URI syntax
# - Other datatypes like ^^<GEOM>
#
# Need to change the file before being able to load it in RDFlib.


## Read and inspect files

# Install packages (in bash):
# uv add rdflib matplotlib seaborn python-dateutil

# Standard library
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote, urlparse
import dateutil.parser

# RDF processing
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns


# Read command-line arguments
if len(sys.argv) != 3:
    print("Usage: uv run rdf2text.py input.nt output.txt")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]


# Preprocess the file to convert into N-Triples syntax
with open(input_file, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []
for line in lines:
    # Convert "URL"^^<URI> to <URL>
    cleaned_line = re.sub(r'"(https?://[^"]+)"\^\^<URI>', r'<\1>', line)

    # Convert "GEOM"^^<GEOM> to standard string literal "GEOM" to make it readable N-Triples
    cleaned_line = re.sub(r'\^\^<GEOM>', '', cleaned_line)

    cleaned_lines.append(cleaned_line)


# Parse the cleaned file
g = Graph()
g.parse(data="".join(cleaned_lines), format="nt")

print(f"Number of triples: {len(g):,}")


# Inspect triples
for i, triple in enumerate(g):
    print(triple)
    if i == 9:
        break


# Count resources by type
types = Counter(
    str(obj)
    for subject, obj in g.subject_objects(RDF.type)
)

for resource_type, count in types.most_common(20):
    print(f"{count:>6}  {resource_type}") # Right align printed nr with min value of 6 characters


# Initialize counters
subjects = Counter()
predicates = Counter()
objects = Counter()

# Count
for s, p, o in g:
    subjects[str(s)] += 1
    predicates[str(p)] += 1
    objects[str(o)] += 1


# Get impression of data
print("=== TOP 10 MOST COMMON SUBJECTS ===")
for item, count in subjects.most_common(10):
    print(f"{count:>6}  {item}")

print("\n=== TOP 10 MOST COMMON PREDICATES ===")
for item, count in predicates.most_common(10):
    print(f"{count:>6}  {item}")

print("\n=== TOP 10 MOST COMMON OBJECTS ===")
for item, count in objects.most_common(10):
    print(f"{count:>6}  {item}")


# Extract predicates in descending order of occurrence
all_predicates = predicates.most_common()

names = [
    item[0].split('#')[-1] if '#' in item[0]
    else item[0].split('/')[-1]
    for item in all_predicates
]

counts = [item[1] for item in all_predicates]


# Set style
sns.set_theme(style="whitegrid")

# Dynamically size the figure height based on the number of unique predicates
fig, ax = plt.subplots(figsize=(10, max(6, len(names) * 0.4)))

# Create horizontal bar plot
sns.barplot(
    x=counts,
    y=names,
    hue=names,
    palette="viridis",
    legend=False,
    ax=ax
)

# Labeling and titles
ax.set_title(
    "Distribution of all predicates in ETMIRA collection",
    fontsize=14,
    pad=15
)

ax.set_xlabel("Occurrence Count", fontsize=12)
ax.set_ylabel("Predicate", fontsize=12)

plt.tight_layout()
plt.show()


# Print
for predicate, count in predicates.most_common():
    name = predicate.rstrip("/#").split("/")[-1].split("#")[-1]
    print(f"{count:>6}  {name}")


## Wrangle data to make it more readable

# Namespaces and definition of helpers

DC_TITLE = URIRef("http://purl.org/dc/elements/1.1/title")

LABEL_PREDICATES = {
    str(RDFS.label),
    str(SKOS.prefLabel),
    str(DCTERMS.title),
    str(DC_TITLE),
}


def local_name(term):
    """Get the local name from a predicate or URI."""
    text = str(term).rstrip("/#")
    return re.split(r"[/#]", text)[-1].split(":")[-1]


def readable_predicate(predicate):
    """
    Convert a predicate URI or name into a human-readable phrase.
    """
    name = local_name(predicate)

    # Separate camelCase and PascalCase words
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)

    # Replace underscores and hyphens with spaces
    name = name.replace("_", " ").replace("-", " ")

    # Separate common RDF property prefixes
    name = re.sub(r"^(has|is)(?=[A-Z])", r"\1 ", name)

    return " ".join(name.split()).lower()


def clean_text(value):
    """Clean display text without changing RDF graph."""
    return str(value).strip()


def format_friendly_date(date_str):
    """Format ISO timestamps into friendly readable dates without losing data."""
    try:
        dt = dateutil.parser.isoparse(date_str)

        # If time is present and non-zero
        if dt.hour or dt.minute or dt.second:
            return dt.strftime("%B %d, %Y at %I:%M %p")

        return dt.strftime("%B %d, %Y")

    except Exception:
        return date_str


def uri_fallback(uri):
    """Use a useful URI identifier when there is no label."""
    parsed = urlparse(str(uri))

    segments = [
        part
        for part in unquote(parsed.path).strip("/").split("/")
        if part
    ]

    if not segments:
        return str(uri)

    generic_segments = {"api", "rest", "resource", "resources"}

    if segments[-1].lower() in generic_segments:
        return str(uri)

    if (
        len(segments) > 1
        and segments[-2].lower() in generic_segments
    ):
        return segments[-1]

    return segments[-1]


# Index predicates by full URI and local name.
properties = defaultdict(list)

for s, p, o in g:
    full_uri = str(p).lower()
    short_name = local_name(p).lower()

    properties[(s, full_uri)].append(o)
    properties[(s, short_name)].append(o)


# Resolve labels for linked resources

# Cache labels so repeated resources are only resolved once
LABEL_CACHE = {}


def resource_label(term):
    """Resolve a resource label and cache the result."""

    if term in LABEL_CACHE:
        return LABEL_CACHE[term]

    result = _resolve_resource_label(term, depth=0, visited=set())

    LABEL_CACHE[term] = result
    return result


def _resolve_resource_label(term, depth=0, visited=None):
    """
    Prefer graph labels and titles.
    Fall back to a URI identifier.
    """

    if isinstance(term, Literal):
        return clean_text(term)

    if isinstance(term, BNode):
        return f"blank node {term}"

    if not isinstance(term, URIRef):
        return str(term)

    if visited is None:
        visited = set()

    if term in visited or depth >= 5:
        return uri_fallback(term)

    visited = visited | {term}

    preferred = (
        "preflabel",
        "label",
        "title",
        "hastitle",
        "hasalternativetitle",
        "name",
    )

    # Use the existing properties index instead of searching the graph
    for name in preferred:
        for obj in properties.get((term, name), []):
            if isinstance(obj, Literal) and clean_text(obj):
                return clean_text(obj)

    # Some graphs link to separate title or filename resources
    for name in ("hastitle", "hasalternativetitle", "hasfilename"):
        for obj in properties.get((term, name), []):

            if isinstance(obj, Literal) and clean_text(obj):
                return clean_text(obj)

            if isinstance(obj, URIRef):
                label = _resolve_resource_label(
                    obj, depth + 1, visited
                )

                if label != uri_fallback(obj):
                    return label

    return uri_fallback(term)


def readable_value(term):
    """Make values readable."""
    if isinstance(term, (URIRef, BNode)):
        return resource_label(term)

    return clean_text(term)


def get_values(subject, *names):
    """Get distinct readable values for selected predicates."""
    result = []

    for name in names:
        for obj in properties.get((subject, name.lower()), []):
            value = readable_value(obj)

            if value and value not in result:
                result.append(value)

    return result


def get_first(subject, *names):
    found = get_values(subject, *names)
    return found[0] if found else None


# Generate a natural-language description per triple

def describe_triple(subject, predicate, obj):
    subject_name = resource_label(subject)
    object_name = readable_value(obj)

    pred = local_name(predicate).lower()

    # RDF type information
    if predicate == RDF.type:
        sentence = f"{subject_name} is classified as a {object_name}"

    # Resource relationships
    elif pred == "ispartof":
        sentence = f"{subject_name} is part of {object_name}"

    elif pred == "haspart":
        sentence = f"{subject_name} contains {object_name}"

    elif pred == "relation":
        sentence = f"{subject_name} is related to {object_name}"

    elif pred == "source":
        sentence = f"{subject_name} originates from the source {object_name}"

    elif pred == "ismemberof":
        sentence = f"{subject_name} is a member of {object_name}"

    elif pred == "istitleimageof":
        sentence = f"{subject_name} serves as the title image for {object_name}"

    # People and responsibilities
    elif pred in {"createdby", "hascreator", "creator"}:
        sentence = f"{subject_name} was created by {object_name}"

    elif pred == "hasdepositor":
        sentence = f"{subject_name} was deposited by {object_name}"

    elif pred == "hasmetadatacreator":
        sentence = f"The metadata for {subject_name} was created by {object_name}"

    elif pred in {"hasupdatedrole", "hasbinaryupdatedrole"}:
        role = (
            "binary updates"
            if pred == "hasbinaryupdatedrole"
            else "updates"
        )

        sentence = f"{object_name} is responsible for {role} on {subject_name}"

    elif pred == "hasowner":
        sentence = f"{subject_name} is owned by {object_name}"

    elif pred in {
        "hasdigitisingagent",
        "hascurator",
        "haseditor",
        "hasfunder",
        "hasprincipalinvestigator",
        "hascontact",
    }:
        roles = {
            "hasdigitisingagent": "digitising agent",
            "hascurator": "curator",
            "haseditor": "editor",
            "hasfunder": "funder",
            "hasprincipalinvestigator": "principal investigator",
            "hascontact": "contact person",
        }

        sentence = f"{subject_name} lists {object_name} as its {roles[pred]}"

    # Titles, filenames and identifiers
    elif pred in {"hastitle", "title"}:
        sentence = f"{subject_name} is titled \"{object_name}\""

    elif pred == "hasalternativetitle":
        sentence = f"{subject_name} is also known as \"{object_name}\""

    elif pred in {"hasfilename", "filename"}:
        sentence = f"{subject_name} is saved under the filename \"{object_name}\""

    elif pred in {"hasidentifier", "identifier"}:
        sentence = f"{subject_name} has the identifier {object_name}"

    elif pred == "hasnonlinkedidentifier":
        sentence = f"{subject_name} has the non-linked identifier {object_name}"

    elif pred in {"haspid", "haspersistentidentifier"}:
        sentence = f"{subject_name} has the persistent identifier {object_name}"

    # Dates, version and status
    elif pred == "hasupdateddate":
        friendly_date = format_friendly_date(object_name)
        sentence = f"{subject_name} was last updated on {friendly_date}"

    elif pred == "hasbinaryupdateddate":
        friendly_date = format_friendly_date(object_name)
        sentence = f"The binary file for {subject_name} was last updated on {friendly_date}"

    elif pred == "hasavailabledate":
        friendly_date = format_friendly_date(object_name)
        sentence = f"{subject_name} became available on {friendly_date}"

    elif pred in {"created", "modified"}:
        friendly_date = format_friendly_date(object_name)
        action = "created" if pred == "created" else "modified"
        sentence = f"{subject_name} was {action} on {friendly_date}"

    elif pred == "hasversion":
        sentence = f"{subject_name} is on version {object_name}"

    elif pred == "haslifecyclestatus":
        sentence = f"{subject_name} has a lifecycle status of {object_name}"

    # Technical and digital-file metadata
    elif pred == "hasformat":
        sentence = f"{subject_name} is formatted as {object_name}"

    elif pred == "haslanguage":
        sentence = f"{subject_name} is in the language {object_name}"

    elif pred in {"hasrawbinarysize", "hasbinarysize"}:
        label = (
            "raw binary size"
            if pred == "hasrawbinarysize"
            else "binary size"
        )

        sentence = f"{subject_name} has a {label} of {object_name} bytes"

    elif pred == "hassize":
        sentence = f"{subject_name} has a size of {object_name}"

    elif pred == "haspixelwidth":
        sentence = f"{subject_name} has a width of {object_name} pixels"

    elif pred == "haspixelheight":
        sentence = f"{subject_name} has a height of {object_name} pixels"

    elif pred == "hasnumberofitems":
        sentence = f"{subject_name} consists of {object_name} items"

    elif pred == "hashash":
        sentence = f"{subject_name} has the hash value {object_name}"

    elif pred == "hashosting":
        sentence = f"{subject_name} is hosted by {object_name}"

    elif pred == "hascategory":
        sentence = f"{subject_name} falls under the category of {object_name}"

    elif pred == "hastag":
        sentence = f"{subject_name} is tagged with \"{object_name}\""

    elif pred == "hasusedhardware":
        sentence = f"{subject_name} was captured using the hardware: {object_name}"

    elif pred == "hasusedsoftware":
        sentence = f"{subject_name} was processed using the software: {object_name}"

    elif pred == "hasappliedmethod":
        sentence = f"{subject_name} had the following method applied: {object_name}"

    elif pred == "hasarrangement":
        sentence = f"{subject_name} is arranged in {object_name} order"

    # Rights and access
    elif pred == "haslicensor":
        sentence = f"{subject_name} is licensed by {object_name}"

    elif pred == "hasrightsholder":
        sentence = f"{subject_name} has its rights held by {object_name}"

    elif pred in {"hasrightsinformation", "hasrightsinfo"}:
        sentence = f"{subject_name} is subject to the rights information: {object_name}"

    elif pred == "haslicense":
        sentence = f"{subject_name} is distributed under the license {object_name}"

    elif pred == "haslicensesummary":
        sentence = f"{subject_name} has the following license summary: {object_name}"

    elif pred in {"hasaccessrestriction", "hasaccessrestrictionsummary"}:
        sentence = f"{subject_name} has the access restriction: {object_name}"

    elif pred == "aclread":
        sentence = (
            f"{object_name} has permission to view the resource "
            f"{subject_name}"
        )

    elif pred == "aclwrite":
        sentence = (
            f"{object_name} has permission to modify the resource "
            f"{subject_name}"
        )

    # Descriptive metadata
    elif pred == "hasdescription":
        sentence = f"{subject_name} is described as: {object_name}"

    elif pred == "hasmetadata":
        sentence = f"{subject_name} is associated with the metadata: {object_name}"

    elif pred == "hassubject":
        sentence = f"{subject_name} is about the subject {object_name}"

    # Location and address
    elif pred in {
        "hascity",
        "hasregion",
        "hascountry",
        "haspostcode",
        "hasaddressline1",
        "hasaddressline2",
    }:
        labels = {
            "hascity": "city",
            "hasregion": "region",
            "hascountry": "country",
            "haspostcode": "postcode",
            "hasaddressline1": "address line 1",
            "hasaddressline2": "address line 2",
        }

        sentence = f"{subject_name} records its {labels[pred]} as {object_name}"

    # Web links and catalogue sets
    elif pred == "hasurl":
        sentence = (
            f"{subject_name} is linked to the web address "
            f"{clean_text(obj)}"
        )

    elif pred == "hasoaiset":
        sentence = (
            f"{subject_name} is indexed in the "
            f"Open Archives Initiative (OAI) metadata set \"{object_name}\""
        )

    # SKOS vocabulary and concept relationships
    elif pred in {"preflabel", "altlabel"}:
        label = (
            "preferred label"
            if pred == "preflabel"
            else "alternative label"
        )

        sentence = f"{subject_name} has the {label} \"{object_name}\""

    elif pred == "definition":
        sentence = f"{subject_name} is defined as: {object_name}"

    elif pred == "inscheme":
        sentence = f"{subject_name} belongs to the concept scheme {object_name}"

    elif pred == "topconceptof":
        sentence = f"{subject_name} is a top concept of {object_name}"

    elif pred == "broader":
        sentence = f"{subject_name} is a narrower concept than {object_name}"

    elif pred == "narrower":
        sentence = f"{subject_name} is a broader concept than {object_name}"

    elif pred == "notation":
        sentence = f"{subject_name} has the notation {object_name}"

    elif pred == "hasrelateddiscipline":
        sentence = f"{subject_name} is associated with the discipline {object_name}"

    # Spatial metadata
    elif pred == "haswkt":
        sentence = (
            f"{subject_name} has geographical data in "
            f"WKT format: {object_name}"
        )

    elif pred == "haslatitude":
        sentence = f"{subject_name} is located at latitude {object_name}"

    elif pred == "haslongitude":
        sentence = f"{subject_name} is located at longitude {object_name}"

    elif pred == "hasspatialcoverage":
        sentence = f"{subject_name} has spatial coverage spanning {object_name}"

    # Generic fallback for any other predicate
    else:
        predicate_name = readable_predicate(predicate)

        sentence = (
            f"{subject_name} has the recorded property "
            f"'{predicate_name}' with the value {object_name}"
        )

    sentence = sentence.strip()

    if sentence and sentence[-1] not in ".!?":
        sentence += "."

    return sentence


# Export every triple as one human-readable sentence

assert len(g) > 0, "The RDF graph contains no triples."

with open(output_file, "w", encoding="utf-8") as outfile:

    for subject, predicate, obj in g:
        sentence = describe_triple(subject, predicate, obj)
        outfile.write(sentence + "\n")


print(f"Exported {len(g):,} sentences to {output_file}")
