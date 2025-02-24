### Behavior Session

#### Records
{% filter indent(width=0) %}
{{ tables[0] | render_table(environment) }}
{% endfilter %}

#### Parameters
{% filter indent(width=0) %}
{{ tables[1] | render_table(environment) }}
{% endfilter %}

#### Processing

##### PDF
{{ documents[0] | render_links(6) }}

##### Notebook
{{ files[0] | render_links(6) }}

#### Notes
None
