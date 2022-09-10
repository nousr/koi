from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from krita import DockWidget, Krita
from urllib import request
from koi.helpers import (
    make_selection,
    NOT_IMPLEMENTED,
    selection_to_image,
    image_to_buffer,
    get_selection,
    image_to_layer,
    get_layer,
    buffer_to_image,
    exists,
    compile_endpoint,
    ERROR,
)

TIMEOUT = 60  # maximum seconds to wait for response from server


class Koi(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOI")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)

        mainLayout = QGridLayout()

        # === Prompt Area
        PromptGroup = QGroupBox("Prompt", mainWidget)
        promptLayout = QGridLayout()

        self.promptText = QPlainTextEdit(PromptGroup)
        self.promptText.setPlainText(
            "A beautiful painting of a distant galaxy, by Caspar David Friedrich, matte painting trending on artstation HQ"
        )
        promptLayout.addWidget(self.promptText, 1, 0)

        PromptGroup.setLayout(promptLayout)
        # === End Prompt Area

        # === Settings Area
        SettingGroup = QGroupBox("Settings", mainWidget)
        settingLayout = QGridLayout()

        # sampler label
        samplerBoxLabel = QLabel("Sampler", SettingGroup)
        settingLayout.addWidget(samplerBoxLabel, 0, 0)

        # sampler box
        self.samplerBox = QComboBox(SettingGroup)
        self.samplerBox.addItem("euler_ancestral")
        self.samplerBox.addItem("euler")
        self.samplerBox.addItem("heun")
        self.samplerBox.addItem("dpm_2_ancestral")
        self.samplerBox.addItem("dpm_2")
        self.samplerBox.addItem("lms")
        settingLayout.addWidget(self.samplerBox, 0, 1)

        # steps
        stepBoxLabel = QLabel("Steps", SettingGroup)
        settingLayout.addWidget(stepBoxLabel, 1, 0)

        # step spin box
        self.stepBox = QSpinBox()
        self.stepBox.setMinimum(5)
        self.stepBox.setMaximum(150)
        self.stepBox.setValue(32)
        settingLayout.addWidget(self.stepBox, 1, 1)

        # seed box label
        seedBoxLabel = QLabel("Seed", SettingGroup)
        settingLayout.addWidget(seedBoxLabel, 2, 0)

        # seed spin box
        self.seedBox = QSpinBox()
        self.seedBox.setMinimum(-1)
        self.seedBox.setMaximum(1000000000)
        self.seedBox.setValue(-1)
        settingLayout.addWidget(self.seedBox, 2, 1)

        # strength box label
        strengthBoxLabel = QLabel("Strength", SettingGroup)
        settingLayout.addWidget(strengthBoxLabel, 3, 0)

        # strength spin box
        self.strengthBox = QDoubleSpinBox()
        self.strengthBox.setMinimum(0.00)
        self.strengthBox.setMaximum(1.00)
        self.strengthBox.setSingleStep(0.05)
        self.strengthBox.setValue(0.5)
        settingLayout.addWidget(self.strengthBox, 3, 1)

        # cond scale box label
        condScaleBoxLabel = QLabel("Cond-Scale", SettingGroup)
        settingLayout.addWidget(condScaleBoxLabel, 4, 0)

        # cond scale spin box
        self.condScaleBox = QDoubleSpinBox()
        self.condScaleBox.setMinimum(0.00)
        self.condScaleBox.setSingleStep(0.05)
        self.condScaleBox.setMaximum(25.00)
        self.condScaleBox.setValue(7.5)

        settingLayout.addWidget(self.condScaleBox, 4, 1)

        # variations box label
        variationsBoxLabel = QLabel("Variations", SettingGroup)
        settingLayout.addWidget(variationsBoxLabel, 5, 0)

        # variations spin box
        self.variationsBox = QSpinBox()
        self.variationsBox.setMinimum(1)
        self.variationsBox.setMaximum(4)
        self.variationsBox.setValue(1)

        settingLayout.addWidget(self.variationsBox, 5, 1)
        SettingGroup.setLayout(settingLayout)

        # base url label
        url_label = QLabel("URL", SettingGroup)
        settingLayout.addWidget(url_label, 6, 0)

        # base url
        self.url = QLineEdit(SettingGroup)
        self.url.setText("http://127.0.0.1:8888")
        settingLayout.addWidget(self.url, 6, 1)

        # === End Settings Area

        # === Tool Area
        ToolGroup = QGroupBox(mainWidget)
        ToolGroup.setTitle("Tools")
        toolLayout = QGridLayout()

        selectionButton = QPushButton("New Selection", ToolGroup)
        selectionButton.setIcon(Krita.instance().icon("tool_rect_selection"))
        selectionButton.setContentsMargins(20, 0, 0, 0)
        selectionButton.clicked.connect(make_selection)
        toolLayout.addWidget(selectionButton, 0, 0)

        ToolGroup.setLayout(toolLayout)
        # === End Tool Area

        # === Dream Area
        DreamGroup = QGroupBox(mainWidget)
        DreamGroup.setTitle("Dream")
        toolLayout = QGridLayout()

        # txt2img Button
        txt2img = QPushButton("txt2img", DreamGroup)
        txt2img.setContentsMargins(10, 0, 0, 0)
        txt2img.clicked.connect(NOT_IMPLEMENTED)
        toolLayout.addWidget(txt2img, 1, 0)

        # img2img Button
        img2img = QPushButton("img2img", DreamGroup)
        img2img.setContentsMargins(10, 0, 0, 0)
        img2img.clicked.connect(self.img2img)
        toolLayout.addWidget(img2img, 1, 1)

        # inpaint Button
        inpaint = QPushButton("inpaint", DreamGroup)
        inpaint.setContentsMargins(10, 0, 0, 0)
        inpaint.clicked.connect(NOT_IMPLEMENTED)
        toolLayout.addWidget(inpaint, 1, 2)

        DreamGroup.setLayout(toolLayout)
        # === End Dream Area

        mainLayout.addWidget(PromptGroup, 0, 0)
        mainLayout.addWidget(SettingGroup, 1, 0)
        mainLayout.addWidget(ToolGroup, 2, 0)
        mainLayout.addWidget(DreamGroup, 3, 0)
        mainWidget.setLayout(mainLayout)
        # === End Main Widget

    def canvasChanged(self, canvas):
        """
        This function must exists per Krita documentation.
        """
        pass

    def get_headers(self, image=None):
        """
        Take all input from user and construct HTTP Headers.
        """

        headers = {
            "Content-Type": "application/octet-stream",
            "Prompt": str(self.promptText.toPlainText()),
            "Sample-Steps": str(self.stepBox.value()),
            "Random-Seed": str(self.seedBox.value()),
            "Image-Strength": str(1.0 - self.strengthBox.value()),
            "Cond-Scale": str(self.condScaleBox.value()),
            "Batch-Size": str(self.variationsBox.value()),
            "Sampler": str(self.samplerBox.currentText()),
            "Height": 0,
            "Width": 0,
        }

        if exists(image):
            headers.update({"Width": image.width(), "Height": image.height()})

        return headers

    def img2img(self):
        # get the current selection
        selection = get_selection()

        if not exists(selection):
            return

        # get image from current selection
        image = selection_to_image(selection=selection)

        # turn that image into a buffer
        buffer = image_to_buffer(image)

        # build headers
        headers = self.get_headers(image)

        # get the correct endpoint
        endpoint = compile_endpoint(self.url.text(), action="img2img")

        # make a request to the backend server
        response_url = request.Request(url=endpoint, data=buffer, headers=headers)

        # open the connection
        with request.urlopen(response_url, timeout=TIMEOUT) as response:
            if response.status == 200:
                # TODO: re-implement multiple dream return
                image = buffer_to_image(response)
                image_to_layer(image, get_layer(), x=selection.x(), y=selection.y())

            else:
                ERROR(
                    f"Server Error: {response.status}",
                    "Something went wrong on the server side, check server's output.",
                )
