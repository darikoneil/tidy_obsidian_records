### Imaging Session
{% call_function imaging_meta_file = 'get_imaging_meta_file' %}
{% call_function landmark_meta_file = 'get_landmark_meta_file' %}
{% set planes_proj = images[0] %}

#### Session
{% filter indent(width=0) %}
{{ tables[0] | render_table(environment)}}
{% endfilter %}

#### Records
{% filter indent(width=0) %}
{{ special[0] | special_imaging_fov(imaging_meta_file, environment) }}
{% endfilter %}

#### Expression

##### PDF
{{ documents[0] | render_links(6)}}

##### Notebook
{{ files[0] | render_links(6)}}

#### Fields of View
{% for plane in range(planes_slm|length) %}

###### Z-Projection (STD)
{{ planes_proj[plane] | render_links(5)}}
{% endfor %}

#### Landmarks

##### Records
{% filter indent(width=0) %}
{{ special[0] | special_imaging_fov(landmark_meta_file, environment) }}
{% endfilter %}

##### Landmark Projections
{{ images[1] | render_links(6)}}

#### Notes
None
