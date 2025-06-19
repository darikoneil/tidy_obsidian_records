# tidy_obsidian_records
Generates tidy records that are rendered prettily in obsidian. Requires Python >= 3.10.

## Usage

Note: Various templates require code from the code dump (e.g., ``slm-imaging`` requires the metadata loading functions from ``code_dump.imaging.slm``)
Note: For records that relate to PrairieView or the SLM control gui, a pop-up will appear to select the experiment's meta-files. These will be parsed and used to automatically fill the tables.

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
placeholders for documents, files, images, tables, 'special' tables (autofilled), and the location of the markdown 
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
    "experiment-metadata"
  ],
  "special": [
    "autofilled-table"
]
}
```

The five placeholder types are defined as follows:
- `documents`: a list of strings representing the descriptive names of .pdf files to render inline.
- `files`: a list of strings representing the descriptive names of files to render as links (arbitrary file types).
- `images`: a list of strings representing the descriptive names of image files to render inline. Any image type supported by Obsidian is supported. 
- `tables`: a list of strings representing the keys of table-types to render inline.
- `special`: a list of strings representing the keys of automatically-filled table-types to render inline.

The markdown file contains static elements like headers and free-form notes, and the 
locations in which the placeholders will be inserted using the jinja templating engine.

For example, the following markdown file is a template for a generic experiment record:
```
# Experiment Records

### Pre-Experiment Outline
{{ documents[0] | render_links}}

### Image of Workstation
{{ images[0] | render_links}}

### Handwritten Notes
{{ documents[1] | render_links}}

### Analysis Notebook
{{ files[0] | render_links}}

### Experiment Metadata
{% filter indent(width=0) %}
{{ tables[0] | render_table(environment)}}
{% endfilter %}

### Autofilled Table
{% call_function file_to_load = 'get_file_to_load' %} 
{% filter indent(width=0) %}
{{ tables[0] | special_autofill_table(file_to_load, environment) }}
{% endfilter %}
```

If multiple images/documents/files are provide for one placeholder, you can select the appropriate header level using `render_links(5)` where 5 is the header level.

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
special = ["autofilled-table", ]

add_template(key,
             documents,
             files,
             images,
             tables,
             special)

```


### Adding new table templates
Currently need to add new tables in `tables.py`, but in future could simply
add a hook to register new tables from other files given their is a `TablesRegistry`
class which contains a classmethod to decorate other classes as tables.

### Adding new autofill tables
Currently need to add the special function to the `FilterRegistry`

### Using generic functions
Generic functions (that return a value instead of operating on one) can be used through the `CallbackExtension`.
