from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
)

class VentanaModificar(QDialog):

    def __init__(self, fila, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Modificar registro"
        )

        self.resize(400, 180)

        self.fila = fila.copy()

        layout = QVBoxLayout()

        # ==========================================
        # COMBO COLUMNAS
        # ==========================================

        self.combo = QComboBox()

        self.combo.addItems(
            self.fila.index.tolist()
        )

        layout.addWidget(
            QLabel("Campo:")
        )

        layout.addWidget(
            self.combo
        )

        # ==========================================
        # VALOR
        # ==========================================

        self.input_valor = QLineEdit()

        layout.addWidget(
            QLabel("Nuevo valor:")
        )

        layout.addWidget(
            self.input_valor
        )

        # ==========================================
        # BOTON GUARDAR
        # ==========================================

        self.btn_guardar = QPushButton(
            "Guardar"
        )

        self.btn_guardar.clicked.connect(
            self.guardar
        )

        layout.addWidget(
            self.btn_guardar
        )

        self.setLayout(layout)

        # ==========================================
        # CAMBIAR VALOR AUTOMATICAMENTE
        # ==========================================

        self.combo.currentTextChanged.connect(
            self.cargar_valor
        )

        self.cargar_valor()

    # ==========================================
    # CARGAR VALOR ACTUAL
    # ==========================================

    def cargar_valor(self):

        columna = self.combo.currentText()

        valor = str(
            self.fila[columna]
        )

        self.input_valor.setText(
            valor
        )

    # ==========================================
    # GUARDAR
    # ==========================================

    def guardar(self):

        self.columna = (
            self.combo.currentText()
        )

        self.valor = (
            self.input_valor.text()
        )

        self.accept()