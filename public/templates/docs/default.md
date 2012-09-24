Adding Documentation
--------------------

1. Create a new documentation template with the same name as your HTML file but with
the extension `.md`. By default, this will be saved in the `templates/docs` folder.
For example, if your document is called `mydoc.html`, create a new documentation
template called `mydoc.md`.

2. Write your documentation using the Markdown language.
See the [Markdown web page][mwp] for more information.

3. You can preview your Markdown page from the editor by clicking the link above the edit pane.

4. The default width of the docs panel is 350px. To make it wider, add a style
element to your HTML template after the "rascal-head" include:

        {% include "include/rascal-head.html" %}
        <style>
            .doc-panel {
                width: 500px;
            }
        </style>

[mwp]: http://daringfireball.net/projects/markdown/
