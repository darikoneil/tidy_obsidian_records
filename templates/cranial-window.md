## Cranial Window

### Records
{% filter indent(width=0) %}
{{ tables[0] | render_table(environment) }}
{% endfilter %}

### Surgical Sheet
{{ documents[0] | render_links }}

### Robot File
{{ documents[1] | render_links }}

### Axial View
{{ images[0] | render_links }}

### Coronal View
{{ images[1] | render_links }}

### Notes
None
