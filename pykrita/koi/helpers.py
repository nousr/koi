from io import BytesIO

from krita import Krita, Selection
from PyQt5.QtCore import QBuffer, QIODevice, QByteArray
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMessageBox


def ERROR(title, details):
    msgBox = QMessageBox()
    msgBox.resize(500, 200)
    msgBox.setWindowTitle("Error")
    msgBox.setText(title)
    msgBox.setDetailedText(details)
    msgBox.setStyleSheet("QLabel{min-width: 700px;}")
    msgBox.exec()


def NOT_IMPLEMENTED():
    ERROR("Not Implemented", "This function is not implemented yet!")


def exists(x):
    return x is not None


def get_document():
    return Krita.instance().activeDocument()


def get_layer():
    """
    Get the active layer on the current document.
    """

    n = get_document().activeNode()
    return n if exists(n) else None


def get_selection():
    """
    Get the current selection from the user.
    """

    d = get_document()

    if not exists(d):
        return ERROR(
            "Please create a document.",
            "You must have a document active to make a selection.",
        )

    selection = d.selection()

    if not exists(selection):
        return ERROR(
            "Please make a selection",
            "Operation runs on a selection only. Please use rectangle select tool.",
        )

    if selection.width() > 512 or selection.height() > 512:
        return ERROR(
            "Please use smaller selection area.",
            "For simplicity 512x512px selections are the maximum currently supported.",
        )

    return selection


def make_selection():
    """
    Make a selection with the default 512x512 parameters.
    """

    document = get_document()

    if not exists(document):
        return ERROR(
            "No Document", "You must have an active document opened to use this tool."
        )

    current_selection = document.selection()

    X, Y = (
        (0, 0)
        if not exists(current_selection)
        else (current_selection.x(), current_selection.y())
    )

    new_selection = Selection()
    new_selection.select(X, Y, 512, 512, 255)

    document.setSelection(new_selection)


def selection_to_image(selection):
    """
    Get the current pixels from the selection.
    """

    # get current document
    doc = get_document()

    # get pixels from document on selection
    pixels = doc.pixelData(
        selection.x(), selection.y(), selection.width(), selection.height()
    )

    # create image from pixels
    image = QImage(
        pixels.data(), selection.width(), selection.height(), QImage.Format_RGBA8888
    ).rgbSwapped()

    return image


def layer_to_image(layer):
    """
    Turn a layer into an QImage
    """

    width, height = layer.width(), layer.height()
    return QImage(
        layer.pixelData(0, 0, width, height), width, height, QImage.Format_RGBA8888
    )


def refresh_projection():
    get_document().refreshProjection()


def image_to_layer(image, layer):
    """
    Place an image on the layer
    """
    try:
        ptr = image.bits()
        ptr.setsize(image.byteCount())

        layer.setPixelData(
            QByteArray(ptr.asstring()), 0, 0, image.width(), image.height(),
        )

    except Exception as e:
        ERROR("Unable to paste pixels", f"{e}")


def image_to_buffer(image):
    """
    Turns an image into a I/O Buffer so that it can be sent over HTTP.
    """

    # now make a buffer and save the image into it
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    image.save(buffer, format="PNG")

    # write the data into a buffer and jump to start of file
    image_byte_buffer = BytesIO()
    image_byte_buffer.write(buffer.data())
    image_byte_buffer.read()
    buffer.close()
    image_byte_buffer.seek(0)

    return image_byte_buffer


def buffer_to_image(buffer):
    return QImage.fromData(buffer.read())


def compile_endpoint(base_url, action):
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    if action == "img2img":
        return base_url + "/api/img2img"
    elif action == "txt2img":
        return base_url + "/api/img2img"
    elif action == "inpaint":
        return base_url + "/api/inpaint"

    return ERROR(
        "Bad Endpoint", "You have requesetd and endpoint that is not supported."
    )
