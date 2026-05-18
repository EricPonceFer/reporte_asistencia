from vista.interfaz_reporte import Ui_MainWindow

from PyQt6.QtWidgets import QMainWindow

from controlador.asistencia_controlador import (
    Controlador_Reporte_Asitencia
)

class MainController(QMainWindow):

    def __init__(self):
        super().__init__()

        # ==========================================
        # UI
        # ==========================================

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.asistencia_controller = (
            Controlador_Reporte_Asitencia(self, self.ui)
        )
        # ==========================================
        # LISTA BOTONES MENU
        # ==========================================

        self.botones_menu = [

            self.ui.btn_pltReporte,
            self.ui.btn_pltOperador,
            self.ui.btn_pltVelada

        ]

        # ==========================================
        # CONFIGURAR MENU
        # ==========================================

        self.configurar_navegacion()

        # ==========================================
        # PAGINA INICIAL
        # ==========================================

        self.cambiar_pagina(
            self.ui.Reporte_Asistencia,
            self.ui.btn_pltReporte
        )

    # =====================================================
    # NAVEGACION
    # =====================================================

    def configurar_navegacion(self):

        # ==========================================
        # REPORTE
        # ==========================================

        self.ui.btn_pltReporte.clicked.connect(

            lambda: self.cambiar_pagina(
                self.ui.Reporte_Asistencia,
                self.ui.btn_pltReporte
            )

        )

        # ==========================================
        # OPERADORES
        # ==========================================

        self.ui.btn_pltOperador.clicked.connect(

            lambda: self.cambiar_pagina(
                self.ui.Codigo_Operadores,
                self.ui.btn_pltOperador
            )

        )

        # ==========================================
        # VELADA
        # ==========================================

        self.ui.btn_pltVelada.clicked.connect(

            lambda: self.cambiar_pagina(
                self.ui.Personal_Velada,
                self.ui.btn_pltVelada
            )

        )

    # =====================================================
    # CAMBIAR PAGINA
    # =====================================================

    def cambiar_pagina(self, pagina, boton_activo):

        # CAMBIAR FRAME
        self.ui.Contenido.setCurrentWidget(
            pagina
        )

        # ACTUALIZAR COLORES
        self.actualizar_estilos_menu(
            boton_activo
        )

    # =====================================================
    # ESTILOS MENU
    # =====================================================

    def actualizar_estilos_menu(self, boton_activo):

        # RESET BOTONES
        for boton in self.botones_menu:

            boton.setStyleSheet("""

                QPushButton {

                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-weight: 600;

                }

                QPushButton:hover {

                    background-color: rgba(255, 255, 255, 60);

                }

            """)

        # BOTON ACTIVO
        boton_activo.setStyleSheet("""

            QPushButton {

                background-color: rgba(255, 255, 255, 120);
                color: white;
                border: none;
                padding: 10px;
                font-weight: 600;

            }

        """)