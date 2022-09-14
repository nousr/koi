from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage
from krita import DockWidget, Krita
from urllib import request
from io import BytesIO
from zipfile import ZipFile
import re
import random

class Koi(DockWidget):
    def __init__(self):
        """
        This sets up a basic user interface to interact with.

        TODO/FIXME: Adopt a better approach for managing the UI.
        """
        super().__init__()
        self.ITER = 0

        self.setWindowTitle("Koi")

        # Initializing random seed ===
        random.seed(None) 

        # Main WIdget ===
        self.mainWidget = QWidget(self)
        self.mainWidget.setLayout(QVBoxLayout())
        self.setWidget(self.mainWidget)

        # Input & Prompt Settings ===
        self.input_widget = QWidget(self.mainWidget)

        self.input_layout = QFormLayout()

        self.prompt = QPlainTextEdit(self.input_widget)
        self.prompt.setPlaceholderText("Describe your end goal...")
        self.prompt.setPlainText(
            "A beautiful mountain landscape in the style of greg rutkowski, oils on canvas."
        )

        self.steps = QSpinBox(self.input_widget)
        self.steps.setRange(5, 300)
        self.steps.setValue(32)

        self.variations = QSpinBox(self.input_widget)
        self.variations.setRange(1, 8)
        self.variations.setValue(1)

        self.base_seed_min = 0
        self.base_seed_max = 100000000
        self.base_seed = QSpinBox(self.input_widget)
        self.base_seed.setRange(self.base_seed_min-1, self.base_seed_max) #let -1 choosable
        self.base_seed.setValue(1337)
        self.base_seed.setToolTip('If set to -1, then the seed will be randomized in the background.')

        self.sketch_strengh = QDoubleSpinBox(self.input_widget)
        self.sketch_strengh.setRange(0.05, 0.95)
        self.sketch_strengh.setSingleStep(0.05)
        self.sketch_strengh.setValue(0.25)

        self.prompt_strength = QDoubleSpinBox(self.input_widget)
        self.prompt_strength.setRange(1.0, 20.00)
        self.prompt_strength.setValue(7.5)

        self.input_layout.addRow("Prompt", self.prompt)
        self.input_layout.addRow("Variations", self.variations)
        self.input_layout.addRow("Steps", self.steps)
        self.input_layout.addRow("Base Seed", self.base_seed)
        self.input_layout.addRow("Sketch strength", self.sketch_strengh)
        self.input_layout.addRow("Prompt strength", self.prompt_strength)

        self.input_widget.setLayout(self.input_layout)

        self.mainWidget.layout().addWidget(self.input_widget)

        # Auto random seed checkbox ===
        self.auto_random = QCheckBox(self.mainWidget)
        self.auto_random.setText("Auto randomize seed after Dream")

        self.mainWidget.layout().addWidget(self.auto_random)

        # Endpoint Settings ===
        self.endpoint_widget = QWidget(self.mainWidget)
        self.endpoint_layout = QFormLayout()

        self.endpoint = QLineEdit(self.endpoint_widget)
        self.endpoint.setPlaceholderText("GPU Endpoint")
        self.endpoint.setText("http://127.0.0.1:8888/api/img2img")

        self.endpoint_layout.addRow("Endpoint", self.endpoint)
        self.endpoint_widget.setLayout(self.endpoint_layout)
        self.mainWidget.layout().addWidget(self.endpoint_widget)

        # Dream button ===
        self.dream = QPushButton(self.mainWidget)
        self.dream.setText("Dream")
        self.dream.clicked.connect(self.pingServer)

        self.mainWidget.layout().addWidget(self.dream)

    def canvasChanged(self, canvas):
        """
        This function must exists per Krita documentation.
        """
        pass

    def _prompt_text(self):
        return self.prompt.toPlainText().replace("\n", " ")

    def _get_extra_args(self):
        """
        Take all input from user and construct a mapping object.

        Return: Encoded bytes to send as data in post request.
        """

        headers = {
            "variations": str(self.variations.value()),
            "prompt": self._prompt_text(),
            "steps": str(self.steps.value()),
            "seed": str(self.getRandSeed() if self.base_seed.value()==-1 else self.base_seed.value()),
            "sketch_strength": str(self.sketch_strengh.value()),
            "prompt_strength": str(self.prompt_strength.value()),
        }

        return headers

    def _get_endpoint(self):
        return str(self.endpoint.text())

    def _next_layer_id(self):
        self.ITER += 1
        return self.ITER

    def _safe_layer_name(self, name):
        return re.sub('[^A-Za-z0-9-_]+', '', name.replace(' ', '_'))

    def _add_paint_layer(self, doc, root, returned_file, name):
        dream_layer = doc.createNode(f'{self._safe_layer_name(name)}-{self._next_layer_id()}', "paintLayer")
        root.addChildNode(dream_layer, None)

        # get a pointer to the image's bits and add them to the new layer
        ptr = returned_file.bits()
        ptr.setsize(returned_file.byteCount())
        dream_layer.setPixelData(
            QByteArray(ptr.asstring()),
            0,
            0,
            returned_file.width(),
            returned_file.height(),
        )

    def _get_timeout(self):
        return int(1.5 * self.steps.value()) * self.variations.value()

    def getRandSeed(self):
        return random.randint(self.base_seed_min,self.base_seed_max-self.variations.value())

    def pingServer(self):
        # get the current layer as a I/O buffer
        image_buffer = self.layer2buffer()

        headers = self._get_extra_args()
        headers.update({"Content-Type": "application/octet-stream"})

        response_url = request.Request(url=self._get_endpoint(), data=image_buffer, headers=headers)

        application = Krita.instance()
        doc = application.activeDocument()
        root = doc.rootNode()

        # wait for response and read image
        with request.urlopen(response_url, timeout=self._get_timeout()) as response:
            archive = ZipFile(BytesIO(response.read()))
            filenames = archive.namelist()
            for name in filenames:
                file = archive.read(name)
            
                returned_file = QImage.fromData(file)
                self._add_paint_layer(doc, root, returned_file, name)                

        # check for auto random needed
        if self.auto_random.isChecked():
            self.base_seed.setValue(self.getRandSeed())

        # update user
        doc.refreshProjection()

    def layer2buffer(self):
        """
        Turns the current active layer into a I/O Buffer so that it can be sent over HTTP.
        """
        # get current document
        currentDocument = Krita.instance().activeDocument()
        width, height = (currentDocument.width(), currentDocument.height())

        # get current layer
        currentLayer = currentDocument.activeNode()

        # get the pixel data
        pixelData = currentLayer.pixelData(0, 0, width, height)

        # construct QImage
        qImage = QImage(pixelData, width, height, QImage.Format_RGBA8888)
        qImage = qImage.rgbSwapped()

        # now make a buffer and save the image into it
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        qImage.save(buffer, format="PNG")

        # write the data into a buffer and jump to start of file
        image_byte_buffer = BytesIO()
        image_byte_buffer.write(buffer.data())
        image_byte_buffer.read()
        buffer.close()
        image_byte_buffer.seek(0)

        return image_byte_buffer