{% macro camel_to_snake(column_name) %}
    {% set result = namespace(value='') %}
    {% for char in column_name %}
        {% if loop.index0 > 0 and char.isupper() %}
            {% set result.value = result.value ~ '_' ~ char.lower() %}
        {% else %}
            {% set result.value = result.value ~ char.lower() %}
        {% endif %}
    {% endfor %}
    {{ return(result.value) }}
{% endmacro %}
