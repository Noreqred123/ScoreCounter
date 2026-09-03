import sys
import json
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsDropShadowEffect,
)


# ============================================================
# СОХРАНЕНИЕ СЧЁТА
# ============================================================

APP_DIR = Path.home() / "ScoreCounter"
DATA_FILE = APP_DIR / "score.json"

APP_DIR.mkdir(exist_ok=True)


def load_scores():
    if DATA_FILE.exists():
        try:
            data = json.loads(
                DATA_FILE.read_text(encoding="utf-8")
            )

            return (
                int(data.get("green", 0)),
                int(data.get("red", 0))
            )

        except Exception:
            pass

    return 0, 0


def save_scores(green, red):
    DATA_FILE.write_text(
        json.dumps(
            {
                "green": green,
                "red": red
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ============================================================
# ПРОЗРАЧНАЯ СКРУГЛЁННАЯ ПАНЕЛЬ
# ============================================================

class GlassPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setStyleSheet(
            "background: transparent;"
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = self.rect().adjusted(
            1,
            1,
            -1,
            -1
        )

        path = QPainterPath()

        path.addRoundedRect(
            rect,
            15,
            15
        )

        # ----------------------------------------------------
        # Основной фон
        # ----------------------------------------------------

        painter.fillPath(
            path,
            QColor(
                7,
                15,
                27,
                238
            )
        )

        # ----------------------------------------------------
        # Тонкая рамка
        # ----------------------------------------------------

        painter.setPen(
            QColor(
                255,
                255,
                255,
                38
            )
        )

        painter.drawPath(path)


# ============================================================
# ГЛАВНОЕ ОКНО
# ============================================================

class ScoreCounter(QWidget):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # Состояние
        # ----------------------------------------------------

        self.green_score, self.red_score = load_scores()

        self.green_glow = None
        self.red_glow = None

        self.green_animation = None
        self.red_animation = None

        self.drag_position = None

        # ----------------------------------------------------
        # Окно
        # ----------------------------------------------------

        self.setWindowTitle(
            "Score Counter"
        )

        # МИНИМАЛЬНЫЙ РАЗМЕР
        self.setFixedSize(
            200,
            110
        )

        self.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.Window |
    Qt.WindowType.WindowStaysOnTopHint
)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setStyleSheet(
            "background: transparent;"
        )

        # ----------------------------------------------------
        # Интерфейс
        # ----------------------------------------------------

        self.build_ui()

        self.update_scores()


    # ========================================================
    # СОЗДАНИЕ ИНТЕРФЕЙСА
    # ========================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(
            4,
            4,
            4,
            4
        )

        root.setSpacing(0)

        # ----------------------------------------------------
        # Панель
        # ----------------------------------------------------

        self.panel = GlassPanel()

        root.addWidget(
            self.panel
        )

        layout = QVBoxLayout(
            self.panel
        )

        layout.setContentsMargins(
            5,
            3,
            5,
            3
        )

        layout.setSpacing(0)

        # ====================================================
        # СЧЁТЧИКИ
        # ====================================================

        scores = QHBoxLayout()

        scores.setSpacing(
            2
        )

        scores.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ----------------------------------------------------
        # ЗЕЛЁНАЯ ЦИФРА
        # ----------------------------------------------------

        self.green_label = QLabel(
            "0"
        )

        self.green_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.green_label.setMinimumWidth(
            65
        )

        self.green_label.setFont(
            QFont(
                "Montserrat",
                24,
                QFont.Weight.ExtraBold
            )
        )

        self.green_label.setStyleSheet("""
            QLabel {
                color: #35ff78;
                background: transparent;
            }
        """)

        self.green_glow = self.add_glow(
            self.green_label,
            "#20ff68",
            24,
            55
        )

        # ----------------------------------------------------
        # РАЗДЕЛИТЕЛЬ
        # ----------------------------------------------------

        divider = QLabel()

        divider.setFixedSize(
            1,
            30
        )

        divider.setStyleSheet("""
            background-color:
                rgba(255, 255, 255, 100);

            border-radius: 1px;
        """)

        # ----------------------------------------------------
        # КРАСНАЯ ЦИФРА
        # ----------------------------------------------------

        self.red_label = QLabel(
            "0"
        )

        self.red_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.red_label.setMinimumWidth(
            65
        )

        self.red_label.setFont(
            QFont(
                "Montserrat",
                24,
                QFont.Weight.ExtraBold
            )
        )

        self.red_label.setStyleSheet("""
            QLabel {
                color: #ff405c;
                background: transparent;
            }
        """)

        self.red_glow = self.add_glow(
            self.red_label,
            "#ff1744",
            24,
            55
        )

        # ----------------------------------------------------
        # Раскладка цифр
        # ----------------------------------------------------

        scores.addWidget(
            self.green_label,
            1
        )

        scores.addWidget(
            divider
        )

        scores.addWidget(
            self.red_label,
            1
        )

        layout.addLayout(
            scores
        )

        # ====================================================
        # КНОПКИ
        # ====================================================

        layout.addSpacing(
            2
        )

        buttons = QHBoxLayout()

        buttons.setSpacing(
            3
        )

        buttons.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ----------------------------------------------------
        # PLUS
        # ----------------------------------------------------

        self.plus_button = self.create_button(
            "+",
            "#28d968",
            "#159447"
        )

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        self.reset_button = self.create_button(
            "↻",
            "#5790b5",
            "#315d7a"
        )

        # ----------------------------------------------------
        # MINUS
        # ----------------------------------------------------

        self.minus_button = self.create_button(
            "−",
            "#ff405c",
            "#bd293f"
        )

        # ----------------------------------------------------
        # Подключение
        # ----------------------------------------------------

        self.plus_button.clicked.connect(
            self.add_green
        )

        self.reset_button.clicked.connect(
            self.reset_scores
        )

        self.minus_button.clicked.connect(
            self.add_red
        )

        # ----------------------------------------------------
        # Добавляем кнопки
        # ----------------------------------------------------

        buttons.addWidget(
            self.plus_button,
            1
        )

        buttons.addWidget(
            self.reset_button,
            1
        )

        buttons.addWidget(
            self.minus_button,
            1
        )

        layout.addLayout(
            buttons
        )


    # ========================================================
    # СОЗДАНИЕ КНОПКИ
    # ========================================================

    def create_button(
        self,
        text,
        hover_color,
        normal_color
    ):

        button = QPushButton(
            text
        )

        button.setFixedSize(
            QSize(
                40,
                25
            )
        )

        button.setFont(
            QFont(
                "Montserrat",
                14,
                QFont.Weight.Bold
            )
        )

        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        button.setStyleSheet(
            f"""
            QPushButton {{
                color: white;

                border: 1px solid
                    rgba(255,255,255,35);

                border-radius: 8px;

                background-color:
                    {normal_color};

                padding: 0px;
            }}

            QPushButton:hover {{
                background-color:
                    {hover_color};
            }}

            QPushButton:pressed {{
                background-color:
                    {normal_color};

                padding-top: 2px;
            }}
            """
        )

        # ----------------------------------------------------
        # Свечение кнопки
        # ----------------------------------------------------

        glow = QGraphicsDropShadowEffect()

        glow.setBlurRadius(
            12
        )

        glow.setOffset(
            0,
            0
        )

        glow_color = QColor(
            hover_color
        )

        glow_color.setAlpha(
            70
        )

        glow.setColor(
            glow_color
        )

        button.setGraphicsEffect(
            glow
        )

        return button


    # ========================================================
    # СВЕЧЕНИЕ ЦИФР
    # ========================================================

    def add_glow(
        self,
        widget,
        color,
        blur=24,
        opacity=55
    ):

        glow = QGraphicsDropShadowEffect()

        glow.setBlurRadius(
            blur
        )

        glow.setOffset(
            0,
            0
        )

        c = QColor(
            color
        )

        c.setAlpha(
            opacity
        )

        glow.setColor(
            c
        )

        widget.setGraphicsEffect(
            glow
        )

        return glow


    # ========================================================
    # ИМПУЛЬС СВЕЧЕНИЯ
    # ========================================================

    def pulse_glow(
        self,
        glow,
        color
    ):

        glow.setBlurRadius(
            50
        )

        bright = QColor(
            color
        )

        bright.setAlpha(
            255
        )

        glow.setColor(
            bright
        )

        animation = QPropertyAnimation(
            glow,
            b"blurRadius"
        )

        animation.setDuration(
            650
        )

        animation.setStartValue(
            50
        )

        animation.setEndValue(
            15
        )

        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        animation.start()

        return animation


    # ========================================================
    # ОБНОВЛЕНИЕ СЧЁТА
    # ========================================================

    def update_scores(self):

        self.green_label.setText(
            str(
                self.green_score
            )
        )

        self.red_label.setText(
            str(
                self.red_score
            )
        )

        save_scores(
            self.green_score,
            self.red_score
        )


    # ========================================================
    # ДОБАВИТЬ ЗЕЛЁНОЕ ОЧКО
    # ========================================================

    def add_green(self):

        self.green_score += 1

        self.update_scores()

        self.green_animation = self.pulse_glow(
            self.green_glow,
            "#20ff68"
        )


    # ========================================================
    # ДОБАВИТЬ КРАСНОЕ ОЧКО
    # ========================================================

    def add_red(self):

        self.red_score += 1

        self.update_scores()

        self.red_animation = self.pulse_glow(
            self.red_glow,
            "#ff1744"
        )


    # ========================================================
    # СБРОС
    # ========================================================

    def reset_scores(self):

        self.green_score = 0
        self.red_score = 0

        self.update_scores()

        self.green_animation = self.pulse_glow(
            self.green_glow,
            "#20ff68"
        )

        self.red_animation = self.pulse_glow(
            self.red_glow,
            "#ff1744"
        )


    # ========================================================
    # ПЕРЕТАСКИВАНИЕ ОКНА
    # ========================================================

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.MouseButton.LeftButton:

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()


    def mouseMoveEvent(
        self,
        event
    ):

        if (
            event.buttons()
            & Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()


    def mouseReleaseEvent(
        self,
        event
    ):

        self.drag_position = None


    # ========================================================
    # ГОРЯЧИЕ КЛАВИШИ
    # ========================================================

    def keyPressEvent(
        self,
        event
    ):

        key = event.key()

        if key in (
            Qt.Key.Key_Plus,
            Qt.Key.Key_Equal
        ):

            self.add_green()

        elif key == Qt.Key.Key_Minus:

            self.add_red()

        elif key == Qt.Key.Key_R:

            self.reset_scores()

        elif key == Qt.Key.Key_Escape:

            self.close()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    app.setStyle(
        "Fusion"
    )

    window = ScoreCounter()

    window.show()

    sys.exit(
        app.exec()
    )
