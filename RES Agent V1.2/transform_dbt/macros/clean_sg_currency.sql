{# transform_dbt/macros/clean_sg_currency.sql #}

{% macro clean_sg_currency(column_name) %}
    {# 
       Removes currency symbols ($), commas, and whitespace,
       then casts the remaining string to a float for math operations. 
    #}
    CAST(
        REGEXP_REPLACE(
            CAST({{ column_name }} AS STRING), 
            '[$,\\s]', 
            ''
        ) AS FLOAT64
    )
{% endmacro %}