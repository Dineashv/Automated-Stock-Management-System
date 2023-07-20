import imgkit

# Set the options for rendering the HTML page to an image
options = {
    'format': 'png',
    'width': '1500',
    'height': '800'
}

# Render the HTML page to a PNG image
imgkit.from_file('templates\summa.html', 'out.png', options=options)
