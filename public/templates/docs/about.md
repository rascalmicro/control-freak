About Rascal Documentation
==========================

When a file extension is `.md`, Rascal renders it with a Markdown processor.

Markdown is a text-to-HTML conversion tool which allows you to write in plain text format
and automatically converts it to valid HTML. Text is formatted using a simple syntax,
summarised below but best learned from the [Markdown web site][mwp]. When the text is viewed
in a web browser, Rascal renders it using the [markdown2][md2] tool written in Python.

If you have upgraded to Beriberi or later from an older version of the Rascal software, you may need to
install the markdown2 processor. Log into your Rascal using SSH and from the command line type:

    pip install markdown2

When you view a Markdown page in a web browser, Rascal renders the Markdown into the template
`markdown.html`. You can edit this template in any way you like, provided that you retain
the following [Jinja2][jj2] expressions and variable:

    {% autoescape false %}
        {{markdown}}
    {% endautoescape %}

For example, you might want to edit `markdown.html` change the default style.

--
Markdown Cheat Sheet
--------------------
It is best to view this section both in the editor to see the Markdown source and in a web browser
to see the rendered result.

### Formatted Text
The subtitle above begins with `###` which generates an `<h3>` tag
##### Beginning a line with `#####` generates an `<h5>` tag

Separate paragraphs with a blank line.

Nullam quis risus eget urna mollis ornare vel eu leo.
Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
Nullam id dolor id nibh ultricies vehicula.

Enclose a word or phrase with a single `_` for _italic_ and double `**` for **bold**.
You can also use `*` for _italic_ and `__` for __bold__.

*These can be combined to put **bold words** in an italic sentence* (or vice versa).

### Lists
You can create unordered lists:

* Apples
* Pears
* Berries
    * Raspberries
    * Strawberries

or ordered lists:

1. One potato
2. Two potatoes
3. Three potatoes
4. Four

### Block Quotes
Begin block quotes with the greater than character `>`:

> Are you sitting comfortably?
> Then I'll begin.

### Links and Images
Here is a link to [google](http://www.google.com/)

Here is an image of a LED ![LED](/static/images/led.gif)

### Code Examples
You can include a block of code by indenting with four spaces.
The following example shows the code that renders this page:

    @public.route('/docs/<doc_name>.md')
    def document_docs(doc_name):
        return render_markdown('docs/', doc_name)
    
    def render_markdown(path, doc_name):
        import markdown2
        with open('/var/www/public/templates/' + path + doc_name + '.md', 'r') as mdf:
            return render_template('markdown.html', title=doc_name, markdown=markdown2.markdown(mdf.read()))
        return 'Not Found', 404

### Further Reading
The definitive source for all things Markdown is the [Markdown web site][mwp].

[mwp]: http://daringfireball.net/projects/markdown/
[md2]: https://github.com/trentm/python-markdown2
[jj2]: http://jinja.pocoo.org/docs/templates/
