### Imaging Session
{% call_function imaging_meta_file = 'get_imaging_meta_file' %}
{% call function landmark_meta_file = 'get_landmark_meta_file' %}
{% set planes_slm = special[1] | special_multiplane_slm(environment) %}
{% set planes_slm = planes_slm | split_to_list %}
{% set planes_proj = images[0] %}
{% set num_planes = plane_slm | length %}

#### Session
{% filter indent(width=0) %}
{{ tables[0] }}
{% endfilter %}

##### Records
{% filter indent(width=0) %}
{{ special[0] | special_imaging_fov(imaging_meta_file, environment) }}
{% endfilter %}

#### Expression (PDF)
{{ documents[0] | render_links(5)}}

#### Expression (Notebook)
{{ files[0] | render_links(5)}}

#### Fields of View
{% for plane in range(num_planes) %}

###### Metadata
{% filter indent(width=0) %}
{{ planes_slm[plane] }}
{% endfilter %}

###### Projection
{{ planes_proj[plane] | render_links(6)}}
{% endfor %}

#### Landmarks

##### Records
{% filter indent(width=0) %}
{{ special[0] | special_imaging_fov(landmark_meta_file, environment) }}
{% endfilter %}

##### Landmark Projections
{{ images[1] }}

#### Roadmap
{% filter indent(width=0) %}
#{{ special[2] | special_imaging_roadmap(imaging_meta_file, landmark_meta_file, environment) }}
{% endfilter %}

#### Notes
None
