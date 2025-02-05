pip install -r theme_common/requirements.txt
python theme_common/scripts/combine_theme_resources.py -s theme_common/resources -ov theme_override/resources -o dist/_theme
python theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml
