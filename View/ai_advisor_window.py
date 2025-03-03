# ai_advisor_window.py
import sys
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QLineEdit, QToolButton, QMenu, QSpacerItem)
from PySide6.QtGui import (QColor, QPixmap, QPainter, QPen, QFont, QPainterPath, QCursor, QBrush, QIcon)
from PySide6.QtCore import (Qt, QRect, QSize, QTimer, Signal, QPropertyAnimation, QEasingCurve)

# Import shared components
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget


class ChatBubbleAnimation(QPropertyAnimation):
    """Animation for chat bubbles when they appear"""
    def __init__(self, target, duration=150):
        super().__init__(target, b"maximumHeight")
        self.setDuration(duration)
        self.setStartValue(0)
        self.setEndValue(target.sizeHint().height())
        self.setEasingCurve(QEasingCurve.OutQuad)


class AIAdvisorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Financial Advisor - StockMaster Pro")
        self.setMinimumSize(950, 650)

        # Store chat message history
        self.chat_history = []

        # Create typing indicator
        self.typing_indicator = None
        self.ai_thinking_timer = QTimer(self)
        self.ai_thinking_timer.timeout.connect(self._add_ai_response)

        # Set dark theme with dashboard matching style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QScrollBar:vertical {{
                background: {ColorPalette.BG_DARK};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {ColorPalette.BORDER_LIGHT};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Chat container in card style matching dashboard
        self.chat_card = self._create_chat_card()
        main_layout.addWidget(self.chat_card)

    def _create_header(self):
        """Create a header matching dashboard style"""
        header = QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: transparent;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title and subtitle matching dashboard
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("AI Financial Advisor")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)

        subtitle = QLabel("Personalized financial insights and recommendations")
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        # Actions section
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        # Clear chat button
        clear_btn = QPushButton("Clear Chat")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        clear_btn.clicked.connect(self._clear_chat)

        # Back button styled like dashboard secondary button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        back_btn.clicked.connect(self.close)

        action_layout.addWidget(clear_btn)
        action_layout.addWidget(back_btn)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(action_layout)

        return header

    def _create_chat_card(self):
        """Create a chat card matching dashboard card style"""
        chat_card = QFrame()
        chat_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        chat_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add shadow effect matching dashboard cards
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        chat_card.setGraphicsEffect(shadow)

        # Chat layout
        chat_layout = QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Chat header matching dashboard card headers
        chat_header = QFrame()
        chat_header.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            border-bottom: 1px solid {ColorPalette.BORDER_DARK};
        """)
        chat_header.setFixedHeight(64)

        header_layout = QHBoxLayout(chat_header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # AI icon with accent color matching dashboard
        ai_icon = AvatarWidget("AI", size=36, background_color=ColorPalette.ACCENT_INFO)

        # Chat title
        chat_title = QLabel("Financial Assistant")
        chat_title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: bold;
        """)

        # Status with pulse animation
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)

        status_indicator = QFrame()
        status_indicator.setFixedSize(8, 8)
        status_indicator.setStyleSheet(f"""
            background-color: {ColorPalette.ACCENT_SUCCESS};
            border-radius: 4px;
        """)

        status_label = QLabel("Online")
        status_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")

        status_layout.addWidget(status_indicator)
        status_layout.addWidget(status_label)

        # Topic selector
        topic_btn = QToolButton()
        topic_btn.setText("Select Topic")
        topic_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QToolButton::menu-indicator {{ image: none; }}
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {ColorPalette.TEXT_PRIMARY};
            }}
        """)
        topic_btn.setCursor(Qt.PointingHandCursor)

        # Create topic menu
        topic_menu = QMenu(topic_btn)
        topic_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 6px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 15px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {ColorPalette.ACCENT_PRIMARY}30;
            }}
        """)

        # Add topics
        topics = [
            "Portfolio Analysis",
            "Investment Strategies",
            "Market Trends",
            "Risk Assessment",
            "Retirement Planning",
            "Tax Optimization"
        ]

        topic_btn.setMenu(topic_menu)
        topic_btn.setPopupMode(QToolButton.InstantPopup)

        header_layout.addWidget(ai_icon)
        header_layout.addWidget(chat_title)
        header_layout.addLayout(status_layout)
        header_layout.addStretch()
        header_layout.addWidget(topic_btn)

        # Messages area
        self.messages_area = QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_area.setFrameShape(QFrame.NoFrame)
        self.messages_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {ColorPalette.BG_CARD};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {ColorPalette.BG_CARD};
            }}
        """)

        # Message container
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(20, 20, 20, 20)
        self.message_layout.setSpacing(20)

        # Welcome message
        welcome_message = self._create_ai_message(
            "Hello! I'm your AI financial advisor. I can help you with investment strategies, portfolio analysis, market trends, and financial planning. How can I assist you today?"
        )
        self.message_layout.addWidget(welcome_message)
        self.chat_history.append(("ai", "Hello! I'm your AI financial advisor. I can help you with investment strategies, portfolio analysis, market trends, and financial planning. How can I assist you today?"))

        # Add spacer to push messages up
        self.message_layout.addStretch()

        self.messages_area.setWidget(self.message_container)

        # Chat input area matching dashboard style
        input_area = QFrame()
        input_area.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            border-top: 1px solid {ColorPalette.BORDER_DARK};
        """)
        input_area.setMinimumHeight(70)

        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(15)

        # Input field matching dashboard input style
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your financial question here...")
        self.input_field.setStyleSheet(GlobalStyle.INPUT_STYLE)
        self.input_field.setFixedHeight(40)
        self.input_field.returnPressed.connect(self._send_message)

        # Send button matching dashboard primary button style
        send_btn = QPushButton("Send")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        send_btn.setFixedSize(80, 40)
        send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)

        # Add all elements to chat layout
        chat_layout.addWidget(chat_header)
        chat_layout.addWidget(self.messages_area, 1)  # 1 = stretch factor
        chat_layout.addWidget(input_area)

        return chat_card

    def _create_ai_message(self, text):
        """Create an AI message bubble matching dashboard style"""
        message = QFrame()
        message.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 12px;
            border-top-left-radius: 4px;
        """)

        # Add subtle shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        message.setGraphicsEffect(shadow)

        message_layout = QVBoxLayout(message)
        message_layout.setContentsMargins(15, 15, 15, 15)
        message_layout.setSpacing(10)

        # Header with avatar and timestamp
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # AI avatar with accent color
        avatar = AvatarWidget("AI", size=32, background_color=ColorPalette.ACCENT_INFO)

        # AI name
        name_label = QLabel("Financial AI")
        name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 13px;")

        # Timestamp
        time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        time_label.setStyleSheet(f"color: {ColorPalette.TEXT_MUTED}; font-size: 11px;")

        header_layout.addWidget(avatar)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        # Message text
        text_label = QLabel(text)
        text_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 14px;
            line-height: 1.5;
        """)
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.MarkdownText)

        message_layout.addLayout(header_layout)
        message_layout.addWidget(text_label)

        return message

    def _create_user_message(self, text):
        """Create a more attractive user message bubble with solid styling"""
        message = QFrame()
        message.setStyleSheet(f"""
            background-color: transparent;
            border-radius: 12px;
            border: 0.5px solid {ColorPalette.BORDER_LIGHT};
        """)

        # Add subtle shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        message.setGraphicsEffect(shadow)

        message_layout = QVBoxLayout(message)
        message_layout.setContentsMargins(16, 16, 16, 16)
        message_layout.setSpacing(10)

        # Header with avatar and timestamp
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # User name
        name_label = QLabel("You")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; border: none;")

        # Timestamp
        time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        time_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 11px; border: none;")

        # User avatar - with solid dark blue border
        avatar = AvatarWidget("JD", size=32)
        avatar_layout = QHBoxLayout()
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setSpacing(0)
        avatar_layout.addWidget(avatar)

        # Add items to header
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        header_layout.addWidget(name_label)
        header_layout.addLayout(avatar_layout)

        # Message text
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            line-height: 1.5;
            border: none;
        """)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignRight)

        message_layout.addLayout(header_layout)
        message_layout.addWidget(text_label)

        return message

    def _create_typing_indicator(self):
        """Create a typing indicator that shows AI is thinking"""
        message = QFrame()
        message.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 12px;
            border-top-left-radius: 4px;
            margin-right: 200px;
        """)

        message_layout = QHBoxLayout(message)
        message_layout.setContentsMargins(15, 10, 15, 10)
        message_layout.setSpacing(10)

        # AI avatar with accent color
        avatar = AvatarWidget("AI", size=24, background_color=ColorPalette.ACCENT_INFO)

        # Typing dots container
        typing_label = QLabel("Thinking")
        typing_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 13px;")

        message_layout.addWidget(avatar)
        message_layout.addWidget(typing_label)
        message_layout.addStretch()

        return message

    def _send_message(self):
        """Send a message and get AI response"""
        message_text = self.input_field.text().strip()
        if not message_text:
            return

        # Add user message to chat
        user_message = self._create_user_message(message_text)

        # Remove stretch spacer if it exists
        if self.message_layout.count() > 0 and isinstance(self.message_layout.itemAt(self.message_layout.count()-1), QSpacerItem):
            spacer = self.message_layout.itemAt(self.message_layout.count()-1)
            self.message_layout.removeItem(spacer)

        self.message_layout.addWidget(user_message)
        self.chat_history.append(("user", message_text))

        # Clear input field
        self.input_field.clear()

        # Add typing indicator
        self.typing_indicator = self._create_typing_indicator()
        self.message_layout.addWidget(self.typing_indicator)

        # Scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

        # Simulate AI thinking and responding
        self.ai_thinking_timer.start(2000)

    def _add_ai_response(self):
        """Add AI response after thinking animation"""
        # Stop the thinking timer
        self.ai_thinking_timer.stop()

        # Remove typing indicator
        if self.typing_indicator:
            self.typing_indicator.setVisible(False)
            self.message_layout.removeWidget(self.typing_indicator)
            self.typing_indicator.deleteLater()
            self.typing_indicator = None

        # Generate response based on latest user message
        last_message = self.chat_history[-1][1] if self.chat_history else ""
        response = self._generate_ai_response(last_message)

        # Add AI response
        ai_message = self._create_ai_message(response)
        self.message_layout.addWidget(ai_message)
        self.chat_history.append(("ai", response))

        # Add stretch spacer back
        self.message_layout.addStretch()

        # Scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

        # Animate the new message
        animation = ChatBubbleAnimation(ai_message)
        animation.start()

    def _generate_ai_response(self, user_message):
        """Generate an appropriate AI response based on the user message"""
        user_message = user_message.lower()

        if "portfolio" in user_message or "stocks" in user_message:
            return "Based on your current portfolio, I notice you're heavily weighted in technology stocks. To improve diversification, consider adding some defensive sectors like healthcare or consumer staples. Companies like Johnson & Johnson (JNJ) or Procter & Gamble (PG) could help balance your portfolio risk profile."

        elif "market" in user_message or "trend" in user_message:
            return "Recent market trends show increasing volatility due to inflation concerns and potential interest rate adjustments. The technology sector has experienced some correction, while energy stocks have been performing well. For long-term investors, this could present buying opportunities in quality companies that have solid fundamentals but have seen price drops."

        elif "invest" in user_message or "strategy" in user_message:
            return "For your investment strategy, I recommend a core-satellite approach:\n\n1. **Core holdings** (70-80%) - Low-cost index ETFs like VTI, VXUS, and BND\n\n2. **Satellite positions** (20-30%) - Individual stocks or sector ETFs in areas you believe will outperform\n\nThis balances steady growth with opportunities for higher returns while managing overall portfolio risk."

        elif "risk" in user_message:
            return "Your current risk exposure appears moderate to high based on your allocation. Some ways to reduce risk include:\n\n• Increasing your bond allocation (currently only 15% of your portfolio)\n• Adding uncorrelated assets like REITs or commodities\n• Using stop-loss orders on your more volatile holdings\n\nWhat's your risk tolerance on a scale of 1-10?"

        elif "retire" in user_message or "retirement" in user_message:
            return "For retirement planning, you should aim to save at least 15-20% of your income. Based on your current savings rate and portfolio value, you appear to be on track for your stated retirement age of 62. However, I recommend increasing your contributions to tax-advantaged accounts like your 401(k) and Roth IRA before investing in your taxable brokerage account."

        else:
            return "Thank you for your question. As an AI financial advisor, I can provide insights on portfolio management, investment strategies, market trends, risk assessment, and retirement planning. Could you share more specifics about your financial situation and goals so I can give you more tailored advice?"

    def _select_topic(self, topic):
        """Handle topic selection from dropdown menu"""
        prompt = ""

        if topic == "Portfolio Analysis":
            prompt = "Can you analyze my current portfolio and suggest improvements?"
        elif topic == "Investment Strategies":
            prompt = "What investment strategies would you recommend for the current market?"
        elif topic == "Market Trends":
            prompt = "What are the most important market trends I should be aware of right now?"
        elif topic == "Risk Assessment":
            prompt = "How can I better manage risk in my investment portfolio?"
        elif topic == "Retirement Planning":
            prompt = "What should I focus on for effective retirement planning?"
        elif topic == "Tax Optimization":
            prompt = "How can I optimize my investments for tax efficiency?"

        # Set the prompt in the input field
        if prompt:
            self.input_field.setText(prompt)
            self.input_field.setFocus()

    def _clear_chat(self):
        """Clear the chat history"""
        # Remove all message widgets except the first welcome message
        while self.message_layout.count() > 2:  # 1 for welcome message + 1 for stretch
            item = self.message_layout.itemAt(1)  # Skip the first item (welcome message)
            if item.widget():
                widget = item.widget()
                self.message_layout.removeWidget(widget)
                widget.deleteLater()

        # Reset chat history to just the welcome message
        self.chat_history = [self.chat_history[0]] if self.chat_history else []

        # Clear the input field
        self.input_field.clear()

    def _scroll_to_bottom(self):
        """Scroll the message area to the bottom"""
        self.messages_area.verticalScrollBar().setValue(
            self.messages_area.verticalScrollBar().maximum()
        )


# For testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIAdvisorWindow()
    window.show()
    sys.exit(app.exec())