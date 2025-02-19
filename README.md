# tidy_obsidian_records
Generates tidy records that are rendered prettily in obsidian. Requires Python >= 3.10.

## Usage
Note: generating records may invoke a popup to manually fill out a table. For records that relate to PrairieView, you can simply press submit immediately, and a pop-up will appear to select the experiment's prairieview meta-files. These will be parsed and used to automatically fill the tables.

### Command Line
```
records key subject
```

### Python
```
from pathlib import Path
from records import generate_records

# key identifying the template for these records
key = "experiment-records"

# experimental subject or other specific identifier
subject = "subject one"

# directory containing templates
template_directory = Path.cwd().joinpath("templates")

# directory to export records to
exports_directory = Path.cwd().joinpath("exports")

generate_records(key,
                 subject,
                 template_directory, 
                 exports_directory)
```

### Exports
The exported records are placed in a new directory named after the subject in the 
exports directory The exported records are in the form of a single markdown file 
(named after the template key and subject) and a second supporting directory `/files`.
The folder can be copied directly to your obsidian vault. The contents of the markdown 
can also be pasted into an existing obsidian note provided the associated `files` folder
is also copied to the vault.

## Records Templates:
Records templates are composed of two components:
  1. Defined *placeholders* that will be filled on a per-experiment basis
  2. The *markdown file* containing static elements and placeholder locations.

Every record template is stored within the record template registry (`templates.json`)
using a unique `key`. Each entry contains lists of string
placeholders for documents, files, images, and tables, and the location of the markdown 
file.

For example, the following entry in `templates.json` defines a template for a generic
experiment record:
```
"experiment-records": {
  "key": "experiment-records",
  "documents": [
    "Pre-Experiment Outline",
    "Handwritten Notes"
  ],
  "files": [
    "Analysis Notebook"
  ],
  "images": [
    "Image of Workstation"
  ],
  "tables": [
    "experiment-metadata",
  ],
}
```

The four placeholder types are defined as follows:
- `documents`: a list of strings representing the descriptive names of .pdf files to render inline.
- `files`: a list of strings representing the descriptive names of files to render as links (arbitrary file types).
- `images`: a list of strings representing the descriptive names of image files to render inline. Any image type supported by Obsidian is supported. 
- `tables`: a list of strings representing the keys of table-types to render inline. 

The markdown file contains static elements like headers and free-form notes, and the 
locations in which the placeholders will be inserted using the jinja templating engine.

For example, the following markdown file is a template for a generic experiment record:
```
# Experiment Records

### Pre-Experiment Outline
{{ documents[0] }}

### Image of Workstation
{{ images[0] }}

### Handwritten Notes
{{ documents[1] }}

### Analysis Notebook
{{ files[0] }}

### Experiment Metadata
{% filter indent(width=0) %}
{{ tables[0] }}
{% endfilter %}
```


### Adding new records templates
To add a new record template, create a new markdown file in the `templates` directory.
Next, within python
```
from records import RecordsTemplate, RecordsTemplateRegistry

# unique key for the template AND the name of the markdown file
key = "experiment-records"

documents = ["Pre-Experiment Outline", "Handwritten Notes"]
files = ["Analysis Notebook", ]
images = ["Image of Workstation", ]
tables = ["experiment-metadata", ]

add_template(key,
             documents,
             files,
             images,
             tables)

```


### Adding new table templates
Currently need to add new tables in `tables.py`, but in future could simply
add a hook to register new tables from other files given their is a `TablesRegistry`
class which contains a classmethod to decorate other classes as tables.
