# This script is meant to be used for pull request builds
pip install -r theme_common/requirements.txt
python theme_common/scripts/combine_theme_resources.py -s theme_common/resources -ov theme_override/resources -o dist/_theme
# The next step is used to override resources for pull request builds - these overrides could as well have been put in the local theme_override folder, but this is a generic solution
python theme_common/scripts/combine_theme_resources.py -s theme_common/resources_pr_specific -ov theme_override/resources -o dist/_theme -skiprmtree
python theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml
